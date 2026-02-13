"""Base screen class with drawing helpers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from ..protocol.base import MinitelProtocol
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent
from ..i18n import I18n

if TYPE_CHECKING:
    from ..session import Session


class Screen(ABC):
    """Abstract base class for all Minitel screens."""

    def __init__(self, session: "Session"):
        self.session = session
        self.protocol: MinitelProtocol = session.protocol
        self.i18n: I18n = session.i18n

    @abstractmethod
    async def draw(self) -> bytes:
        """Render the full screen and return bytes to send."""

    @abstractmethod
    async def handle_input(self, event: InputEvent) -> bytes | None:
        """Handle input event. Return bytes to send, or None."""

    async def on_state_changed(self, entity_id: str, new_state: dict) -> bytes | None:
        """Handle real-time state update. Return partial redraw bytes or None."""
        return None

    def draw_header(self, title: str) -> bytes:
        """Draw a header bar at row 1 with inverted text."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(1, 1)
        buf += p.set_double_height()
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.set_bg_color(C.COLOR_BLUE)
        buf += p.set_invert(True)
        # Pad title to 40 chars
        padded = title[:40].center(40)
        buf += p.text(padded)
        buf += p.set_invert(False)
        buf += p.set_normal_size()
        return bytes(buf)

    def draw_footer(self, text: str) -> bytes:
        """Draw a footer at row 24."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(C.LAST_ROW, 1)
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.set_bg_color(C.COLOR_BLUE)
        buf += p.set_invert(True)
        padded = text[:40].center(40)
        buf += p.text(padded)
        buf += p.set_invert(False)
        return bytes(buf)

    def draw_menu_item(self, row: int, number: int, label: str, state: str = "") -> bytes:
        """Draw a numbered menu item."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(row, 1)
        buf += p.set_text_color(C.COLOR_YELLOW)
        buf += p.text(f"{number}.")
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.text(f" {label[:30]}")
        if state:
            buf += p.move_cursor(row, 35)
            buf += p.set_text_color(C.COLOR_CYAN)
            buf += p.text(state[:5])
        return bytes(buf)

    def draw_text_line(self, row: int, text: str, color: int = C.COLOR_WHITE) -> bytes:
        """Draw a line of text at the given row."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(row, 1)
        buf += p.set_text_color(color)
        buf += p.text(text[:40])
        return bytes(buf)

    def clear_row(self, row: int) -> bytes:
        """Clear a row by writing spaces."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(row, 1)
        buf += p.text(" " * 40)
        return bytes(buf)

    def draw_input_field(self, row: int, label: str, width: int = 20) -> bytes:
        """Draw an input field with label and underlined area."""
        p = self.protocol
        buf = bytearray()
        buf += p.move_cursor(row, 1)
        buf += p.set_text_color(C.COLOR_WHITE)
        buf += p.text(label)
        buf += p.set_underline(True)
        buf += p.text("." * width)
        buf += p.set_underline(False)
        buf += p.move_cursor(row, len(label) + 1)
        buf += p.show_cursor()
        return bytes(buf)
