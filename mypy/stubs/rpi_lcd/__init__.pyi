ALIGN_FUNC: dict[str, str]
CLEAR_DISPLAY: int
ENABLE_BIT: int
LINES: dict[int, int]
LCD_BACKLIGHT: int
LCD_NOBACKLIGHT: int

class LCD:
    address: int
    bus: int
    delay: float
    rows: int
    width: int
    backlight_status: bool
    def __init__(self, address: int = 39, bus: int = 1, width: int = 20, rows: int = 4, backlight: bool = True) -> None: ...
    def write(self, byte: int, mode: int = 0) -> None: ...
    def text(self, text: str, line: int, align: str = 'left') -> None: ...
    def backlight(self, turn_on: bool = True) -> None: ...
    def get_text_line(self, text: str) -> str: ...
    def clear(self) -> None: ...
