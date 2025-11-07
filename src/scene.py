from abc import ABC, abstractmethod

from pyglet.window import Window
from pyglet.event import EventDispatcher
from pyglet.graphics import Batch

class Scene(ABC, EventDispatcher):
	"""Abstract class for a Scene in the game, inherit to create own scenes.
	Window object should hold all scenes in window.scenes dictionary

	When inheriting, a batch must be created
	
	Dispatches `on_scene_change` (to window) when program wishes to switch scenes.

	`enable` and `disable` run from `Window` class when enabling and disabling scene.
	These enabled and disable the scene, but rendering is stopped because batch is not rendered

	Use kwargs to attach event handlers.
	"""

	batch: Batch

	def __init__(self, name: str, window: Window, **kwargs) -> None:
		"""Create a scene.

		Args:
			name (str): The name of the scene (used to identity scene by name)
			window (Window): The screen window
			**kwargs: Event handlers to attach (name=func)
		"""
		self.name, self.window = name, window
		
		# Adds any event handlers passed through kwargs
		for name in kwargs:
			self.register_event_type(name)
		self.push_handlers(**kwargs)

	@abstractmethod
	def enable(self) -> None:
		"""Enables this scene. (does not enable rendering)"""
	@abstractmethod
	def disable(self) -> None:
		"""Disables this scene. (does not disable rendering)"""
