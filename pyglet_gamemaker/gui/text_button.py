from __future__ import annotations

from typing import TYPE_CHECKING

from ..types import *
from . import Button, Text, Widget

if TYPE_CHECKING:
	from pyglet.graphics import Batch, Group
	from pyglet.window import Window

	from ..sprite import SpriteSheet


class TextButton(Widget):
	"""Both a 2D button and 2D text in one. Refer to `gui.Button` and `gui.Text`.

	Dispatches: Refer to `gui.Button`.

	Note: `.text` holds Text object, `.button` holds Button object

	Use kwargs to attach event handlers.
	"""

	_hover_enlarge: int = 0

	window: Window
	"""Window button is associated with."""
	button: Button
	"""Button object"""
	text: Text
	"""Text object"""
	start_hover_enlarge: int
	"""Starting hover enlarge value"""

	_enlarged: bool = False
	"""If true, text is currently enlarged. Used internally to enlarge text once."""

	def __init__(
		self,
		ID: str,
		text: str,
		x: float,
		y: float,
		window: Window,
		batch: Batch,
		button_group: Group,
		text_group: Group,
		image_sheet: SpriteSheet,
		image_start: str | int,
		button_anchor: Anchor = (0, 0),
		text_anchor: Anchor = (0, 0),
		font_info: FontInfo = (None, None),
		color: Color = Color.WHITE,
		hover_enlarge: int = 0,
		dispatch: bool = True,
		**kwargs,
	) -> None:
		"""Create a button with text.

		Args:
			ID (str):
				Name/ID of widget
			text (str):
				Label text
			x (float):
				Anchored x position of button
			y (float):
				Anchored y position of button
			window (Window):
				Window for attaching self
			batch (Batch):
				Batch for rendering
			group (Group):
				Group for rendering
			image_sheet (SpriteSheet):
				SpriteSheet with the button images
			image_start (str | int):
				The starting index of the button images
			button_anchor (Anchor, optional):
				Anchor position for the button. See `gui.Button` for more info on anchor values.
				Defaults to (0, 0).
			text_anchor (Anchor, optional):
				Anchor position for the text. See `gui.Text` for more info on anchor values.
				Defaults to (0, 0).
			font_info (FontInfo, optional):
				Font name and size.
				Defaults to (None, None).
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
			hover_enlarge (int, optional):
				How much to enlarge text when hovered over.
				Defaults to 0.
			dispatch (bool, optional):
				If False, don't dispatch events to handlers. See `gui.Button` for more info.
				Defaults to True.

			**kwargs:
				Any event handlers to attach (such as 'on_full_click')
		"""
		self.button = Button(
			ID,
			x,
			y,
			image_sheet,
			image_start,
			window,
			batch,
			button_group,
			button_anchor,
			dispatch=dispatch,
			attach_events=False,
			**kwargs,
		)
		self.start_hover_enlarge = self.hover_enlarge = hover_enlarge

		self.text = Text(
			text,
			x,
			y,
			batch,
			text_group,
			text_anchor,
			font_info,
			color,
		)

		self.window = window
		# Adds event handler for mouse events
		self.window.push_handlers(
			on_mouse_press=self._on_mouse_press,
			on_mouse_release=self._on_mouse_release,
			on_mouse_motion=self._on_mouse_motion,
			on_mouse_drag=self._on_mouse_drag,
		)

	def reset(self) -> None:
		self.text.reset()
		self.button.reset()
		self.hover_enlarge = self.start_hover_enlarge
		# Sync status
		self._on_mouse_motion(*self.button._last_mouse_pos, 0, 0)

	def _calc_anchor(self) -> None:
		self.button._calc_anchor()

	def _enlarge(self) -> None:
		"""Enlarge the text based on button status"""
		if self.button.status == 'Hover':
			# First frame hover: enlarge text
			if not self._enlarged:
				self._enlarged = True
				prev = self.text.width, self.text.height
				self.text.font_size += self._hover_enlarge
				self._sync_text_anchor(prev)
		else:
			# First frame unhover: unenlarge text
			if self._enlarged:
				self._enlarged = False
				prev = self.text.width, self.text.height
				self.text.font_size -= self._hover_enlarge
				self._sync_text_anchor(prev)

	def _sync_text_anchor(self, prev: tuple[int, int]) -> None:
		"""Sync anchor of text widget using dimensions before resize.

		Args:
			prev (tuple[int, int]):
				The previous dimensions before resizing text
		"""
		# Only sync if dynamic anchor
		# Use _anchor to circumvent auto setting of raw_anchor to static

		if isinstance(self.text.raw_anchor[0], str):
			self.text._anchor = (
				self.text.anchor_x + (self.text.width - prev[0]) / 2,
				self.text.anchor_y,
			)
			# Refresh position
			self.button.pos = self.button.pos
			self.text.pos = self.text.pos

		if isinstance(self.text.raw_anchor[1], str):
			self.text._anchor = (
				self.text.anchor_x,
				self.text.anchor_y + (self.text.height - prev[1]) / 2,
			)
			# Refresh position
			self.button.pos = self.button.pos
			self.text.pos = self.text.pos

	def _on_mouse_press(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.button.enabled:
			return
		self.button._on_mouse_press(x, y, buttons, modifiers)
		self._enlarge()

	def _on_mouse_motion(self, x: int, y: int, dx: int, dy: int) -> None:
		if not self.button.enabled:
			return
		self.button._on_mouse_motion(x, y, dx, dy)
		self._enlarge()

	def _on_mouse_release(self, x: int, y: int, buttons: int, modifiers: int) -> None:
		if not self.button.enabled:
			return
		self.button._on_mouse_release(x, y, buttons, modifiers)
		self._enlarge()

	def _on_mouse_drag(
		self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int
	) -> None:
		if not self.button.enabled:
			return
		self.button._on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._enlarge()

	def enable(self) -> None:
		self.button.enable()

	def disable(self) -> None:
		self.button.disable()

	@property
	def x(self) -> float:
		"""The x position of the anchor point. Setting sets text AND button.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.button.x

	@x.setter
	def x(self, val: float) -> None:
		self.button.x = self.text.x = val
		self._enlarge()

	@property
	def y(self) -> float:
		"""The y position of the anchor point. Setting sets text AND button.

		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.button.y

	@y.setter
	def y(self, val: float) -> None:
		self.button.y = self.text.y = val
		self._enlarge()

	@property
	def pos(self) -> Point2D:
		"""The x position of the anchor point. Setting sets text AND button."""
		return self.button.pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.button.pos = self.text.pos = val
		self._enlarge()

	@property
	def anchor_x(self) -> float:
		"""The x position of the button anchor point. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.button.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.button.anchor_x = val

		# Just overwrite anchor if dynamic
		# 	If static, use _anchor to circumvent auto setting of
		# 	possible dynamic raw_anchor to static
		if isinstance(val, str):
			self.text.anchor_x = val
		else:
			self.text._anchor = val, self.text.anchor_y

		# Subtract half of width diff between items (because text centered in button)
		# 	to correct for different sized text
		self.text._anchor = (
			self.text.anchor_x - (self.button.width - self.text.width) / 2,
			self.text.anchor_y,
		)
		# Refresh position
		self.pos = self.pos

		# * Do not call ._enlarge as refreshing position calls it already

	@property
	def anchor_y(self) -> float:
		"""The x position of the button anchor point. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)

		To set both `.anchor_x` and `.anchor_y`, use `.anchor`
		"""
		return self.button.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.button.anchor_y = val

		# Just overwrite anchor if dynamic
		# 	If static, use _anchor to circumvent auto setting of
		# 	possible dynamic raw_anchor to static
		if isinstance(val, str):
			self.text.anchor_y = val
		else:
			self.text._anchor = self.text.anchor_x, val

		# Subtract half of height diff between items (because text centered in button)
		# 	to correct for different sized text
		self.text._anchor = (
			self.text.anchor_x,
			self.text.anchor_y - (self.button.height - self.text.height) / 2,
		)
		# Refresh position
		self.pos = self.pos

		# * Do not call ._enlarge as refreshing position calls it already

	@property
	def anchor(self) -> Point2D:
		"""The anchor position of the button. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)
		"""
		return self.button.anchor

	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.anchor_x, self.anchor_y = val

	@property
	def status(self) -> ButtonStatus:
		return self.button.status

	@status.setter
	def status(self, val: ButtonStatus) -> None:
		self.button.status = val

	@property
	def hover_enlarge(self) -> int:
		"""How much to enlarge text when hovered over"""
		return self._hover_enlarge

	@hover_enlarge.setter
	def hover_enlarge(self, size: int) -> None:
		# If need to be resized and synced
		if self._enlarged:
			# Trick: Can unhover and rehover button to make changes automatically.
			# 	This way, no copy pasting code needed.
			# 	Because status is being manually set instead of in Button._update_status,
			# 	no dispatches are made.
			self.button.status = 'Unpressed'
			self._enlarge()
			self._hover_enlarge = size
			self.button.status = 'Hover'
			self._enlarge()

		else:
			self._hover_enlarge = size

	@property
	def enabled(self) -> bool:
		return self.button.enabled

	@property
	def dispatch(self) -> bool:
		return self.button.dispatch

	@dispatch.setter
	def dispatch(self, val: bool) -> None:
		self.button.dispatch = val

	@property
	def width(self) -> int:
		return self.button.width

	@property
	def height(self) -> int:
		return self.button.height
