# Built-In Modules
from abc import ABC, abstractmethod

# Pip Modules
import pyglet
from pyglet.window import Window
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch

class Scene(ABC, EventDispatcher):
	"""Abstract class for a Scene in the game, inherit to create own scenes.
	Window object should hold all scenes in window.scenes dictionary
	
	Dispatches `on_scene_change` (to window) when program wishes to switch scenes.

	`enable` and `disable` run from Window when enabling and disabling scene.

	Use kwargs to attach event handlers.
	"""

	batch: Batch

	def __init__(self, name: str, window: Window, **kwargs) -> None:
		"""Create a scene.

		Args:
			name (str): The name of the scene (used to identity scene by name)
			window (Window): The screen window (for pushing/popping handlers)
			**kwargs: Event handlers to attach (name=func)
		"""
		self.name, self.window = name, window
		
		self.register_event_type('on_scene_change')
		# Adds any event handlers passed through kwargs
		for name in kwargs:
			self.register_event_type(name)
		self.push_handlers(**kwargs)

	@abstractmethod
	def enable(self) -> None:
		"""Enables this scene. (does not enable rendering, it is always enabled)"""
	@abstractmethod
	def disable(self) -> None:
		"""Disables this scene. (does not disable rendering, it is always enabled)"""