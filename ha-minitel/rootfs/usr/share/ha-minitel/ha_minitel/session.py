"""Session management: one session per transport, screen navigation stack."""

import asyncio
import logging
from typing import Callable, Awaitable

from .transport.base import Transport
from .protocol.base import MinitelProtocol
from .protocol.input_handler import InputHandler, EventType
from .ha_client.client import HAClient
from .i18n import I18n
from .screens.home import HomeScreen

logger = logging.getLogger(__name__)


class Session:
    """A single Minitel session tied to one transport."""

    def __init__(
        self,
        transport: Transport,
        ha_client: HAClient,
        protocol: MinitelProtocol,
        i18n: I18n,
    ):
        self.transport = transport
        self.ha_client = ha_client
        self.protocol = protocol
        self.i18n = i18n
        self._screen_stack: list = []
        self._input_handler = InputHandler()
        self._task: asyncio.Task | None = None

    @property
    def current_screen(self):
        return self._screen_stack[-1] if self._screen_stack else None

    async def start(self):
        """Initialize session: show home screen, start input loop."""
        home = HomeScreen(self)
        await self.push_screen(home)
        self._task = asyncio.create_task(self._input_loop())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def push_screen(self, screen):
        """Push a new screen onto the stack and draw it."""
        self._screen_stack.append(screen)
        await self._send_screen()

    async def pop_screen(self) -> bool:
        """Pop the current screen. Returns False if already at home."""
        if len(self._screen_stack) <= 1:
            return False
        self._screen_stack.pop()
        await self._send_screen()
        return True

    async def go_home(self):
        """Navigate back to the home screen."""
        self._screen_stack.clear()
        home = HomeScreen(self)
        self._screen_stack.append(home)
        await self._send_screen()

    async def _send_screen(self):
        """Draw the current screen and send to transport."""
        screen = self.current_screen
        if screen:
            try:
                data = await screen.draw()
                await self.transport.send(data)
            except Exception:
                logger.exception("Error drawing screen")

    async def _input_loop(self):
        """Read input from transport and dispatch to current screen."""
        try:
            while self.transport.is_connected:
                try:
                    raw = await self.transport.recv()
                except ConnectionError:
                    break

                events = self._input_handler.feed(raw)
                for event in events:
                    response = None

                    # Global key handling
                    if event.event_type == EventType.FKEY:
                        if event.fkey == "sommaire":
                            await self.go_home()
                            continue
                        elif event.fkey == "retour":
                            popped = await self.pop_screen()
                            if popped:
                                continue
                            # If at home, let screen handle it
                        elif event.fkey == "repetition":
                            await self._send_screen()
                            continue

                    # Delegate to current screen
                    screen = self.current_screen
                    if screen:
                        try:
                            response = await screen.handle_input(event)
                        except Exception:
                            logger.exception("Error handling input")

                    if response:
                        await self.transport.send(response)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Input loop error for %s", self.transport.transport_id)

    async def on_state_changed(self, entity_id: str, new_state: dict):
        """Forward state change to the current screen for partial redraw."""
        screen = self.current_screen
        if screen:
            try:
                response = await screen.on_state_changed(entity_id, new_state)
                if response:
                    await self.transport.send(response)
            except Exception:
                logger.exception("Error in on_state_changed")


class SessionManager:
    """Manages all active sessions and broadcasts HA events."""

    def __init__(self, ha_client: HAClient, protocol: MinitelProtocol, i18n: I18n):
        self.ha_client = ha_client
        self.protocol = protocol
        self.i18n = i18n
        self._sessions: dict[str, Session] = {}

    async def on_transport_connected(self, transport: Transport):
        """Create and start a new session for the transport."""
        session = Session(transport, self.ha_client, self.protocol, self.i18n)
        self._sessions[transport.transport_id] = session
        logger.info("Session started: %s", transport.transport_id)
        await session.start()

    async def on_transport_disconnected(self, transport: Transport):
        """Stop and remove a session."""
        session = self._sessions.pop(transport.transport_id, None)
        if session:
            await session.stop()
            logger.info("Session ended: %s", transport.transport_id)

    async def on_state_changed(self, event_data: dict):
        """Broadcast state change to all sessions."""
        entity_id = event_data.get("entity_id", "")
        new_state = event_data.get("new_state", {})
        if not entity_id or not new_state:
            return

        for session in list(self._sessions.values()):
            await session.on_state_changed(entity_id, new_state)
