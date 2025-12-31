from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.gui import PushButton as _PushButton

from ..types import *
from . import Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group
	from pyglet.image import AbstractImage
	from pyglet.window import Window

	from ..sprite import SpriteSheet


class Button(Widget, _PushButton):
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

	_last_mouse_pos: tuple[int, int] = 0, 0
	"""Holds the last mouse position registered by button"""

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
		attach_events: bool = True,
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
				If False, don't dispatch events to handlers. See `gui.Button` for more info.
				Defaults to True.
			attach_events (bool, optional):
				If False, don't attach mouse events to window.
				Event handlers can still be manually invoked.
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
		self.start_anchor = self.anchor = anchor
		self.dispatch = dispatch
		self.attach_events = attach_events

		self.ID = ID
		self.window = window
		self.status = 'Unpressed'

		# Adds event handler for mouse events
		if attach_events:
			self.window.push_handlers(
				on_mouse_press = self._on_mouse_press,
				on_mouse_release = self._on_mouse_release,
				on_mouse_motion = self._on_mouse_motion,
				on_mouse_drag = self._on_mouse_drag,
			)
		# Adds any event handlers passed through kwargs
		for name in kwargs:
			self.register_event_type(name)
		self.push_handlers(**kwargs)

	def update_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Update the sheet of the button"""
		self._parse_sheet(image_sheet, image_start)
		self._calc_anchor()

	def _parse_sheet(self, image_sheet: SpriteSheet, image_start: str | int) -> None:
		"""Parse a sheet into individual images and store them"""
		start = (
			image_sheet.lookup[image_start]
			if isinstance(image_start, str) else
			image_start
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

	def _calc_anchor(self) -> None:
		prev_pos = self.pos
		self._anchor = (
			(
				self.CONVERT_DYNAMIC[self.raw_anchor[0]] * self.hover_img.width
				if isinstance(self.raw_anchor[0], str) else
				self.raw_anchor[0]
			),
			(
				self.CONVERT_DYNAMIC[self.raw_anchor[1]] * self.hover_img.height
				if isinstance(self.raw_anchor[1], str) else
				self.raw_anchor[1]
			),
		)
		# Refresh position
		self.pos = prev_pos

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_press(x, y, buttons, modifiers)
		self._update_status(x, y)

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_motion(x, y, dx, dy)
		self._update_status(x, y)

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_release(x, y, buttons, modifiers)
		self._update_status(x, y)

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> None:
		if not self.enabled:
			return
		self._last_mouse_pos = x, y
		super().on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._update_status(x, y)

	def enable(self) -> None:  # noqa: D102
		self.enabled = True

	def disable(self) -> None:  # noqa: D102
		self.enabled = False

	@property  # type: ignore[override]
	def x(self) -> float:
		"""The x position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._x + self._anchor[0]

	@x.setter
	def x(self, val: float) -> None:
		_PushButton.x.fset(self, val - self._anchor[0])  # type: ignore[attr-defined]
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property  # type: ignore[override]
	def y(self) -> float:
		"""The y position of the anchor point.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._y + self._anchor[1]

	@y.setter
	def y(self, val: float) -> None:
		_PushButton.y.fset(self, val - self._anchor[1])  # type: ignore[attr-defined]
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def pos(self) -> Point2D:
		"""The anchor position."""
		return self._x + self._anchor[0], self._y + self._anchor[1]

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.position = val[0] - self._anchor[0], val[1] - self._anchor[1]  # type: ignore[assignment] # bro widget can take float
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the button, in px.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor[0]

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.raw_anchor = val, self._anchor[1]
		self._calc_anchor()
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the button, in px.

		Can be set in px or dynamic.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor[1]

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.raw_anchor = self._anchor[0], val
		self._calc_anchor()
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def anchor(self) -> Point2D:
		"""The anchor of the button, in px.

		Can be set in px or dynamic.
		"""
		return self._anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.raw_anchor = val
		self._calc_anchor()
		# Sync status
		self._on_mouse_motion(*self._last_mouse_pos, 0, 0)

	@property
	def width(self) -> int:  # noqa: D102
		return self.hover_img.width

	@property
	def height(self) -> int:  # noqa: D102
		return self.hover_img.height
