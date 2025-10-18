from __future__ import annotations
from typing import TYPE_CHECKING

import pyglet
from pyglet.image import TextureRegion, ImageGrid, TextureGrid
if TYPE_CHECKING:
	...

class SpriteSheet:
	"""An object holding a sheet of common sprites. Allows indexing by name using :py:meth:`.name`"""

	def __init__(self, file_path: str, rows: int, cols: int) -> None:
		self.path, self.rows, self.cols = file_path, rows, cols
		self.raw_img = pyglet.resource.image(file_path) # Loads og img
		self.image_grid = ImageGrid(self.raw_img, 3, 1) # Creates image grid
		self.grid = TextureGrid(self.image_grid) # For efficient rendering, make it all one texture

		self.lookup: dict[str, int] = {}

	def name(self, *args: str) -> None:
		"""Name all of the grid parts instead of indexing with numbers"""

		# Must be same number of names as parts of the grid
		if len(args) != len(self.grid):
			raise ValueError(f'SpriteSheet.name() takes {len(self.grid)} args, but {len(args)} were given.')
		
		# Add all to lookup table
		self.lookup = {name: i for i, name in enumerate(args)}

	def __getitem__(self, index: str | int | slice) -> TextureRegion | list[TextureRegion]:
		# Slice and int can be directly used
		if isinstance(index, slice | int):
			return self.grid[index]
		# Use lookup table if string
		if isinstance(index, str):
			return self.grid[self.lookup[index]]
		raise ValueError(f'SpriteSheet[] recieved bad value: {index}')
	
	@property
	def width(self) -> int:
		"""Number of sprites wide"""
		return self.grid.item_width
	@property
	def height(self) -> int:
		"""Number of sprites high"""
		return self.grid.item_height