from __future__ import annotations
from typing import TYPE_CHECKING

from pyglet.gui import PushButton as _PushButton
from ..types import *
if TYPE_CHECKING:
	from pyglet.customtypes import AnchorX, AnchorY
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group
	from ..sprite import SpriteSheet


class Button(_PushButton):
	"""A basic button.
	
	Takes images for all 3 states ('Unpressed', 'Hover', 'Pressed').

	Dispatches 'on_half_click' when pressed, and 'on_full_click' when pressed and released without mouse moving off.

	Use kwargs to attach event handlers.
	"""

	# Converts anchor type to multiplier
	ANCHOR_TYPE_TO_FACTOR: dict[AnchorX | AnchorY, float] = {
		'left': 0, 'bottom': 0,
		'center': 0.5,
		'right': 1, 'top': 1,
	}
	
	def __init__(self,
			ID: str,
			x: float, y: float, anchor: tuple[AnchorX, AnchorY],
			image_sheet: SpriteSheet, image_start: str | int,
			window: Window, batch: Batch, group: Group,
			**kwargs
	) -> None:
		"""Create a button.

		Args:
			ID (str): Name/ID of widget
			x (float): Anchored x position of button
			y (float): Anchored y position of button
			anchor (tuple[AnchorX, AnchorY]): Anchor for both axes
			image_sheet (SpriteSheet): SpriteSheet with the button images
			image_start (str | int): The starting index of the button images
			window (Window): Window for attaching self
			batch (Batch): Batch for rendering
			group (Group): Group for rendering
		"""
		
		# Extract images from sheet
		start = image_sheet.lookup[image_start] if isinstance(image_start, str) else image_start
		self.unpressed_img, self.hover_img, self.pressed_img = image_sheet[start:start + 3] # type: ignore[misc]
		
		# Calculate anchor
		self.anchor = anchor
		self.anchor_pos: Point2D = (
			self.ANCHOR_TYPE_TO_FACTOR[anchor[0]] * self.pressed_img.width,
			self.ANCHOR_TYPE_TO_FACTOR[anchor[1]] * self.pressed_img.height
		)
		# Translate pos
		x -= self.anchor_pos[0]
		y -= self.anchor_pos[1]

		super().__init__(x, y, self.pressed_img, self.unpressed_img, self.hover_img, batch, group) # type: ignore[arg-type]
		self.window = window

		# ID for event dispatch recievers to identify button
		self.ID = ID

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
	
	def on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

	def on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int) -> None:
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

	def enable(self) -> None:
		self.enabled = True

	def disable(self) -> None:
		self.enabled = False

	@property
	def pos(self) -> Point2D:
		"""The anchored position of the button."""
		return self.x + self.anchor_pos[0], self.y + self.anchor_pos[1]
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.x = val[0] - self.anchor_pos[0] # type: ignore[assignment]
		self.y = val[1] - self.anchor_pos[1] # type: ignore[assignment]
