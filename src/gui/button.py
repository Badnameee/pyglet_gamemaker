from __future__ import annotations
from typing import TYPE_CHECKING
from ..types import *

from pyglet.gui import PushButton as _PushButton
if TYPE_CHECKING:
	from pyglet.image import AbstractImage
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group
	from ..sprite import SpriteSheet


class Button(_PushButton):
	"""A basic 2D button.
	Supports anchoring with specific pixel values or dynamic.
	
	Dynamic Anchors:
	- `AnchorX`: 'left', 'center', 'right'
	- `AnchorY`: 'bottom', 'center', 'top'
	
	Takes a sprite sheet (using `sprite.Spritesheet`) to render the button.
	Button has three status: 'unpressed', 'hover', 'pressed'.
	Sprite sheet must have images in a row for all of the statuses in this order.

	Dispatches:
	- 'on_half_click' when pressed
	- 'on_full_click' when pressed and released without mouse moving off.
	
	Use kwargs to attach event handlers.
	"""

	CONVERT_DYNAMIC: dict[AnchorX | AnchorY, float] = {
		'left': 0, 'bottom': 0,
		'center': 0.5,
		'right': 1, 'top': 1,
	}
	"""Converts dynamic anchor to multiplier"""

	unpressed_img: AbstractImage
	hover_img: AbstractImage
	pressed_img: AbstractImage
	_anchor: Point2D = 0, 0
	ID: str
	window: Window
	status: ButtonStatus

	_last_mouse_pos: Point2D = 0, 0
	
	def __init__(self,
			ID: str,
			x: float, y: float, anchor: Anchor,
			image_sheet: SpriteSheet, image_start: str | int,
			window: Window, batch: Batch, group: Group,
			*, attach_events: bool=True,
			**kwargs
	) -> None:
		"""Create a button.

		Args:
			ID (str):
				Name/ID of widget
			x (float):
				Anchored x position of button
			y (float):
				Anchored y position of button
			anchor (Anchor):
				Anchor position. See `gui.Button` for more info on anchor values. Defaults to (0, 0).
			image_sheet (SpriteSheet):
				SpriteSheet with the button images
			image_start (str | int):
				The starting index of the button images
			window (Window):
				Window for attaching self
			batch (Batch):
				Batch for rendering
			group (Group):
				Group for rendering
			attach_events (bool, optional):
				If False, don't push mouse event handlers to window
			kwargs: Event handlers (name=func)
		"""
		
		# Extract images from sheet
		start = image_sheet.lookup[image_start] if isinstance(image_start, str) else image_start
		self.unpressed_img, self.hover_img, self.pressed_img = image_sheet[start:start + 3] # type: ignore[misc]

		super().__init__(
			x, y,													# type: ignore[arg-type]
			self.pressed_img, self.unpressed_img, self.hover_img,
			batch, group
		)

		self.anchor = anchor

		self.ID = ID
		self.window = window
		self.status = 'Unpressed'
		
		# Adds event handler for mouse events
		if attach_events:
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

	def _calc_anchor_pos(self, val: Anchor) -> None:
		"""Calculate a new anchor position and sync position."""
		prev_pos = self.pos
		self._anchor = (
			(
				self.CONVERT_DYNAMIC[val[0]] * self.hover_img.width
				if isinstance(val[0], str) else
				val[0]
			),
			(
				self.CONVERT_DYNAMIC[val[1]] * self.hover_img.height
				if isinstance(val[1], str) else
				val[1]
			)
		)
		# Refresh position
		self.pos = prev_pos
	
	def on_mouse_press(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		self._last_mouse_pos = x, y
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_motion(self,
			x: int, y: int,
			dx: int, dy: int
	) -> None:
		self._last_mouse_pos = x, y
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

	def on_mouse_release(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		self._last_mouse_pos = x, y
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_drag(self,
			x: int, y: int, dx: int, dy: int,
			buttons: int, modifiers: int
	) -> None:
		self._last_mouse_pos = x, y
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

	def enable(self) -> None:
		self.enabled = True

	def disable(self) -> None:
		self.enabled = False

	@property # type: ignore[override]
	def x(self) -> float:
		"""Anchored x position"""
		return self._x + self._anchor[0]
	@x.setter
	def x(self, val: float) -> None:
		_PushButton.x.fset(self, val - self._anchor[0]) # type: ignore[attr-defined]
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0) # type: ignore[arg-type]

	@property # type: ignore[override]
	def y(self) -> float:
		"""Anchored y position"""
		return self._y + self._anchor[1]
	@y.setter
	def y(self, val: float) -> None:
		_PushButton.y.fset(self, val - self._anchor[1]) # type: ignore[attr-defined]
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0) # type: ignore[arg-type]

	@property
	def pos(self) -> Point2D:
		"""Anchored position"""
		return self._x + self._anchor[0], self._y + self._anchor[1]
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.position = val[0] - self._anchor[0], val[1] - self._anchor[1] # type: ignore[assignment] # bro widget can take float
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0) # type: ignore[arg-type]

	@property
	def anchor_x(self) -> float:
		"""The unconverted x anchor of the button.

		Can be set in px or dynamic.
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self._anchor[0]
	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self._calc_anchor_pos((val, self._anchor[1]))

	@property
	def anchor_y(self) -> float:
		"""The unconverted y anchor of the button.

		Can be set in px or dynamic.
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self._anchor[1]
	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self._calc_anchor_pos((self._anchor[0], val))

	@property
	def anchor(self) -> Point2D:
		"""The unconverted anchor of the button.
		
		Can be set in px or dynamic.
		"""
		return self._anchor
	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self._calc_anchor_pos(val)

	@property
	def width(self) -> int:
		return self.hover_img.width

	@property
	def height(self) -> int:
		return self.hover_img.height
