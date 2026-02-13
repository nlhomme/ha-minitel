"""Minitel UI screens."""

from .base import Screen
from .home import HomeScreen
from .rooms import RoomsScreen
from .entity_detail import EntityDetailScreen
from .entity_control import EntityControlScreen
from .automations import AutomationsScreen
from .logs import LogsScreen

__all__ = [
    "Screen", "HomeScreen", "RoomsScreen", "EntityDetailScreen",
    "EntityControlScreen", "AutomationsScreen", "LogsScreen",
]
