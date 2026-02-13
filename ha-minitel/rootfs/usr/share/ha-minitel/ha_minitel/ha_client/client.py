"""Home Assistant WebSocket API client."""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Callable, Awaitable, Any

import websockets

logger = logging.getLogger(__name__)


class HAClient:
    """Client for the Home Assistant WebSocket API."""

    def __init__(self, url: str, token: str):
        self._url = url
        self._token = token
        self._ws: websockets.WebSocketClientProtocol | None = None
        self._msg_id = 0
        self._pending: dict[int, asyncio.Future] = {}
        self._connected = False

    def _next_id(self) -> int:
        self._msg_id += 1
        return self._msg_id

    async def connect(self):
        """Connect and authenticate with Home Assistant."""
        self._ws = await websockets.connect(self._url)
        # Wait for auth_required
        msg = json.loads(await self._ws.recv())
        if msg.get("type") != "auth_required":
            raise RuntimeError(f"Expected auth_required, got: {msg}")

        # Send auth
        await self._ws.send(json.dumps({
            "type": "auth",
            "access_token": self._token,
        }))

        msg = json.loads(await self._ws.recv())
        if msg.get("type") != "auth_ok":
            raise RuntimeError(f"Auth failed: {msg}")

        self._connected = True
        logger.info("Connected to Home Assistant")

    async def close(self):
        self._connected = False
        if self._ws:
            await self._ws.close()

    async def _send_command(self, payload: dict) -> dict:
        """Send a command and wait for the response."""
        if not self._ws:
            raise ConnectionError("Not connected to HA")

        msg_id = self._next_id()
        payload["id"] = msg_id
        future: asyncio.Future = asyncio.get_event_loop().create_future()
        self._pending[msg_id] = future

        await self._ws.send(json.dumps(payload))
        return await future

    async def recv_loop(self, on_state_changed: Callable[[dict], Awaitable[None]]):
        """Background receive loop: dispatches responses and events."""
        if not self._ws:
            return

        # Subscribe to state changes
        sub_id = self._next_id()
        self._pending[sub_id] = asyncio.get_event_loop().create_future()
        await self._ws.send(json.dumps({
            "id": sub_id,
            "type": "subscribe_events",
            "event_type": "state_changed",
        }))

        try:
            async for raw in self._ws:
                msg = json.loads(raw)
                msg_id = msg.get("id")

                if msg.get("type") == "event" and msg_id == sub_id:
                    event_data = msg.get("event", {}).get("data", {})
                    await on_state_changed(event_data)
                elif msg_id and msg_id in self._pending:
                    future = self._pending.pop(msg_id)
                    if not future.done():
                        future.set_result(msg)
        except websockets.exceptions.ConnectionClosed:
            logger.warning("HA WebSocket connection closed")
            self._connected = False

    async def get_states(self) -> list[dict]:
        """Get all entity states."""
        result = await self._send_command({"type": "get_states"})
        return result.get("result", [])

    async def get_areas(self) -> list[dict]:
        """Get all areas (rooms)."""
        result = await self._send_command({
            "type": "config/area_registry/list",
        })
        return result.get("result", [])

    async def get_entity_registry(self) -> list[dict]:
        """Get the entity registry to map entities to areas."""
        result = await self._send_command({
            "type": "config/entity_registry/list",
        })
        return result.get("result", [])

    async def get_device_registry(self) -> list[dict]:
        """Get the device registry to map devices to areas."""
        result = await self._send_command({
            "type": "config/device_registry/list",
        })
        return result.get("result", [])

    async def get_area_entities(self, area_id: str) -> list[dict]:
        """Get entities for a given area by cross-referencing registries."""
        entities = await self.get_entity_registry()
        devices = await self.get_device_registry()
        states = await self.get_states()

        # Build device -> area map
        device_area = {}
        for dev in devices:
            if dev.get("area_id"):
                device_area[dev["id"]] = dev["area_id"]

        # Find entity_ids in area (direct or via device)
        area_entity_ids = set()
        for ent in entities:
            if ent.get("area_id") == area_id:
                area_entity_ids.add(ent["entity_id"])
            elif ent.get("device_id") and device_area.get(ent["device_id"]) == area_id:
                area_entity_ids.add(ent["entity_id"])

        # Return matching states
        return [s for s in states if s["entity_id"] in area_entity_ids]

    async def call_service(self, domain: str, service: str, entity_id: str = "", data: dict | None = None) -> dict:
        """Call a Home Assistant service."""
        payload: dict[str, Any] = {
            "type": "call_service",
            "domain": domain,
            "service": service,
        }
        target: dict[str, Any] = {}
        if entity_id:
            target["entity_id"] = entity_id
        if target:
            payload["target"] = target
        if data:
            payload["service_data"] = data
        return await self._send_command(payload)

    async def get_automations(self) -> list[dict]:
        """Get automation entities."""
        states = await self.get_states()
        return [s for s in states if s["entity_id"].startswith("automation.")]

    async def get_logbook(self, hours: int = 24) -> list[dict]:
        """Get recent logbook entries."""
        from datetime import datetime, timedelta, timezone
        start = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        result = await self._send_command({
            "type": "logbook/get_events",
            "start_time": start,
        })
        return result.get("result", [])
