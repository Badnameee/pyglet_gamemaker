"""Stores all custom types used in library.

- Point2D: (float, float) - for 2D points
- FontInfo: (type, size)
- ButtonStatus: A status for button widgets. See `~pgm.gui.button.Button`
- Axis: Either 'x' or 'y'
- AnchorX: Dynamic or static anchor on x-axis
- AnchorY: Dynamic or static anchor on y-axis
- Anchor: (AnchorX, AnchorY)
- Color: Enum that stores a bunch of preset colors. See `~pgm.types.Color`
- Eventhandler: Type for user-made event handlers
- YAMLDict: Type for parsed YAML files
- YAMLIterable: Type for iterable YAML values for custom parsing
- YAMLValidationMode: Types of validation currently supposed by custom YAML parser
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Callable, Literal

from pyglet.customtypes import AnchorX as _AnchorX
from pyglet.customtypes import AnchorY as _AnchorY

Point2D = tuple[float, float]
FontInfo = tuple[str | None, int | None]
ButtonStatus = Literal['Unpressed', 'Hover', 'Pressed']
Axis = Literal['x', 'y']
AnchorX = _AnchorX | float
AnchorY = _AnchorY | float
Anchor = tuple[AnchorX, AnchorY]
EventHandler = Callable[..., Any]
YAMLDict = dict[Any, Any] | None
YAMLIterable = dict | list  # type: ignore[type-arg]
YAMLValidationMode = Literal['Anim']


class Color(Enum):
	"""A bunch of colors in the form (int, int, int, int)."""

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
