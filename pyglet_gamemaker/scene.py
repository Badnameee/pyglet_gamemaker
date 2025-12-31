from abc import ABC, abstractmethod
from typing import Callable

from pyglet.window import Window
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch, Group
from .types import *
from .sprite import SpriteSheet
from .shapes import Rect
from .gui import *


class Scene(ABC, EventDispatcher):
	"""Abstract class for a Scene in the game, inherit to create own scenes.
	`Window` object should hold all scenes in window.scenes dictionary.

	Required Methods (**do not override `.__init__`**):
	- `.initialize()`: The initializer that runs when adding scene to window
	- `.enable()`: Enable scene (not rendering, just logic)
	- `.disable()`: Disable scene (not rendering, just logic)

	Constants to set:
	- `.WIDGET_POS`: Positions of widgets as scale to window (see `Scene.WIDGET_POS`)
	- `.default_font_info`: The default font information used if none passed into methods

	Creates its own batch and groups:
	- `.batch`
	- `.main_group` - For everything not UI
		- `.bg_group`
		- Create subgroups
	- `.UI_group` - For all UI
		- `.button_group`
		- `.text_group`

	Dispatches:
	- 'on_scene_change' (to window) when program wishes to switch scenes.
		- Arg: Name of new scene to switch to

	Use kwargs to attach event handlers.
	"""

	WIDGET_POS: dict[str, tuple[float, float]]
	"""Stores the position of every widget as a scale {id: (scale_x, scale_y)}.

	Ex. `'Test': (0.5, 0.5)` is the center of the window.
	"""
	default_font_info: FontInfo = None, None
	"""The default font info is none is passed to gui methods"""

	name: str
	"""The name of the scene"""
	event_handlers: dict[str, Callable]
	"""All manually attached event handlers for this scene.
	
	**Do not modify**; use `.add_event_handlers` and `.remove_event_handlers` instead.
	"""
	window: Window
	"""Window scene is a part of"""
	batch: Batch
	"""Batch scene is drawn on"""
	main_group: Group
	"""Rendering group for everything not UI"""
	bg_group: Group
	"""Rendering subgroup for the background"""
	UI_group: Group
	"""Rendering group for all UI"""
	button_group: Group
	"""Rendering subgroup for the buttons"""
	text_group: Group
	"""Rendering subgroup for the text"""
	widgets: dict[str, Text | Button | TextButton]
	"""Stores all widgets in the menu"""

	def __init__(self, name: str, **kwargs) -> None:
		"""Create a scene.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
			**kwargs:
				Event handlers to attach (name=func)
		"""
		self.name = name
		self.event_handlers = {}
		self.widgets = {}

		self.batch = Batch()
		self.main_group = Group(0)
		self.bg_group = Group(0, self.main_group)
		self.UI_group = Group(1)
		self.button_group = Group(0, self.UI_group)
		self.text_group = Group(1, self.UI_group)

		# Adds any event handlers passed through kwargs
		self.add_event_handlers(**kwargs)

	def set_window(self, window: Window) -> None:
		"""Set the window the Scene will use.

		Args:
			window (Window):
				The screen window
		"""
		self.window = window
		self.initialize()

	def add_event_handlers(self, **kwargs: Callable) -> None:
		"""Add event handlers to this scene.

		Args:
			**kwargs (Callable):
				Name-function pair(s) representing handlers
		"""
		for name, handler in kwargs.items():
			self.event_handlers[name] = handler
			self.register_event_type(name)
		self.push_handlers(**kwargs)

	def remove_event_handlers(self, *args: str) -> None:
		"""Remove event handlers from this scene.

		Args:
			*args (name):
				Names of handler(s) to remove
		"""
		for name in args:
			self.remove_handler(name, self.event_handlers.pop(name))

	def create_bg(self, color: Color) -> Rect:
		"""Create a solid background for the menu.

		Args:
			color (Color):
				The color of the background.

		Returns:
			Rect: The bg
		"""
		return Rect(
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
			widget_name,
			self.WIDGET_POS[widget_name][0] * self.window.width,
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
	def initialize(self) -> None:
		"""Initialize the scene."""

	@abstractmethod
	def enable(self) -> None:
		"""Enables this scene. (does not enable rendering)"""

	@abstractmethod
	def disable(self) -> None:
		"""Disables this scene. (does not disable rendering)"""
