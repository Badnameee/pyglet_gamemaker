from typing import TYPE_CHECKING

import pyglet
from pyglet.window import Window as PygletWin

if TYPE_CHECKING:
	from .scene import Scene


class Window(PygletWin):
	"""The main window that stores the scenes and runs the game.

	Add scenes using `add_scene` and use `start()` to run the game.
	"""

	scenes: dict[str, Scene] = {}
	"""Stores all the scenes in the game"""
	scene: str = ''
	"""The currently running scene"""

	centered: bool
	"""If True, the window is centered. Do not set."""

	def __init__(
		self, window_dim: tuple[int, int], center_window: bool = True, **kwargs
	) -> None:
		"""Create a Window object.

		Args:
			window_dim (tuple[int, int]):
				The dimensions of the window.
			center_window (bool, optional):
				If True, center the window on the screen.
				Defaults to True.
			**kwargs:
				Any extra arguments to add to pyglet window constructor.
				Read `pyglet.window.Window` documentation or see
				https://pyglet.readthedocs.io/en/latest/programming_guide/windowing.html
				for more.
		"""
		super().__init__(*window_dim, **kwargs)  # type: ignore[call-arg]

		# Center if requested
		self.centered = center_window
		if center_window:
			self.set_location(
				(self.screen.width - window_dim[0]) // 2,
				(self.screen.height - window_dim[1]) // 2,
			)

	def run(self, start_scene: str | None = None) -> None:
		"""Run the game.

		Args:
			start_scene (str | None, optional):
				The scene to start on.
				Defaults to None.
		"""
		if not self.scenes:
			raise RuntimeError('Window.scenes must have at least 1 scene!')

		# Set start scene if needed
		if start_scene:
			self.scene = start_scene

		# Enable beginning scene
		self.scenes[self.scene].enable()

		pyglet.app.run()

	def on_draw(self) -> None:
		self.clear()
		self.scenes[self.scene].batch.draw()

	def add_scene(self, name: str, obj: Scene) -> None:
		"""Add a scene to the game.

		Args:
			name (str): The name of the scene
			obj (Scene): The Scene object
		"""
		self.scenes[name] = obj
		obj.set_window(self)
		obj.add_event_handlers(on_scene_change=self._on_scene_change)
		obj.disable()

		# Sets default scene
		if self.scene == '':
			self.scene = name

	def pop_scene(self, name: str) -> Scene:
		"""Pop and return a scene from the game.

		Args:
			name (str): The name of the scene

		Returns:
			Scene: The Scene object removed
		"""
		return self.scenes.pop(name)

	def _on_scene_change(self, new_scene: str) -> None:
		"""Runs when the scene needs to be changed to a new one"""
		# Disable previous scene
		self.scenes[self.scene].disable()
		# Update scene
		self.scene = new_scene
		# Enable new scene
		self.scenes[self.scene].enable()
