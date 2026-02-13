"""Concrete Videotex protocol implementation."""

from .base import MinitelProtocol
from . import constants as C


class VideotexProtocol(MinitelProtocol):
    """Encodes Minitel Videotex display commands."""

    def clear_screen(self) -> bytes:
        return bytes([C.FF])

    def move_cursor(self, row: int, col: int) -> bytes:
        return bytes([C.US, C.CURSOR_POS_OFFSET + row, C.CURSOR_POS_OFFSET + col])

    def show_cursor(self) -> bytes:
        return bytes([C.CON])

    def hide_cursor(self) -> bytes:
        return bytes([C.COFF])

    def text(self, s: str) -> bytes:
        result = bytearray()
        for ch in s:
            if ch in C.ACCENT_MAP:
                accent_code, base_char = C.ACCENT_MAP[ch]
                result.extend([C.SS2, accent_code, base_char])
            elif ch == "\n":
                result.extend([C.CR, C.LF])
            elif ord(ch) < 0x80:
                result.append(ord(ch))
            else:
                # Fallback: replace unsupported chars with '?'
                result.append(ord("?"))
        return bytes(result)

    def set_text_color(self, color: int) -> bytes:
        return bytes([C.ESC, C.ATTR_TEXT + color])

    def set_bg_color(self, color: int) -> bytes:
        return bytes([C.ESC, C.ATTR_BG + color])

    def set_double_height(self) -> bytes:
        return bytes([C.ESC, C.STYLE_DOUBLE_HEIGHT])

    def set_normal_size(self) -> bytes:
        return bytes([C.ESC, C.STYLE_NORMAL_SIZE])

    def set_underline(self, on: bool) -> bytes:
        code = C.STYLE_UNDERLINE_ON if on else C.STYLE_UNDERLINE_OFF
        return bytes([C.ESC, code])

    def set_invert(self, on: bool) -> bytes:
        code = C.STYLE_INVERT_ON if on else C.STYLE_INVERT_OFF
        return bytes([C.ESC, code])

    def set_blink(self, on: bool) -> bytes:
        code = C.STYLE_BLINK_ON if on else C.STYLE_BLINK_OFF
        return bytes([C.ESC, code])

    def beep(self) -> bytes:
        return bytes([C.BEL])
