from __future__ import annotations
from typing import TYPE_CHECKING

from ..types import *
from pyglet.text import Label
if TYPE_CHECKING:
	from pyglet.customtypes import AnchorX, AnchorY
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group


class Text(Label):
	"""A 2D label with extra functions, mainly offsetting for scrolling.
	
	Use kwargs to attach event handlers.
	"""

	_text = ''

	def __init__(self,
			text: str,
			x: float, y: float,
			batch: Batch, group: Group,
			anchor: tuple[AnchorX, AnchorY] = ('center', 'baseline'),
			font_info: FontInfo = (None, None),
			color: Color = Color.WHITE,
	) -> None:
		"""Create a text label.

		Args:
			text (str): Label text
			x (float): Anchored x position. Defaults to 0
			y (float): Anchored y position. Defaults to 0
			batch (Batch): Batch for rendering
			group (Group): Group for rendering
			anchor (tuple[AnchorX, AnchorY], optional): Anchor for both axes. Defaults to ('center', 'baseline').
			font_info (FontInfo, optional): Font name and size. Defaults to (None, None).
			color (Color, optional): Color of text. Defaults to Color.WHITE.
		"""

		super().__init__(
			text, x, y, 0,
			anchor_x=anchor[0], anchor_y=anchor[1],
			font_name=font_info[0], font_size=font_info[1],
			color=color.value,
			batch=batch, group=group
		)

		self.start_pos = x, y
		self.font_info = font_info
		self.text = text

	def offset(self, val: Point2D) -> None:
		"""Add from current offset of the text by an amount."""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:
		"""Set offset of the text to an amount."""
		self.x, self.y = self.start_pos[0] + val[0], self.start_pos[1] + val[1]

	def reset(self) -> None:
		"""Reset text to initial state"""
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
