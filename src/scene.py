from abc import ABC, abstractmethod
from typing import Callable

from pyglet.window import Window
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch


class Scene(ABC, EventDispatcher):
	"""Abstract class for a Scene in the game, inherit to create own scenes.
	`Window` object should hold all scenes in window.scenes dictionary.

	When inheriting, a batch must be created for automatic rendering.

	Dispatches:
	- 'on_scene_change' (to window) when program wishes to switch scenes.
		- Arg: Name of new scene to switch to

	`enable` and `disable` run from `Window` class when enabling and disabling scene.
	These enable and disable the scene, but not rendering. This happens in `Window`.

	Use kwargs to attach event handlers.
	"""

	event_handlers: dict[str, Callable]
	"""All manually attached event handlers for this scene.
	
	**Do not modify**; use `add_event_handlers` and `remove_event_handlers` instead.
	"""

	batch: Batch
	"""Batch scene is drawn on"""
	name: str
	"""The name of the scene"""
	window: Window
	"""Window scene is a part of"""

	def __init__(self, name: str, window: Window, **kwargs) -> None:
		"""Create a scene.

		Args:
			name (str):
				The name of the scene (used to identity scene by name)
			window (Window):
				The screen window
			**kwargs:
				Event handlers to attach (name=func)
		"""
		self.event_handlers = {}
		self.name, self.window = name, window

		# Adds any event handlers passed through kwargs
		self.add_event_handlers(**kwargs)

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

	@abstractmethod
	def enable(self) -> None:
		"""Enables this scene. (does not enable rendering)"""

	@abstractmethod
	def disable(self) -> None:
		"""Disables this scene. (does not disable rendering)"""
