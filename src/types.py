from enum import Enum
from typing import Literal

from pyglet.customtypes import AnchorX as _AnchorX, AnchorY as _AnchorY

Point2D = tuple[float, float]
FontInfo = tuple[str | None, int | None]
ButtonStatus = Literal['Unpressed', 'Hover', 'Pressed']
Axis = Literal['x', 'y', 'xy']
AnchorX = _AnchorX | float
AnchorY = _AnchorY | float
Anchor = tuple[AnchorX, AnchorY]


class Color(Enum):
	RED = 255, 0, 0, 255
	ORANGE = 255, 167, 0, 255
	YELLOW = 255, 255, 0, 255
	GREEN = 0, 255, 0, 255
	CYAN = 0, 255, 255, 255
	BLUE = 0, 0, 255, 255
	PURPLE = 167, 0, 255, 255
	MAGENTA = 255, 0, 255, 255
	WHITE = 255, 255, 255, 255
	GRAY = 128, 128, 128, 255
	BLACK = 0, 0, 0, 255
