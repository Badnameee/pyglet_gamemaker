from __future__ import annotations
from typing import TYPE_CHECKING

from ..types import *
from .text import Text
from .button import Button
if TYPE_CHECKING:
	from pyglet.window import Window
	from pyglet.graphics import Batch, Group
	from ..sprite import SpriteSheet


class TextButton:
	"""Both a 2D button and 2D text in one. Refer to `gui.Button` and `gui.Text`.

	Dispatches: Refer to `gui.Button`.

	Note: `.text` holds Text object, `.button` holds Button object
	
	Use kwargs to attach event handlers.
	"""

	_hover_enlarge = 0

	window: Window
	"""Window button is associated with."""
	button: Button
	"""Button object"""
	text: Text
	"""Text object"""
	_enlarged: bool = False
	"""If true, text is currently enlarged. Used internally to enlarge text once."""

	def __init__(self,
			ID: str,
			text: str,
			x: float, y: float,
			window: Window, batch: Batch, button_group: Group, text_group: Group,
			image_sheet: SpriteSheet, image_start: str | int,
			button_anchor: Anchor=(0, 0),
			text_anchor: Anchor=(0, 0),
			font_info: FontInfo=(None, None),
			color: Color=Color.WHITE,
			hover_enlarge: int=0, **kwargs
	) -> None:
		"""Create a button with text

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

			**kwargs:
				Any event handlers to attach (such as 'on_full_click')
		"""

		self.button = Button(
			ID, x, y,
			image_sheet, image_start,
			window, batch, button_group,
			button_anchor,
			attach_events=False, **kwargs
		)
		self.hover_enlarge = hover_enlarge

		self.text = Text(
			text,
			x, y,
			batch, text_group,
			text_anchor,
			font_info,
			color,
		)

		self.window = window
		# Adds event handler for mouse events
		self.window.push_handlers(self)

	def _enlarge(self) -> None:
		"""Enlarge the text based on button status"""

		# Hovering
		if self.button.status == 'Hover':
			# First frame hover: enlarge text
			if not self._enlarged:
				self._enlarged = True

				#* Automatically centers text when enlarging
				# First get previous dimensions
				prev = self.text.content_width, self.text.content_height

				self.text.font_size += self.hover_enlarge

				# Use new dimensions to find difference to recenter
				#	Have to check if dynamic anchor first
				if isinstance(self.text.raw_anchor[0], str):
					# Store the previous dynamic anchor to set
					#	because adding to anchor x makes anchor static
					anchor = self.text.raw_anchor
					self.text.anchor_x += (self.text.content_width - prev[0]) / 2
					self.text.raw_anchor = anchor

				if isinstance(self.text.raw_anchor[1], str):
					# Store the previous dynamic anchor to set
					#	because adding to anchor x makes anchor static
					anchor = self.text.raw_anchor
					self.text.anchor_y += (self.text.content_height - prev[1]) / 2
					self.text.raw_anchor = anchor
		else:
			# First frame unhover: unenlarge text
			if self._enlarged:
				self._enlarged = False

				#* Automatically centers text when enlarging
				# First get previous dimensions
				prev = self.text.content_width, self.text.content_height

				self.text.font_size -= self.hover_enlarge

				# Use new dimensions to find difference to recenter
				if isinstance(self.text.raw_anchor[0], str):
					# Store the previous dynamic anchor to set
					#	because adding to anchor x makes anchor static
					anchor = self.text.raw_anchor
					self.text.anchor_x += (self.text.content_width - prev[0]) / 2
					self.text.raw_anchor = anchor
					
				if isinstance(self.text.raw_anchor[1], str):
					# Store the previous dynamic anchor to set
					#	because adding to anchor x makes anchor static
					anchor = self.text.raw_anchor
					self.text.anchor_y += (self.text.content_height - prev[1]) / 2
					self.text.raw_anchor = anchor

	def on_mouse_press(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		if not self.button.enabled:
			return
		self.button.on_mouse_press(x, y, buttons, modifiers)
		self._enlarge()

	def on_mouse_motion(self,
			x: int, y: int,
			dx: int, dy: int
	) -> None:
		if not self.button.enabled:
			return
		self.button.on_mouse_motion(x, y, dx, dy)
		self._enlarge()

	def on_mouse_release(self,
			x: int, y: int,
			buttons: int, modifiers: int
	) -> None:
		if not self.button.enabled:
			return
		self.button.on_mouse_release(x, y, buttons, modifiers)
		self._enlarge()

	def on_mouse_drag(self,
			x: int, y: int, dx: int, dy: int,
			buttons: int, modifiers: int
	) -> None:
		if not self.button.enabled:
			return
		self.button.on_mouse_drag(x, y, dx, dy, buttons, modifiers)
		self._enlarge()

	def enable(self) -> None:
		self.button.enable()

	def disable(self) -> None:
		self.button.disable()

	@property # type: ignore[override]
	def x(self) -> float:
		"""Anchored x position of the button. Setting sets text AND button."""
		return self.button._x + self.anchor[0]
	@x.setter
	def x(self, val: float) -> None:
		self.button.x = self.text.x = val
		self._enlarge()

	@property
	def y(self) -> float:
		"""Anchored y position of the button. Setting sets text AND button."""
		return self.button._y + self.anchor[1]
	@y.setter
	def y(self, val: float) -> None:
		self.button.y = self.text.y = val
		self._enlarge()

	@property
	def pos(self) -> Point2D:
		"""Anchored position of the button. Setting sets text AND button."""
		return self.button._x + self.anchor[0], self.button._y + self.anchor[1]
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.button.pos = self.text.pos = val
		self._enlarge()

	@property
	def anchor_x(self) -> float:
		"""The unconverted x anchor of the button. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self.button.anchor_x
	@anchor_x.setter
	def anchor_x(self, val: AnchorX) -> None:
		self.button.anchor_x = self.text.anchor_x = val
		# Subtract half of width diff between items (because text centered in button)
		#	to correct for different sized text
		self.text.anchor_x -= (self.button.width - self.text.content_width) / 2
		self._enlarge()

	@property
	def anchor_y(self) -> float:
		"""The unconverted y anchor of the button. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)
		
		To set both `.anchor_x` and `.anchor_y`, use `anchor =`
		"""
		return self.button.anchor_y
	@anchor_y.setter
	def anchor_y(self, val: AnchorY) -> None:
		self.button.anchor_y = self.text.anchor_y = val
		# Subtract half of height diff between items (because text centered in button)
		#	to correct for different sized text
		self.text.anchor_y -= (self.button.height - self.text.content_height) / 2
		self._enlarge()

	@property
	def anchor(self) -> Point2D:
		"""The unconverted anchor of the button. Setting sets text AND button.

		Can be set in px or dynamic (see `gui.Button` and `gui.Text`)
		"""
		return self.button.anchor
	@anchor.setter
	def anchor(self, val: Anchor) -> None:
		self.anchor_x, self.anchor_y = val
		self._enlarge()

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
			#* Trick: Can unhover and rehover button to make changes automatically.
			#	This way, no copy pasting code needed.
			#	Because status is being manually set instead of in Button._update_status,
			#	no dispatches are made.
			self.status = 'Unpressed'
			self._enlarge()
			self._hover_enlarge = size
			self.status = 'Hover'
			self._enlarge()

		else:
			self._hover_enlarge = size

	@property
	def enabled(self) -> bool:
		return self.button.enabled
