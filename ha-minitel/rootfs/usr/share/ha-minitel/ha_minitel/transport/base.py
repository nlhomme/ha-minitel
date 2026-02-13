"""Transport ABC for Minitel connections."""

from abc import ABC, abstractmethod


class Transport(ABC):
    """Abstract base class for Minitel transports (WS or serial)."""

    @abstractmethod
    async def send(self, data: bytes) -> None:
        """Send raw bytes to the Minitel."""

    @abstractmethod
    async def recv(self) -> bytes:
        """Receive raw bytes from the Minitel."""

    @abstractmethod
    async def close(self) -> None:
        """Close the transport."""

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Whether the transport is currently connected."""

    @property
    @abstractmethod
    def transport_id(self) -> str:
        """Unique identifier for this transport instance."""
