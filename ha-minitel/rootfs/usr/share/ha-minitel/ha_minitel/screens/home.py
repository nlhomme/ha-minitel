"""Home screen: area list + automations/logs menu."""

import logging

from .base import Screen
from ..protocol import constants as C
from ..protocol.input_handler import InputEvent, EventType

logger = logging.getLogger(__name__)


class HomeScreen(Screen):
    """Main menu: list areas (1-8), automations (9), logs (0)."""

    def __init__(self, session):
        super().__init__(session)
        self.areas: list[dict] = []

    async def draw(self) -> bytes:
        p = self.protocol
        i18n = self.i18n
        buf = bytearray()

        buf += p.clear_screen()
        buf += p.hide_cursor()

        # Header
        buf += self.draw_header(i18n.t("home.title"))

        # Subtitle
        buf += p.move_cursor(3, 1)
        buf += p.set_text_color(C.COLOR_CYAN)
        buf += p.set_double_height()
        buf += p.text(f"  {i18n.t('home.subtitle')}")
        buf += p.set_normal_size()

        # Load areas
        try:
            self.areas = await self.session.ha_client.get_areas()
        except Exception:
            logger.exception("Failed to load areas")
            self.areas = []

        # Areas header
        buf += p.move_cursor(6, 1)
        buf += p.set_text_color(C.COLOR_GREEN)
        buf += p.text(f"  {i18n.t('home.areas_header')}:")

        # List areas (max 8)
        for i, area in enumerate(self.areas[:8]):
            name = area.get("name", area.get("area_id", "?"))
            buf += self.draw_menu_item(8 + i, i + 1, name)

        # Automations & Logs
        row = max(17, 8 + len(self.areas[:8]) + 1)
        buf += self.draw_menu_item(row, 9, i18n.t("home.automations"))
        buf += self.draw_menu_item(row + 1, 0, i18n.t("home.logs"))

        # Footer
        buf += self.draw_footer(i18n.t("home.footer"))

        return bytes(buf)

    async def handle_input(self, event: InputEvent) -> bytes | None:
        if event.event_type != EventType.CHAR:
            return None

        ch = event.char
        if ch.isdigit():
            num = int(ch)
            if 1 <= num <= len(self.areas):
                area = self.areas[num - 1]
                from .rooms import RoomsScreen
                screen = RoomsScreen(self.session, area)
                await self.session.push_screen(screen)
                return None  # push_screen draws
            elif num == 9:
                from .automations import AutomationsScreen
                screen = AutomationsScreen(self.session)
                await self.session.push_screen(screen)
                return None
            elif num == 0:
                from .logs import LogsScreen
                screen = LogsScreen(self.session)
                await self.session.push_screen(screen)
                return None

        return None
