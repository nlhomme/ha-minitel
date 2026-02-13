"""Minitel protocol ABC."""

from abc import ABC, abstractmethod


class MinitelProtocol(ABC):
    """Abstract interface for encoding Minitel display commands."""

    @abstractmethod
    def clear_screen(self) -> bytes:
        """Clear the entire screen."""

    @abstractmethod
    def move_cursor(self, row: int, col: int) -> bytes:
        """Position the cursor at row, col (1-based)."""

    @abstractmethod
    def show_cursor(self) -> bytes:
        """Make the cursor visible."""

    @abstractmethod
    def hide_cursor(self) -> bytes:
        """Make the cursor invisible."""

    @abstractmethod
    def text(self, s: str) -> bytes:
        """Encode a text string with accent support."""

    @abstractmethod
    def set_text_color(self, color: int) -> bytes:
        """Set text foreground color."""

    @abstractmethod
    def set_bg_color(self, color: int) -> bytes:
        """Set text background color."""

    @abstractmethod
    def set_double_height(self) -> bytes:
        """Set double height text."""

    @abstractmethod
    def set_normal_size(self) -> bytes:
        """Set normal size text."""

    @abstractmethod
    def set_underline(self, on: bool) -> bytes:
        """Enable or disable underline."""

    @abstractmethod
    def set_invert(self, on: bool) -> bytes:
        """Enable or disable inverse video."""

    @abstractmethod
    def set_blink(self, on: bool) -> bytes:
        """Enable or disable blinking."""

    @abstractmethod
    def beep(self) -> bytes:
        """Produce a beep sound."""
