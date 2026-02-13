"""Configuration dataclass for ha-minitel."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration parsed from CLI args."""

    language: str = "fr"
    websocket_port: int = 3615
    serial_device: str = ""
    serial_baud_rate: int = 1200
    serial_parity: str = "even"
    log_level: str = "info"
    ha_url: str = "ws://supervisor/core/websocket"
    ha_token: str = ""
