"""Room entities screen with pagination."""

import logging
import math

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 8


def friendly_name(entity: dict) -> str:
    return entity.get("attributes", {}).get("friendly_name", entity["entity_id"])


def short_state(entity: dict) -> str:
    return entity.get("state", "?")[:5]


class RoomsScreen(Screen):
    """Display entities in a room with pagination."""

    def __init__(self, session, area: dict):
        super().__init__(session)
        self.area = area
        self.entities: list[dict] = []
        self.page = 0
        self.total_pages = 1
        self.input_buf = ""

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()
        buf += p.hide_cursor()

        area_name = self.area.get("name", self.area.get("area_id", "?"))
        buf += self.draw_header(i18n.t("rooms.title", name=area_name))

        # Load entities
        try:
            area_id = self.area.get("area_id", self.area.get("id", ""))
            self.entities = await self.session.ha_client.get_area_entities(area_id)
        except Exception:
            logger.exception("Failed to load entities")
            self.entities = []

        if not self.entities:
            buf += self.draw_text_line(5, i18n.t("rooms.no_entities"), C.COLOR_YELLOW)
            buf += self.draw_footer(i18n.t("rooms.footer"))
            return bytes(buf)

        self.total_pages = max(1, math.ceil(len(self.entities) / ITEMS_PER_PAGE))
        start = self.page * ITEMS_PER_PAGE
        page_entities = self.entities[start:start + ITEMS_PER_PAGE]

        # Page indicator
        buf += p.move_cursor(3, 1)
        buf += p.set_text_color(C.COLOR_CYAN)
        buf += p.text(i18n.t("rooms.page", current=self.page + 1, total=self.total_pages))

        # Entity list
        for i, ent in enumerate(page_entities):
            buf += self.draw_menu_item(5 + i, i + 1, friendly_name(ent), short_state(ent))

        # Input prompt
        buf += p.move_cursor(22, 1)
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.text("N\xb0: ")
        buf += p.show_cursor()

        buf += self.draw_footer(i18n.t("rooms.footer"))
        return bytes(buf)

    async def _redraw_page(self) -> bytes:
        """Redraw current page content."""
        return await self.draw()

    async def handle_input(self, event: InputEvent) -> bytes | None:
        if event.event_type == EventType.FKEY:
            if event.fkey == "suite" and self.page < self.total_pages - 1:
                self.page += 1
                return await self._redraw_page()
            elif event.fkey == "retour":
                if self.page > 0:
                    self.page -= 1
                    return await self._redraw_page()
                # else go back (handled by session)
                return None
            elif event.fkey == "envoi":
                return await self._select_entity()
            return None

        if event.event_type == EventType.CHAR:
            if event.char.isdigit():
                self.input_buf += event.char
                return self.protocol.text(event.char)
            elif event.char == "\r":
                return await self._select_entity()
            elif event.char == "\b" and self.input_buf:
                self.input_buf = self.input_buf[:-1]
                return self.protocol.text("\b \b")

        return None

    async def _select_entity(self) -> bytes | None:
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
        if 0 <= idx < len(self.entities):
            entity = self.entities[idx]
            from .entity_detail import EntityDetailScreen
            screen = EntityDetailScreen(self.session, entity)
            await self.session.push_screen(screen)
        return None

    async def on_state_changed(self, entity_id: str, new_state: dict) -> bytes | None:
        """Partial redraw: update just the state column for matching entity."""
        start = self.page * ITEMS_PER_PAGE
        page_entities = self.entities[start:start + ITEMS_PER_PAGE]
        for i, ent in enumerate(page_entities):
            if ent["entity_id"] == entity_id:
                ent["state"] = new_state.get("state", ent["state"])
                if "attributes" in new_state:
                    ent.setdefault("attributes", {}).update(new_state["attributes"])
                row = 5 + i
                p = self.protocol
                buf = bytearray()
                buf += p.move_cursor(row, 35)
                buf += p.set_text_color(C.COLOR_CYAN)
                buf += p.text(short_state(ent))
                return bytes(buf)
        return None
