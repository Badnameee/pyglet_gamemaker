from __future__ import annotations
from typing import TYPE_CHECKING

from ..types import *
from pyglet.text import Label
if TYPE_CHECKING:
	from pyglet.customtypes import AnchorX, AnchorY, HorizontalAlign
	from pyglet.graphics.shader import ShaderProgram
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group


class Text(Label):
	"""A label with extra functions, mainly offsetting for scrolling."""

	_text = ''

	def __init__(self,
			text: str = '',
			x: float = 0, y: float = 0,
			width: int | None = None, height: int | None = None,
			anchor: tuple[AnchorX, AnchorY] = ('center', 'baseline'), rotation: float = 0.0,
			multiline: bool = False, dpi: int | None = None,
			font_info: FontInfo = (None, None),
			weight: str = "normal", italic: bool | str = False, stretch: bool | str=False,
			color: Color = Color.WHITE,
			align: HorizontalAlign = "left",
			batch: Batch | None = None, group: Group | None = None, program: ShaderProgram | None = None
	) -> None:
		"""Create a text label

		Args:
			text (str, optional): Label text. Defaults to ''.
			x (float, optional): Anchored x position. Defaults to 0.
			y (float, optional): Anchored y position. Defaults to 0.
			width (int | None, optional): Width of label. Defaults to None.
			height (int | None, optional): Height of label. Defaults to None.
			anchor (tuple[AnchorX, AnchorY], optional): Anchor for both axes. Defaults to ('center', 'baseline').
			rotation (float, optional): Rotation of text. Defaults to 0.0.
			multiline (bool, optional): Whether text is multiline. Defaults to False.
			dpi (int | None, optional): DPI of text. Defaults to None.
			font_info (FontInfo, optional): Font name and size. Defaults to (None, None).
			weight (str, optional): Weight of text. Defaults to "normal".
			italic (bool | str, optional): Whether to italicize text. Defaults to False.
			stretch (bool | str, optional): Whether to stretch text.. Defaults to False.
			color (Color, optional): Color of text. Defaults to Color.WHITE.
			align (HorizontalAlign, optional): x alignment of text. Defaults to "left".
			batch (Batch | None, optional): Batch for rendering. Defaults to None.
			group (Group | None, optional): Group for rendering. Defaults to None.
			program (ShaderProgram | None, optional): Shader for rendering. Defaults to None.
		"""

		super().__init__(
			text, x, y, 0,
			width, height, *anchor, rotation,
			multiline, dpi,
			*font_info,
			weight, italic, stretch,
			color.value,
			align, # type: ignore[arg-type]
			batch, group, program
		)

		self.start_pos = x, y
		self.font_info = font_info
		self.text = text

	@classmethod
	def from_scale[T: Text](cls: type[T],
			scale: tuple[float, float],
			window: Window,
			text: str = '',
			width: int | None = None, height: int | None = None,
			anchor: tuple[AnchorX, AnchorY] = ('center', 'baseline'), rotation: float = 0.0,
			multiline: bool = False, dpi: int | None = None,
			font_info: FontInfo = (None, None),
			weight: str = "normal", italic: bool | str = False, stretch: bool | str=False,
			color: Color = Color.WHITE,
			align: HorizontalAlign = "left",
			batch: Batch | None = None, group: Group | None = None, program: ShaderProgram | None = None
	) -> T:
		"""Create a button with text

		Args:
			scale (tuple[float, float]): The (x, y) scale for label
			window (Window): Window for scaling
			text (str, optional): Label text. Defaults to ''.
			x (float, optional): Anchored x position. Defaults to 0.
			y (float, optional): Anchored y position. Defaults to 0.
			width (int | None, optional): Width of label. Defaults to None.
			height (int | None, optional): Height of label. Defaults to None.
			anchor (tuple[AnchorX, AnchorY], optional): Anchor for both axes. Defaults to ('center', 'baseline').
			rotation (float, optional): Rotation of text. Defaults to 0.0.
			multiline (bool, optional): Whether text is multiline. Defaults to False.
			dpi (int | None, optional): DPI of text. Defaults to None.
			font_info (FontInfo, optional): Font name and size. Defaults to (None, None).
			weight (str, optional): Weight of text. Defaults to "normal".
			italic (bool | str, optional): Whether to italicize text. Defaults to False.
			stretch (bool | str, optional): Whether to stretch text.. Defaults to False.
			color (Color, optional): Color of text. Defaults to Color.WHITE.
			align (HorizontalAlign, optional): x alignment of text. Defaults to "left".
			batch (Batch | None, optional): Batch for rendering. Defaults to None.
			group (Group | None, optional): Group for rendering. Defaults to None.
			program (ShaderProgram | None, optional): Shader for rendering. Defaults to None.
			hover_enlarge (int, optional): How much to enlarge text when hovered over. Defaults to 0.
		"""
		return cls(
			text, scale[0] * window.width, scale[1] * window.height,
			width, height, anchor, rotation,
			multiline, dpi,
			font_info,
			weight, italic, stretch,
			color,
			align, # type: ignore[arg-type]
			batch, group, program
		)

	def offset(self, val: Point2D) -> None:
		"""Add from current offset of the text by an amount."""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:
		"""Set offset of the text to an amount."""
		self.x, self.y = self.start_pos[0] + val[0], self.start_pos[1] + val[1]

	def reset(self) -> None:
		"""Reset text to creation state"""
		self.x, self.y = self.start_pos
		self.font_name, self.font_size = self.font_info # type: ignore[assignment]

	@property
	def text(self) -> str:
		"""The text string"""
		return self._text
	@text.setter
	def text(self, txt: str | int) -> None:
		self.document.text = self._text = str(txt)

	@property
	def pos(self) -> Point2D:
		"""The position, anchored"""
		return self.position[0], self.position[1]
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.position = *val, self.position[2]
