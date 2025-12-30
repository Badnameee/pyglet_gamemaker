from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from pyglet.window import Window
from pyglet.graphics import Group
from .scene import Scene
from .types import *
from .shapes import Rect
from .gui import *

if TYPE_CHECKING:
	from .sprite import SpriteSheet


class Menu(Scene, ABC):
	"""Abstract class for a Menu (a Scene with boilerplate). Inherit to create own menus.

	Required Methods:
	- `.create_widgets()`: To create all menu widgets and other logic (basically the init)
	- `.enable()`: Enables scene (not rendering, just logic)
	- `.disable()`: Disables scene (not rendering, just logic)

	Creates its own batch and groups:
	- `.batch`
	- `.bg_group`, `.button_group`, and `.text_group`

	`.default_font_info` stores default font info for widgets.

	Dispatches: Refer to `gui.Scene`
	"""

	WIDGET_POS: dict[str, tuple[float, float]]
	"""Stores the position of every widget as a scale {id: (scale_x, scale_y)}.

	Ex. `'Test': (0.5, 0.5)` is the center of the window.
	"""
	widgets: dict[str, Text | Button | TextButton]
	"""Stores all widgets in the menu"""

	bg_group: Group
	"""Rendering group for the background"""
	button_group: Group
	"""Rendering group for the buttons"""
	text_group: Group
	"""Rendering group for the text"""

	bg: Rect

	default_font_info: FontInfo = None, None
	"""The default font info is none is passed to gui functions"""

	def __init__(self, name: str, **kwargs) -> None:
		"""Create a menu.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
		"""

		super().__init__(name, **kwargs)

		self.widgets = {}

		self.bg_group = Group(0)
		self.button_group = Group(1)
		self.text_group = Group(2)

	def set_window(self, window: Window) -> None:
		super().set_window(window)
		self.create_widgets()

	@abstractmethod
	def create_widgets(self) -> None:
		"""Creates the widgets for the menu."""
	
	def create_bg(self, color: Color) -> None:
		"""Create a solid background for the menu.

		Args:
			color (Color):
				The color of the background.
		"""
		self.bg = Rect(
			0,
			0,
			self.window.width,
			self.window.height,
			color,
			self.batch,
			self.bg_group,
		)

	def create_text(
		self,
		widget_name: str,
		text: str,
		anchor_pos: Anchor = (0, 0),
		font_info: FontInfo = (None, None),
		color: Color = Color.WHITE,
	) -> None:
		"""Create a text widget.

		Args:
			widget_name (str):
				The name of the widget. Used as ID and to get position from widget_pos.
			text (str):
				Label text
			anchor_pos (Anchor, optional):
				Anchor position. See `gui.Text` for more info on anchor values.
				Defaults to (0, 0).
			font_info (FontInfo, optional):
				Font name and size.
				Defaults to value in `.default_font_info`.
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
		"""

		# Use default if none provided
		if font_info == (None, None):
			font_info = self.default_font_info

		self.widgets[widget_name] = text_obj = Text(
			text,
			self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.width,
			self.batch,
			self.text_group,
			anchor_pos,
			font_info,
			color,
		)
		text_obj.disable()

	def create_button(
		self,
		widget_name: str,
		image_sheet: SpriteSheet,
		image_start: str | int,
		anchor: Anchor = (0, 0),
		*,
		attach_events: bool = True,
		**kwargs,
	) -> None:
		"""Create a button widget.

		Args:
			widget_name (str):
				The name of the widget. Used as ID and to get position from widget_pos.
			image_sheet (SpriteSheet):
				SpriteSheet with the button images
			image_start (str | int):
				The starting index of the button images
			anchor (Anchor):
				Anchor position. See `gui.Button` for more info on anchor values.
				Defaults to (0, 0).
			attach_events (bool, optional):
				If False, don't push mouse event handlers to window.
				Defaults to True.
			kwargs:
				Event handlers (name=func)
		"""

		self.widgets[widget_name] = button = Button(
			widget_name, self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.height,
			image_sheet,
			image_start,
			self.window,
			self.batch,
			self.button_group,
			anchor,
			attach_events=attach_events,
			**kwargs,
		)
		button.disable()

	def create_text_button(
		self,
		widget_name: str,
		text: str,
		image_sheet: SpriteSheet,
		image_start: str | int,
		button_anchor: Anchor = (0, 0),
		text_anchor: Anchor = (0, 0),
		font_info: FontInfo = (None, None),
		color: Color = Color.WHITE,
		hover_enlarge: int = 0,
		attach_events: bool = True,
		**kwargs,
	) -> None:
		"""Create a text button widget.

		Args:
			widget_name (str):
				The name of the widget. Used as ID and to get position from widget_pos.
			text (str):
				Label text
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
				Defaults to value in `.default_font_info`.
			color (Color, optional):
				Color of text.
				Defaults to Color.WHITE.
			hover_enlarge (int, optional):
				How much to enlarge text when hovered over.
				Defaults to 0.
			attach_events (bool, optional):
				If False, don't push mouse event handlers to window.
				Defaults to True.
			kwargs:
				Event handlers (name=func)
		"""

		# Use default if none provided
		if font_info == (None, None):
			font_info = self.default_font_info

		self.widgets[widget_name] = text_button = TextButton(
			widget_name,
			text,
			self.WIDGET_POS[widget_name][0] * self.window.width,
			self.WIDGET_POS[widget_name][1] * self.window.width,
			self.window,
			self.batch,
			self.button_group,
			self.text_group,
			image_sheet,
			image_start,
			button_anchor,
			text_anchor,
			font_info,
			color,
			hover_enlarge,
			attach_events,
			**kwargs,
		)
		text_button.disable()

	@abstractmethod
	def enable(self) -> None: ...

	@abstractmethod
	def disable(self) -> None: ...
