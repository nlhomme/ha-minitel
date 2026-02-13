"""Videotex constants: control codes, colors, function keys, accent mapping."""

# Control codes
ESC = 0x1B
US = 0x1F
RS = 0x1E
FF = 0x0C  # Clear screen
LF = 0x0A  # Line feed
CR = 0x0D  # Carriage return
BS = 0x08  # Backspace
HT = 0x09  # Tab
BEL = 0x07  # Bell
CON = 0x11  # Cursor on
COFF = 0x14  # Cursor off
SEP = 0x13  # Function key separator
SS2 = 0x19  # Single shift 2 (accented characters)
REP = 0x12  # Repeat character
SP = 0x20  # Space
DEL = 0x7F  # Delete

# Cursor positioning: US row col (row and col offset by 0x40)
CURSOR_POS_OFFSET = 0x40

# Screen dimensions (Minitel standard)
SCREEN_ROWS = 24
SCREEN_COLS = 40
STATUS_ROW = 0  # Row 0 is the status line (read-only)
FIRST_ROW = 1
LAST_ROW = 24

# ESC sequence attributes
ATTR_TEXT = 0x40  # Text attributes base
ATTR_BG = 0x50  # Background attributes base

# Text colors (ESC + 0x40 + code)
COLOR_BLACK = 0
COLOR_RED = 1
COLOR_GREEN = 2
COLOR_YELLOW = 3
COLOR_BLUE = 4
COLOR_MAGENTA = 5
COLOR_CYAN = 6
COLOR_WHITE = 7

# Text style attributes (ESC + code)
STYLE_NORMAL_SIZE = 0x4C
STYLE_DOUBLE_HEIGHT = 0x4D
STYLE_DOUBLE_WIDTH = 0x4E
STYLE_DOUBLE_SIZE = 0x4F
STYLE_BLINK_ON = 0x48
STYLE_BLINK_OFF = 0x49
STYLE_UNDERLINE_ON = 0x5A
STYLE_UNDERLINE_OFF = 0x59
STYLE_INVERT_ON = 0x5D
STYLE_INVERT_OFF = 0x5C

# Function keys (SEP + code)
FKEY_ENVOI = 0x41  # Send/Submit
FKEY_RETOUR = 0x42  # Back
FKEY_REPETITION = 0x43  # Repeat/Refresh
FKEY_GUIDE = 0x44  # Guide/Help
FKEY_ANNULATION = 0x45  # Cancel
FKEY_SOMMAIRE = 0x46  # Home/Summary
FKEY_CORRECTION = 0x47  # Correction/Delete
FKEY_SUITE = 0x48  # Next page
FKEY_CONNEXION = 0x49  # Connect/Disconnect (Connexion/Fin)

FKEY_NAMES = {
    FKEY_ENVOI: "envoi",
    FKEY_RETOUR: "retour",
    FKEY_REPETITION: "repetition",
    FKEY_GUIDE: "guide",
    FKEY_ANNULATION: "annulation",
    FKEY_SOMMAIRE: "sommaire",
    FKEY_CORRECTION: "correction",
    FKEY_SUITE: "suite",
    FKEY_CONNEXION: "connexion",
}

# Accent map: accented char -> SS2 + accent code + base char
# SS2 accent codes
ACCENT_GRAVE = 0x41
ACCENT_ACUTE = 0x42
ACCENT_CIRCUMFLEX = 0x43
ACCENT_DIAERESIS = 0x48
ACCENT_CEDILLA = 0x4B

ACCENT_MAP = {
    "à": (ACCENT_GRAVE, ord("a")),
    "è": (ACCENT_GRAVE, ord("e")),
    "ù": (ACCENT_GRAVE, ord("u")),
    "é": (ACCENT_ACUTE, ord("e")),
    "â": (ACCENT_CIRCUMFLEX, ord("a")),
    "ê": (ACCENT_CIRCUMFLEX, ord("e")),
    "î": (ACCENT_CIRCUMFLEX, ord("i")),
    "ô": (ACCENT_CIRCUMFLEX, ord("o")),
    "û": (ACCENT_CIRCUMFLEX, ord("u")),
    "ë": (ACCENT_DIAERESIS, ord("e")),
    "ï": (ACCENT_DIAERESIS, ord("i")),
    "ü": (ACCENT_DIAERESIS, ord("u")),
    "ç": (ACCENT_CEDILLA, ord("c")),
}
