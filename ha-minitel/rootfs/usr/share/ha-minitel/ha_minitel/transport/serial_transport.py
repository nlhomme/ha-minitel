"""Serial transport for physical Minitel terminals."""

import asyncio
import logging
import uuid

import serial_asyncio

from .base import Transport

logger = logging.getLogger(__name__)

PARITY_MAP = {
    "none": "N",
    "even": "E",
    "odd": "O",
}


class SerialMinitelTransport(Transport):
    """Wraps a pyserial-asyncio connection as a Transport."""

    def __init__(self, device: str, baud_rate: int = 1200, parity: str = "even"):
        self._device = device
        self._baud_rate = baud_rate
        self._parity = PARITY_MAP.get(parity, "E")
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._id = f"serial-{uuid.uuid4().hex[:8]}"
        self._connected = False

    async def open(self) -> None:
        self._reader, self._writer = await serial_asyncio.open_serial_connection(
            url=self._device,
            baudrate=self._baud_rate,
            parity=self._parity,
            bytesize=7,
            stopbits=1,
        )
        self._connected = True
        logger.info("Serial port opened: %s @ %d baud", self._device, self._baud_rate)

    async def send(self, data: bytes) -> None:
        if self._writer:
            self._writer.write(data)
            await self._writer.drain()

    async def recv(self) -> bytes:
        if not self._reader:
            raise ConnectionError("Serial port not open")
        data = await self._reader.read(256)
        if not data:
            self._connected = False
            raise ConnectionError("Serial port closed")
        return data

    async def close(self) -> None:
        self._connected = False
        if self._writer:
            self._writer.close()
            self._writer = None
        self._reader = None

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def transport_id(self) -> str:
        return self._id
