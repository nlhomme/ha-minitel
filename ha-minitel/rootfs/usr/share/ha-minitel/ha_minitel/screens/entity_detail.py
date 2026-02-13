"""Entity detail screen: state + domain-specific controls."""

from __future__ import annotations

import logging

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)

# Domains that support toggle
TOGGLEABLE = {"light", "switch", "fan", "input_boolean", "automation", "cover", "media_player"}
# Domains that have controllable attributes
CONTROLLABLE = {"light", "cover", "climate", "fan"}


def entity_domain(entity_id: str) -> str:
    return entity_id.split(".")[0]


def friendly_name(entity: dict) -> str:
    return entity.get("attributes", {}).get("friendly_name", entity["entity_id"])


class EntityDetailScreen(Screen):
    """Show entity state and available controls."""

    def __init__(self, session, entity: dict):
        super().__init__(session)
        self.entity = entity

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()
        buf += p.hide_cursor()

        name = friendly_name(self.entity)
        buf += self.draw_header(i18n.t("entity.title"))

        # Entity name
        buf += p.move_cursor(3, 1)
        buf += p.set_double_height()
        buf += p.set_text_color(C.COLOR_CYAN)
        buf += p.text(f" {name[:38]}")
        buf += p.set_normal_size()

        # State
        state = self.entity.get("state", "unknown")
        buf += p.move_cursor(6, 1)
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.text(i18n.t("entity.state", state=state))

        # Attributes
        attrs = self.entity.get("attributes", {})
        row = 8
        for key in ("brightness", "color_temp", "temperature", "current_temperature", "position"):
            if key in attrs:
                buf += self.draw_text_line(row, f"  {key}: {attrs[key]}", C.COLOR_GREEN)
                row += 1
                if row > 16:
                    break

        # Actions
        domain = entity_domain(self.entity["entity_id"])
        action_row = 18
        if domain in TOGGLEABLE:
            buf += self.draw_text_line(action_row, i18n.t("entity.toggle"), C.COLOR_YELLOW)
            action_row += 1
        if domain in CONTROLLABLE:
            buf += self.draw_text_line(action_row, i18n.t("entity.control"), C.COLOR_YELLOW)
            action_row += 1

        buf += self.draw_text_line(22, i18n.t("entity.back"), C.COLOR_CYAN)
        buf += self.draw_footer(name[:40])

        return bytes(buf)

    async def handle_input(self, event: InputEvent) -> bytes | None:
        if event.event_type != EventType.CHAR:
            return None

        domain = entity_domain(self.entity["entity_id"])
        eid = self.entity["entity_id"]

        if event.char == "1" and domain in TOGGLEABLE:
            try:
                service = "toggle"
                await self.session.ha_client.call_service(domain, service, eid)
                # Refresh state
                states = await self.session.ha_client.get_states()
                for s in states:
                    if s["entity_id"] == eid:
                        self.entity = s
                        break
                return await self.draw()
            except Exception:
                logger.exception("Toggle failed")
                return self.draw_text_line(20, self.i18n.t("common.error"), C.COLOR_RED)

        if event.char == "2" and domain in CONTROLLABLE:
            from .entity_control import EntityControlScreen
            screen = EntityControlScreen(self.session, self.entity)
            await self.session.push_screen(screen)
            return None

        return None

    async def on_state_changed(self, entity_id: str, new_state: dict) -> bytes | None:
        if entity_id != self.entity["entity_id"]:
            return None
        self.entity["state"] = new_state.get("state", self.entity["state"])
        if "attributes" in new_state:
            self.entity.setdefault("attributes", {}).update(new_state["attributes"])
        # Partial redraw: just the state line
        state = self.entity.get("state", "unknown")
        return self.draw_text_line(6, self.i18n.t("entity.state", state=state))
