"""Application orchestrator."""

import asyncio
import logging

from .config import Config
from .ha_client.client import HAClient
from .i18n import I18n
from .protocol.videotex import VideotexProtocol
from .session import SessionManager
from .transport.websocket_server import WebSocketServer
from .transport.serial_transport import SerialMinitelTransport

logger = logging.getLogger(__name__)


class Application:
    """Main application: starts transports, HA client, and session manager."""

    def __init__(self, config: Config):
        self.config = config
        self.i18n = I18n(config.language)
        self.protocol = VideotexProtocol()
        self.ha_client = HAClient(config.ha_url, config.ha_token)
        self.session_manager = SessionManager(
            ha_client=self.ha_client,
            protocol=self.protocol,
            i18n=self.i18n,
        )

    async def run(self):
        logger.info("Starting ha-minitel")

        await self.ha_client.connect()

        tasks = []

        ws_server = WebSocketServer(
            port=self.config.websocket_port,
            on_connect=self.session_manager.on_transport_connected,
            on_disconnect=self.session_manager.on_transport_disconnected,
        )
        tasks.append(asyncio.create_task(ws_server.serve()))
        logger.info("WebSocket server starting on port %d", self.config.websocket_port)

        if self.config.serial_device:
            serial_transport = SerialMinitelTransport(
                device=self.config.serial_device,
                baud_rate=self.config.serial_baud_rate,
                parity=self.config.serial_parity,
            )
            tasks.append(asyncio.create_task(
                self._run_serial(serial_transport)
            ))
            logger.info("Serial transport on %s", self.config.serial_device)

        tasks.append(asyncio.create_task(self.ha_client.recv_loop(
            self.session_manager.on_state_changed
        )))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            logger.info("Shutting down")
        finally:
            await self.ha_client.close()

    async def _run_serial(self, transport: SerialMinitelTransport):
        """Connect serial transport and register with session manager."""
        backoff = 1
        while True:
            try:
                await transport.open()
                backoff = 1
                await self.session_manager.on_transport_connected(transport)
                # Wait until disconnected
                while transport.is_connected:
                    await asyncio.sleep(1)
            except Exception:
                logger.exception("Serial transport error, reconnecting in %ds", backoff)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 60)
            finally:
                await self.session_manager.on_transport_disconnected(transport)
                await transport.close()
