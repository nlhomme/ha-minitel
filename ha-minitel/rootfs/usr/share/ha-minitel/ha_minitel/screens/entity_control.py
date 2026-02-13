"""Entity control screen: form-based input for brightness, temperature, etc."""

from __future__ import annotations

import logging

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)


def entity_domain(entity_id: str) -> str:
    return entity_id.split(".")[0]


def friendly_name(entity: dict) -> str:
    return entity.get("attributes", {}).get("friendly_name", entity["entity_id"])


# Domain -> list of (attribute_key, service, service_data_key, i18n_key)
CONTROL_MAP = {
    "light": [
        ("brightness", "turn_on", "brightness", "control.brightness"),
    ],
    "cover": [
        ("current_position", "set_cover_position", "position", "control.position"),
    ],
    "climate": [
        ("temperature", "set_temperature", "temperature", "control.temperature"),
    ],
    "fan": [
        ("percentage", "set_percentage", "percentage", "control.position"),
    ],
}


class EntityControlScreen(Screen):
    """Form screen for controlling entity attributes."""

    def __init__(self, session, entity: dict):
        super().__init__(session)
        self.entity = entity
        self.domain = entity_domain(entity["entity_id"])
        self.controls = CONTROL_MAP.get(self.domain, [])
        self.current_field = 0
        self.input_buf = ""

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()

        name = friendly_name(self.entity)
        buf += self.draw_header(i18n.t("control.title", name=name))

        if not self.controls:
            buf += self.draw_text_line(5, i18n.t("entity.unavailable"), C.COLOR_RED)
            buf += self.draw_footer(i18n.t("entity.back"))
            return bytes(buf)

        row = 5
        for i, (attr_key, _, _, label_key) in enumerate(self.controls):
            current_val = self.entity.get("attributes", {}).get(attr_key, "?")
            buf += self.draw_text_line(row, f"  Actuel: {current_val}", C.COLOR_GREEN)
            row += 1
            if i == self.current_field:
                buf += self.draw_input_field(row, f"  {i18n.t(label_key)} ")
            else:
                buf += self.draw_text_line(row, f"  {i18n.t(label_key)}", C.COLOR_WHITE)
            row += 2

        buf += self.draw_text_line(20, i18n.t("control.submit"), C.COLOR_CYAN)
        buf += self.draw_footer(name[:40])

        return bytes(buf)

    async def handle_input(self, event: InputEvent) -> bytes | None:
        p = self.protocol
        i18n = self.i18n

        if event.event_type == EventType.FKEY:
            if event.fkey == "envoi":
                return await self._submit()
            return None

        if event.event_type == EventType.CHAR:
            if event.char.isdigit() or event.char == ".":
                self.input_buf += event.char
                return p.text(event.char)
            elif event.char == "\r":
                return await self._submit()
            elif event.char == "\b" and self.input_buf:
                self.input_buf = self.input_buf[:-1]
                return p.text("\b \b")

        return None

    async def _submit(self) -> bytes:
        i18n = self.i18n
        if not self.input_buf or not self.controls:
            return b""

        try:
            value = float(self.input_buf)
        except ValueError:
            self.input_buf = ""
            return self.draw_text_line(22, i18n.t("control.error", msg="invalid"), C.COLOR_RED)

        _, service, data_key, _ = self.controls[self.current_field]
        eid = self.entity["entity_id"]

        try:
            await self.session.ha_client.call_service(
                self.domain, service, eid, {data_key: value}
            )
            self.input_buf = ""
            result = self.draw_text_line(22, i18n.t("control.success"), C.COLOR_GREEN)
            # Refresh entity
            states = await self.session.ha_client.get_states()
            for s in states:
                if s["entity_id"] == eid:
                    self.entity = s
                    break
            return result + await self.draw()
        except Exception as e:
            logger.exception("Service call failed")
            self.input_buf = ""
            return self.draw_text_line(22, i18n.t("control.error", msg=str(e)[:30]), C.COLOR_RED)
