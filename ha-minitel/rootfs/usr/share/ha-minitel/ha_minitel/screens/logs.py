"""Logs screen: recent logbook entries with pagination."""

from __future__ import annotations

import logging
import math

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 15


class LogsScreen(Screen):
    """Display recent logbook entries."""

    def __init__(self, session):
        super().__init__(session)
        self.entries: list[dict] = []
        self.page = 0
        self.total_pages = 1

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()
        buf += p.hide_cursor()

        buf += self.draw_header(i18n.t("logs.title"))

        try:
            self.entries = await self.session.ha_client.get_logbook(hours=24)
            # Most recent first
            self.entries.reverse()
        except Exception:
            logger.exception("Failed to load logbook")
            self.entries = []

        if not self.entries:
            buf += self.draw_text_line(5, i18n.t("logs.empty"), C.COLOR_YELLOW)
            buf += self.draw_footer(i18n.t("logs.footer"))
            return bytes(buf)

        self.total_pages = max(1, math.ceil(len(self.entries) / ITEMS_PER_PAGE))

        buf += p.move_cursor(3, 1)
        buf += p.set_text_color(C.COLOR_CYAN)
        buf += p.text(i18n.t("rooms.page", current=self.page + 1, total=self.total_pages))

        start = self.page * ITEMS_PER_PAGE
        page_entries = self.entries[start:start + ITEMS_PER_PAGE]

        for i, entry in enumerate(page_entries):
            name = entry.get("name", entry.get("entity_id", "?"))[:20]
            message = entry.get("message", entry.get("state", ""))[:18]
            row = 5 + i
            buf += p.move_cursor(row, 1)
            buf += p.set_text_color(C.COLOR_WHITE)
            buf += p.text(f"{name[:20]}")
            buf += p.move_cursor(row, 22)
            buf += p.set_text_color(C.COLOR_CYAN)
            buf += p.text(f"{message[:18]}")

        buf += self.draw_footer(i18n.t("logs.footer"))
        return bytes(buf)

    async def handle_input(self, event: InputEvent) -> bytes | None:
        if event.event_type == EventType.FKEY:
            if event.fkey == "suite" and self.page < self.total_pages - 1:
                self.page += 1
                return await self.draw()
            elif event.fkey == "retour" and self.page > 0:
                self.page -= 1
                return await self.draw()

        return None
