from __future__ import annotations
from typing import TYPE_CHECKING

from ..types import *
from pyglet.text import Label
if TYPE_CHECKING:
	from pyglet.customtypes import AnchorX, AnchorY
	from pyglet.graphics import Batch, Group


class Text(Label):
	"""A 2D label with scrolling and custom anchor support.

	Supports anchoring with specific pixel values.

	Does not support rotating around anchor point (rotates about bottomleft)
	
	Use kwargs to attach event handlers.
	"""

	ANCHOR_TYPE_TO_FACTOR: dict[AnchorX | AnchorY, float] = {
		'left': 0, 'bottom': 0,
		'center': 0.5,
		'right': 1, 'top': 1,
	}
	"""Converts anchor type to multiplier"""

	_text: str = ''
	_pos: Point2D = 0, 0

	start_pos: Point2D
	"""Original (*unanchored* AND *unrotated*) position of text"""
	font_info: FontInfo
	"""(name, size)"""

	def __init__(self,
			text: str,
			x: float, y: float,
			batch: Batch, group: Group,
			anchor: tuple[AnchorX | float, AnchorY | float]=(0, 0),
			font_info: FontInfo=(None, None),
			color: Color=Color.WHITE,
	) -> None:
		"""Create a text label.

		Args:
			text (str): Label text
			x (float): Anchored x position
			y (float): Anchored y position
			batch (Batch): Batch for rendering
			group (Group): Group for rendering
			anchor (tuple[AnchorX | float, AnchorY | float], optional): Anchor for both axes.
				*Float* -- static anchor, *Anchor string* -- dynamic anchor.
				Defaults to (0, 0).
			font_info (FontInfo, optional): Font name and size.
				Defaults to (None, None).
			color (Color, optional): Color of text.
				Defaults to Color.WHITE.
		"""

		super().__init__(
			text, x, y, 0,
			font_name=font_info[0], font_size=font_info[1],
			color=color.value,
			batch=batch, group=group
		)

		self.anchor = anchor
		self.start_pos = self.pos = x, y
		self.font_info = font_info
		self.text = text

	def offset(self, val: Point2D) -> None:
		"""Add from current offset of the text by an amount"""
		self.x += val[0]
		self.y += val[1]

	def set_offset(self, val: Point2D) -> None:
		"""Set offset of the text to an amount"""
		self.pos = self.start_pos[0] + val[0], self.start_pos[1] + val[1]

	def reset(self) -> None:
		"""Reset text to initial state"""
		self.pos = self.start_pos
		self.font_name, self.font_size = self.font_info # type: ignore[assignment]

	def _calc_anchor_pos(self) -> None:
		self.anchor_pos = (
			(
				# Convert if AnchorX, else use raw int value
				self.ANCHOR_TYPE_TO_FACTOR[self._anchor[0]] * self.content_width
				if isinstance(self._anchor[0], str) else
				self._anchor[0]
			),
			(
				# Convert if AnchorY, else use raw int value
				self.ANCHOR_TYPE_TO_FACTOR[self._anchor[1]] * self.content_height
				if isinstance(self._anchor[1], str) else
				self._anchor[1]
			)
		)
		# Refresh position
		self.pos = self.pos

	@property
	def text(self) -> str:
		"""The text string"""
		return self._text
	@text.setter
	def text(self, txt: str | int) -> None:
		self.document.text = self._text = str(txt)

	@property
	def x(self) -> float:
		"""*Anchored*, but *unrotated* x position of text.
		
		To set both `.x` and `.y`, use `.pos =`
		"""
		return self.pos[0]
	@x.setter
	def x(self, val: float) -> None:
		self._pos = val, self._pos[1]
		self._set_x(val - self.anchor_pos[0])

	@property
	def y(self) -> float:
		"""*Anchored*, but *unrotated* y position of text.
		
		To set both `.x` and `.y`, use `.pos =`
		"""
		return self._pos[1]
	@y.setter
	def y(self, val: float) -> None:
		self._pos = self._pos[0], val
		self._set_y(val - self.anchor_pos[1])

	@property
	def pos(self) -> Point2D:
		"""The position, *Anchored*, but *unrotated*"""
		return self._pos
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self._pos = val
		self._set_position((
			val[0] - self.anchor_pos[0],
			val[1] - self.anchor_pos[1],
			self._z
		))

	@property
	def anchor_x(self) -> AnchorX | float:
		"""The unconverted x anchor of the button.
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self._anchor[0]
	@anchor_x.setter
	def anchor_x(self, val: AnchorX | float) -> None:
		self._anchor = val, self.anchor_y
		self._calc_anchor_pos()

	@property
	def anchor_y(self) -> AnchorY | float:
		"""The unconverted y anchor of the button.
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self._anchor[1]
	@anchor_y.setter
	def anchor_y(self, val: AnchorY | float) -> None:
		self._anchor = self.anchor_x, val
		self._calc_anchor_pos()

	@property
	def anchor(self) -> tuple[AnchorX | float, AnchorY | float]:
		"""The unconverted anchor of the button"""
		return self._anchor
	@anchor.setter
	def anchor(self, val: tuple[AnchorX | float, AnchorY | float]) -> None:
		self._anchor = val
		self._calc_anchor_pos()
