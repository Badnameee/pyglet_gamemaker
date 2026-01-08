"""Module holding SpriteSheet class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pyglet
from .image_grid import ImageGrid
from .texture_grid import TextureGrid

if TYPE_CHECKING:
	from typing import SupportsIndex

	from pyglet.image import AbstractImage, TextureRegion


class SpriteSheet:
	"""An object holding a rectangular sheet of common sprites.

	Index to get portion of image to render.
	Allows indexing by name using `.name()`.
	"""

	path: str
	"""Path of original image"""
	rows: int
	"""Number of rows in sheet"""
	cols: int
	"""Number of cols in sheet"""
	img: AbstractImage
	"""Stores the original image"""
	image_grid: ImageGrid
	"""Stores the unoptimized image grid"""
	texture_grid: TextureGrid
	"""Stores the optimized image grid (one actually rendered)"""
	lookup: dict[str, int] = {}
	"""The lookup table to convert aliases to integers for indexing"""

	def __init__(self, file_path: str, rows: int, cols: int, row_padding: int=0, col_padding: int=0, top_down: bool=True) -> None:
		"""Create a sprite sheet from a file.

		Args:
			file_path (str): The path to the sprite sheet
			rows (int): The number of rows for sprites
			cols (int): The number of columns for sprites
		"""
		self.path, self.rows, self.cols = file_path, rows, cols
		self.row_padding, self.col_padding = row_padding, col_padding
		self.top_down = top_down
		self.img = pyglet.resource.image(file_path)
		self.image_grid = ImageGrid(self.img, rows, cols, row_padding, col_padding, self.top_down)
		self.texture_grid = TextureGrid(self.image_grid)

	def name(self, *args: str) -> None:
		"""Name all of the grid parts instead of indexing with numbers.

		Args:
			*args (str):
				The names of the grid parts. Must be in same order as regular indexing.
		"""
		# Must be same number of names as parts of the grid
		if len(args) != len(self.texture_grid):
			raise ValueError(
				f'SpriteSheet.name() takes {len(self.texture_grid)} args, but {len(args)} were given.'
			)

		# Add all to lookup table
		self.lookup = {name: i for i, name in enumerate(args)}

	def __getitem__(
		self,
		index: str
		| int
		| slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
	) -> TextureRegion | list[TextureRegion]:
		"""Get the sprite at position `index`.

		Either a normal index or a string matching an index (using `.name()`) can be used.
		"""
		# Slice and int can be directly used
		if isinstance(index, slice | int):
			return self.texture_grid[index]
		# Use lookup table if string
		if isinstance(index, str):
			return self.texture_grid[self.lookup[index]]
		raise ValueError(f'SpriteSheet[] recieved bad value: {index}')

	@property
	def item_width(self) -> int:
		"""Width of single sprite."""
		return self.texture_grid.item_width

	@property
	def item_height(self) -> int:
		"""Height of single sprite."""
		return self.texture_grid.item_height

	@property
	def item_dim(self) -> tuple[int, int]:
		"""Dimensions of single sprite."""
		return self.item_width, self.item_height
