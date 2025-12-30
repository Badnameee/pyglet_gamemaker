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
		'left': 0,
		'bottom': 0,
		'center': 0.5,
		'right': 1,
		'top': 1,
	}
	"""Converts dynamic anchor to multiplier"""

	_anchor_pos: Point2D = 0, 0

	unpressed_img: AbstractImage
	"""Image of unpressed button"""
	hover_img: AbstractImage
	"""Image of hovered button"""
	pressed_img: AbstractImage
	"""Image of pressed button"""
	ID: str
	"""Identifier of button"""
	window: Window
	"""Window button is associated with"""
	status: ButtonStatus
	"""Status of button"""
	dispatch: bool
	"""if False, don't dispatch event handlers"""

	_last_mouse_pos: Point2D = 0, 0
	"""Holds the last mouse position registered by button"""
	raw_anchor: Anchor = 0, 0
	"""Holds the raw anchor position (static + dynamic)"""

	def __init__(
		self,
		ID: str,
		x: float,
		y: float,
		image_sheet: SpriteSheet,
		image_start: str | int,
		window: Window,
		batch: Batch,
		group: Group,
		anchor: Anchor = (0, 0),
		*,
		dispatch: bool = True,
		**kwargs,
	) -> None:
		"""Create a button.

		Args:
			ID (str):
				Name/ID of widget
			x (float):
				Anchored x position of button
			y (float):
				Anchored y position of button
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
			anchor (Anchor):
				Anchor position. See `gui.Button` for more info on anchor values.
				Defaults to (0, 0).
			dispatch (bool, optional):
				If False, don't dispatch event handlers. See `gui.Button` for more info.
				Defaults to True.
			kwargs:
				Event handlers (name=func)
		"""

		# Extract images from sheet
		self._parse_sheet(image_sheet, image_start)

		super().__init__(
			x,  # type: ignore[arg-type]
			y,  # type: ignore[arg-type]
			self.pressed_img,
			self.unpressed_img,
			self.hover_img,
			batch,
			group,
		)

		self.start_pos = x, y
		self.anchor_pos = anchor
		self.dispatch = dispatch

		self.ID = ID
		self.window = window
		self.status = 'Unpressed'

		# Adds event handler for mouse events
		self.window.push_handlers(self)
		# Adds any event handlers passed through kwargs
		for name in kwargs:
			self.register_event_type(name)
		self.push_handlers(**kwargs)

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

	def update_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Update the sheet of the button"""
		self._parse_sheet(image_sheet, image_start)
		self._calc_anchor_pos(self.raw_anchor)

	def _parse_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Parse a sheet into individual images and store them"""
		start = (
			image_sheet.lookup[image_start]
			if isinstance(image_start, str)
			else image_start
		)
		self.unpressed_img, self.hover_img, self.pressed_img = image_sheet[
			start : start + 3
		]  # type: ignore[misc]

	def _update_status(self, x: int, y: int) -> None:
		"""Update the status of the button given mouse position"""
		if self.value:
			if self.dispatch and self.status != 'Pressed':
				self.dispatch_event('on_half_click', self)
			self.status = 'Pressed'
		elif self._check_hit(x, y):
			if self.dispatch and self.status == 'Pressed':
				self.dispatch_event('on_full_click', self)
			self.status = 'Hover'
		else:
			self.status = 'Unpressed'

	def _calc_anchor_pos(self, val: Anchor) -> None:
		"""Calculate a new anchor position and sync position"""
		prev_pos = self.pos
		self.raw_anchor = val
		self._anchor_pos = (
			(
				self.CONVERT_DYNAMIC[val[0]] * self.hover_img.width
				if isinstance(val[0], str)
				else val[0]
			),
			(
				self.CONVERT_DYNAMIC[val[1]] * self.hover_img.height
				if isinstance(val[1], str)
				else val[1]
			),
		)
		# Refresh position
		self.pos = prev_pos

	def on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

	def on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

	def on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

	def enable(self) -> None:
		self.enabled = True

	def disable(self) -> None:
		self.enabled = False

	@property  # type: ignore[override]
	def x(self) -> float:
		"""The x position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._x + self._anchor_pos[0]

	@x.setter
	def x(self, val: float) -> None:
		_PushButton.x.fset(self, val - self._anchor_pos[0])  # type: ignore[attr-defined]
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0)  # type: ignore[arg-type]

	@property  # type: ignore[override]
	def y(self) -> float:
		"""The y position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._y + self._anchor_pos[1]

	@y.setter
	def y(self, val: float) -> None:
		_PushButton.y.fset(self, val - self._anchor_pos[1])  # type: ignore[attr-defined]
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0)  # type: ignore[arg-type]

	@property
	def pos(self) -> Point2D:
		"""The anchor position."""
		return self._x + self._anchor_pos[0], self._y + self._anchor_pos[1]

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.position = val[0] - self._anchor_pos[0], val[1] - self._anchor_pos[1]  # type: ignore[assignment] # bro widget can take float
		# Sync status
		self.on_mouse_motion(*self._last_mouse_pos, 0, 0)  # type: ignore[arg-type]

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the button, in px.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor_pos[0]

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self._calc_anchor_pos((val, self._anchor_pos[1]))

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the button, in px.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor_pos[1]

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self._calc_anchor_pos((self._anchor_pos[0], val))

	@property
	def anchor_pos(self) -> Point2D:
		"""The anchor of the button, in px.

		Can be set in px or dynamic.
		"""
		return self._anchor_pos

	@anchor_pos.setter
	def anchor_pos(self, val: Anchor) -> None:
		self._calc_anchor_pos(val)

	@property
	def width(self) -> int:
		return self.hover_img.width

	@property
	def height(self) -> int:
		return self.hover_img.height
