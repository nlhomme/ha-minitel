# Minitel for Home Assistant

Browse and control your Home Assistant instance from a Minitel terminal or emulator.

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armhf Architecture][armhf-shield]
![Supports armv7 Architecture][armv7-shield]
![Supports i386 Architecture][i386-shield]

## Installation

1. In Home Assistant, go to **Settings > Add-ons > Add-on Store**.
2. Click the three-dot menu (top right) and select **Repositories**.
3. Add this repository URL:
   ```
   https://github.com/nlhomme/ha-minitel
   ```
   Or click the button below:

   [![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fnlhomme%2Fha-minitel)

4. Find **Minitel for Home Assistant** in the add-on store and click **Install**.
5. Go to the add-on **Configuration** tab to adjust settings (language, serial port, etc.).
6. Start the add-on.

## Connecting

### With an emulator

Point a WebSocket Minitel emulator to:

```
ws://<your-ha-ip>:3615/
```

Recommended emulators:
- **MiEdit** — desktop emulator, ideal for testing
- **3615co.de** — web-based emulator

Make sure to use binary WebSocket frames for correct Videotex byte handling.

### With a physical Minitel

1. Connect the Minitel to a USB serial adapter (DIN-5 to USB).
2. In the add-on configuration, set:
   - `serial_enabled` to `true`
   - `serial_device` to the device path (e.g. `/dev/ttyUSB0`)
   - `serial_baud_rate` to match your Minitel (usually `1200`)
   - `serial_parity` to `even` (Minitel standard: 7E1)
3. Restart the add-on.

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

| Key | Action |
|-----|--------|
| **0-9** | Select a menu item |
| **ENVOI** | Submit / confirm |
| **RETOUR** | Go back |
| **SUITE** | Next page |
| **SOMMAIRE** | Return to home screen |
| **REPETITION** | Refresh current screen |

### Screens

- **Home** — Lists your rooms (areas) numbered 1-8, plus **9** for Automations and **0** for Logs.
- **Room** — Entities in the selected area with live state. Paginated with SUITE/RETOUR. Type a number + ENVOI to view details.
- **Entity Detail** — State and attributes. **1** to toggle, **2** to open the control form.
- **Entity Control** — Numeric input for brightness, temperature, or position. Type a value and press ENVOI.
- **Automations** — List with trigger via number + ENVOI.
- **Logs** — Recent logbook entries, paginated.

## Features

- WebSocket server for emulators (MiEdit, 3615co.de)
- Serial port support for physical Minitel terminals (7E1, 1200/4800/9600 baud)
- Navigate rooms and entities with classic Minitel function keys
- Toggle and control lights, switches, covers, climate
- View and trigger automations
- Browse recent logbook entries
- Real-time state updates with partial screen redraw
- French and English interface

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[i386-shield]: https://img.shields.io/badge/i386-yes-green.svg
