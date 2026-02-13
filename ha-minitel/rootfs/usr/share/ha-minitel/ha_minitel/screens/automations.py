"""Automations screen: list and trigger automations."""

import logging
import math

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 8


def friendly_name(entity: dict) -> str:
    return entity.get("attributes", {}).get("friendly_name", entity["entity_id"])


class AutomationsScreen(Screen):
    """List automations with pagination, trigger with N+ENVOI."""

    def __init__(self, session):
        super().__init__(session)
        self.automations: list[dict] = []
        self.page = 0
        self.total_pages = 1
        self.input_buf = ""

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()
        buf += p.hide_cursor()

        buf += self.draw_header(i18n.t("automations.title"))

        try:
            self.automations = await self.session.ha_client.get_automations()
        except Exception:
            logger.exception("Failed to load automations")
            self.automations = []

        self.total_pages = max(1, math.ceil(len(self.automations) / ITEMS_PER_PAGE))

        # Page info
        buf += p.move_cursor(3, 1)
        buf += p.set_text_color(C.COLOR_CYAN)
        buf += p.text(i18n.t("rooms.page", current=self.page + 1, total=self.total_pages))

        start = self.page * ITEMS_PER_PAGE
        page_items = self.automations[start:start + ITEMS_PER_PAGE]

        for i, auto in enumerate(page_items):
            name = friendly_name(auto)
            state = auto.get("state", "?")[:5]
            buf += self.draw_menu_item(5 + i, i + 1, name, state)

        buf += self.draw_text_line(20, i18n.t("automations.trigger"), C.COLOR_CYAN)

        # Input prompt
        buf += p.move_cursor(22, 1)
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.text("N\xb0: ")
        buf += p.show_cursor()

        buf += self.draw_footer(i18n.t("automations.footer"))
        return bytes(buf)

    async def handle_input(self, event: InputEvent) -> bytes | None:
        if event.event_type == EventType.FKEY:
            if event.fkey == "suite" and self.page < self.total_pages - 1:
                self.page += 1
                return await self.draw()
            elif event.fkey == "retour" and self.page > 0:
                self.page -= 1
                return await self.draw()
            elif event.fkey == "envoi":
                return await self._trigger()
            return None

        if event.event_type == EventType.CHAR:
            if event.char.isdigit():
                self.input_buf += event.char
                return self.protocol.text(event.char)
            elif event.char == "\r":
                return await self._trigger()
            elif event.char == "\b" and self.input_buf:
                self.input_buf = self.input_buf[:-1]
                return self.protocol.text("\b \b")

        return None

    async def _trigger(self) -> bytes | None:
        if not self.input_buf:
            return None
        try:
            num = int(self.input_buf)
        except ValueError:
            self.input_buf = ""
            return None
        self.input_buf = ""

        start = self.page * ITEMS_PER_PAGE
        idx = start + num - 1
        if 0 <= idx < len(self.automations):
            auto = self.automations[idx]
            eid = auto["entity_id"]
            try:
                await self.session.ha_client.call_service("automation", "trigger", eid)
                return self.draw_text_line(22, self.i18n.t("automations.triggered"), C.COLOR_GREEN)
            except Exception:
                logger.exception("Trigger failed")
                return self.draw_text_line(22, self.i18n.t("common.error"), C.COLOR_RED)
        return None
