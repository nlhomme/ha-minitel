"""Input event parsing from raw Minitel bytes."""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional

from . import constants as C


class EventType(Enum):
    CHAR = auto()       # Regular character input
    FKEY = auto()       # Function key press
    UNKNOWN = auto()    # Unrecognized input


@dataclass
class InputEvent:
    event_type: EventType
    char: str = ""
    fkey: str = ""
    raw: bytes = b""


class InputHandler:
    """Parses raw Minitel byte stream into InputEvents."""

    def __init__(self):
        self._buffer = bytearray()

    def feed(self, data: bytes) -> list[InputEvent]:
        """Feed raw bytes and return parsed events."""
        self._buffer.extend(data)
        events = []

        while self._buffer:
            event = self._try_parse()
            if event is None:
                break
            events.append(event)

        return events

    def _try_parse(self) -> Optional[InputEvent]:
        if not self._buffer:
            return None

        b = self._buffer[0]

        # Function key: SEP + code
        if b == C.SEP:
            if len(self._buffer) < 2:
                return None  # wait for more data
            code = self._buffer[1]
            raw = bytes(self._buffer[:2])
            del self._buffer[:2]
            name = C.FKEY_NAMES.get(code, f"unknown_0x{code:02x}")
            return InputEvent(EventType.FKEY, fkey=name, raw=raw)

        # Regular printable character
        if 0x20 <= b <= 0x7E:
            del self._buffer[:1]
            return InputEvent(EventType.CHAR, char=chr(b), raw=bytes([b]))

        # CR (Enter without function key context)
        if b == C.CR:
            del self._buffer[:1]
            return InputEvent(EventType.CHAR, char="\r", raw=bytes([b]))

        # Backspace
        if b == C.BS:
            del self._buffer[:1]
            return InputEvent(EventType.CHAR, char="\b", raw=bytes([b]))

        # Unknown byte - consume and skip
        del self._buffer[:1]
        return InputEvent(EventType.UNKNOWN, raw=bytes([b]))
