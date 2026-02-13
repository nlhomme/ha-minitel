# Minitel for Home Assistant

## How it works

This add-on exposes a WebSocket server (port 3615 by default) that speaks the Videotex protocol used by Minitel terminals. You can connect using:

- **MiEdit** emulator (recommended for testing)
- **3615co.de** web-based emulator
- A **physical Minitel** terminal via USB serial adapter

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `language` | `fr` | Display language (`fr` or `en`) |
| `websocket_port` | `3615` | WebSocket server port |
| `serial_enabled` | `false` | Enable serial port for physical Minitel |
| `serial_device` | *(empty)* | Serial device path (e.g. `/dev/ttyUSB0`) |
| `serial_baud_rate` | `1200` | Serial baud rate (1200, 4800, or 9600) |
| `serial_parity` | `even` | Serial parity (none, even, or odd) |
| `log_level` | `info` | Log level (debug, info, warning, error) |

## Navigation

The interface uses classic Minitel function keys:

- **Number keys (0-9)**: Select menu items
- **ENVOI**: Submit/confirm selection
- **RETOUR**: Go back to previous screen
- **SUITE**: Next page (in lists)
- **SOMMAIRE**: Return to home screen
- **REPETITION**: Refresh current screen

## Screens

### Home (SOMMAIRE)
Lists your Home Assistant areas (rooms) numbered 1-8, with:
- **9** for Automations
- **0** for Logs

### Room
Shows entities in the selected area with their current state. Use SUITE/RETOUR for pagination. Type an entity number + ENVOI to view details.

### Entity Detail
Shows entity state and attributes. Options:
- **1**: Toggle on/off (for lights, switches, etc.)
- **2**: Open control form (for dimmable lights, covers, climate)

### Entity Control
Form-based input for numeric attributes (brightness, temperature, position). Type the value and press ENVOI.

### Automations
Lists automations with their state. Type a number + ENVOI to trigger.

### Logs
Recent logbook entries with SUITE/RETOUR pagination.

## Connecting a physical Minitel

1. Connect the Minitel to a USB serial adapter (DIN-5 to USB)
2. Set `serial_enabled` to `true`
3. Set `serial_device` to the device path (e.g. `/dev/ttyUSB0`)
4. Set `serial_baud_rate` to match your Minitel (usually `1200`)
5. Set `serial_parity` to `even` (Minitel standard: 7E1)

## Connecting with an emulator

Point your WebSocket Minitel emulator to:

```
ws://<your-ha-ip>:3615/
```

Use binary WebSocket frames for correct Videotex byte handling.
