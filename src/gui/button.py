from __future__ import annotations
from typing import TYPE_CHECKING
from ..types import *

from pyglet.gui import PushButton as _PushButton
if TYPE_CHECKING:
	from pyglet.image import AbstractImage
	from pyglet.customtypes import AnchorX, AnchorY
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group
	from ..sprite import SpriteSheet


class Button(_PushButton):
	"""A basic 2D button.
	
	Takes images for all 3 states ('Unpressed', 'Hover', 'Pressed').

	Dispatches:
	- 'on_half_click' when pressed
	- 'on_full_click' when pressed and released without mouse moving off.
	
	Use kwargs to attach event handlers.
	"""

	ANCHOR_TYPE_TO_FACTOR: dict[AnchorX | AnchorY, float] = {
		'left': 0, 'bottom': 0,
		'center': 0.5,
		'right': 1, 'top': 1,
	}
	"""Converts anchor type to multiplier"""

	unpressed_img: AbstractImage
	hover_img: AbstractImage
	pressed_img: AbstractImage
	_anchor: tuple[AnchorX | float, AnchorY | float]
	anchor_pos: Point2D = 0, 0
	"""The raw anchor position. Do not set as it will desync with `.anchor`"""
	ID: int
	window: Window
	status: ButtonStatus
	
	def __init__(self,
			ID: str,
			x: float, y: float, anchor: tuple[AnchorX | float, AnchorY | float],
			image_sheet: SpriteSheet, image_start: str | int,
			window: Window, batch: Batch | None, group: Group | None,
			**kwargs
	) -> None:
		"""Create a button.

		Args:
			ID (str): Name/ID of widget
			x (float): Anchored x position of button
			y (float): Anchored y position of button
			anchor (tuple[AnchorX | float, AnchorY | float]): Anchor for both axes.
				Float - static anchor, Anchor string - dynamic anchor
			image_sheet (SpriteSheet): SpriteSheet with the button images
			image_start (str | int): The starting index of the button images
			window (Window): Window for attaching self
			batch (Batch): Batch for rendering
			group (Group): Group for rendering
		"""
		
		# Extract images from sheet
		start = image_sheet.lookup[image_start] if isinstance(image_start, str) else image_start
		self.unpressed_img, self.hover_img, self.pressed_img = image_sheet[start:start + 3] # type: ignore[misc]

		super().__init__(
			x, y,
			self.pressed_img, self.unpressed_img, self.hover_img,
			batch, group
		) # type: ignore[arg-type]

		self.anchor = anchor

		self.ID = ID
		self.window = window
		self.status = 'Unpressed'
		
		# Adds event handler for mouse events
		self.window.push_handlers(self)
		# Adds any event handlers passed through kwargs
		for name in kwargs:
			self.register_event_type(name)
		self.push_handlers(**kwargs)
	
	def _update_status(self, x: int, y: int) -> None:
		"""Updates the status of the button given mouse position."""
		if self.value:
			if self.status != 'Pressed':
				self.dispatch_event('on_half_click', self)
			self.status = 'Pressed'
		elif self._check_hit(x, y):
			if self.status == 'Pressed':
				self.dispatch_event('on_full_click', self)
			self.status = 'Hover'
		else:
			self.status = 'Unpressed'

	def _calc_anchor_pos(self) -> None:
		prev_pos = self.pos
		self.anchor_pos = (
			(
				self.ANCHOR_TYPE_TO_FACTOR[self.anchor_x] * self.width
				if isinstance(self.anchor_x, str) else
				self.anchor_x
			),
			(
				self.ANCHOR_TYPE_TO_FACTOR[self.anchor_y] * self.height
				if isinstance(self.anchor_y, str) else
				self.anchor_y
			)
		)
		# Refresh position
		self.pos = prev_pos
	
	def on_mouse_press(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_motion(self,
			x: int, y: int,
			dx: int, dy: int
	) -> None:
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

	def on_mouse_release(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_drag(self,
			x: int, y: int, dx: int, dy: int,
			buttons: int, modifiers: int
	) -> None:
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

	def enable(self) -> None:
		self.enabled = True

	def disable(self) -> None:
		self.enabled = False

	@property # type: ignore[override]
	def x(self) -> float:
		"""Anchored x position"""
		return self._x + self.anchor_pos[0]
	@x.setter
	def x(self, val: float) -> None:
		_PushButton.x.fset(self, val - self.anchor_pos[0]) # type: ignore[attr-defined]

	@property # type: ignore[override]
	def y(self) -> float:
		"""Anchored y position"""
		return self._y + self.anchor_pos[1]
	@y.setter
	def y(self, val: float) -> None:
		_PushButton.y.fset(self, val - self.anchor_pos[1]) # type: ignore[attr-defined]

	@property
	def pos(self) -> Point2D:
		"""Anchored position"""
		return self.x, self.y
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.x, self.y = val

	@property
	def anchor_x(self) -> AnchorX | float:
		return self._anchor[0]
	@anchor_x.setter
	def anchor_x(self, val: AnchorX | float) -> None:
		self._anchor = val, self.anchor_y
		self._calc_anchor_pos()

	@property
	def anchor_y(self) -> AnchorY | float:
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

	@property
	def width(self) -> int:
		return self.hover_img.width

	@property
	def height(self) -> int:
		return self.hover_img.height
