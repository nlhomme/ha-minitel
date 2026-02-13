"""WebSocket server and transport for Minitel emulators."""

import asyncio
import logging
import ssl
import uuid
from typing import Callable, Awaitable, Optional

import websockets
import websockets.server

from .base import Transport

logger = logging.getLogger(__name__)


class WebSocketTransport(Transport):
    """Wraps a WebSocket connection as a Transport."""

    def __init__(self, ws: websockets.server.WebSocketServerProtocol):
        self._ws = ws
        self._id = f"ws-{uuid.uuid4().hex[:8]}"

    async def send(self, data: bytes) -> None:
        await self._ws.send(data)

    async def recv(self) -> bytes:
        data = await self._ws.recv()
        if isinstance(data, str):
            return data.encode("latin-1")
        return data

    async def close(self) -> None:
        await self._ws.close()

    @property
    def is_connected(self) -> bool:
        return self._ws.open

    @property
    def transport_id(self) -> str:
        return self._id


class WebSocketServer:
    """WebSocket server that creates a transport per connection."""

    def __init__(
        self,
        port: int,
        on_connect: Callable[[Transport], Awaitable[None]],
        on_disconnect: Callable[[Transport], Awaitable[None]],
        ssl_certfile: str = "",
        ssl_keyfile: str = "",
    ):
        self.port = port
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._ssl_context: Optional[ssl.SSLContext] = None
        if ssl_certfile and ssl_keyfile:
            self._ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self._ssl_context.load_cert_chain(ssl_certfile, ssl_keyfile)

    async def serve(self):
        async with websockets.serve(
            self._handler,
            "0.0.0.0",
            self.port,
            subprotocols=["minitel"],
            ssl=self._ssl_context,
        ):
            scheme = "wss" if self._ssl_context else "ws"
            logger.info("%s server listening on port %d", scheme.upper(), self.port)
            await asyncio.Future()  # run forever

    async def _handler(self, ws: websockets.server.WebSocketServerProtocol):
        transport = WebSocketTransport(ws)
        logger.info("New WebSocket connection: %s", transport.transport_id)
        try:
            await self._on_connect(transport)
            await ws.wait_closed()
        finally:
            await self._on_disconnect(transport)
            logger.info("WebSocket disconnected: %s", transport.transport_id)
