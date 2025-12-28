from typing import SupportsIndex

import pyglet
from pyglet.image import TextureRegion, ImageGrid, TextureGrid, AbstractImage


class SpriteSheet:
	"""An object holding a rectangular sheet of common sprites.

	Index to get portion of image to render.
	Allows indexing by name using `name(...)`
	"""

	img: AbstractImage
	"""Stores the original image"""
	image_grid: ImageGrid
	"""Stores the unoptimized image grid"""
	grid: TextureGrid
	"""Stores the optimized image grid (one actually rendered)"""
	lookup: dict[str, int] = {}
	"""The lookup table to convert aliases to integers for indexing"""

	def __init__(self, file_path: str, rows: int, cols: int) -> None:
		"""Create a sprite sheet from a file.

		Args:
			file_path (str): The path to the sprite sheet
			rows (int): The number of rows for sprites
			cols (int): The number of columns for sprites
		"""
		self.path, self.rows, self.cols = file_path, rows, cols
		self.img = pyglet.resource.image(file_path)  # Loads og img
		self.image_grid = ImageGrid(self.img, rows, cols)  # Creates image grid
		self.grid = TextureGrid(
			self.image_grid
		)  # For efficient rendering, make it all one texture

	def name(self, *args: str) -> None:
		"""Name all of the grid parts instead of indexing with numbers

		Args:
			*args (str):
				The names of the grid parts. Must be in same order as regular indexing.
		"""

		# Must be same number of names as parts of the grid
		if len(args) != len(self.grid):
			raise ValueError(
				f'SpriteSheet.name() takes {len(self.grid)} args, but {len(args)} were given.'
			)

		# Add all to lookup table
		self.lookup = {name: i for i, name in enumerate(args)}

	def __getitem__(
		self,
		index: str
		| int
		| slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
	) -> TextureRegion | list[TextureRegion]:
		# Slice and int can be directly used
		if isinstance(index, slice | int):
			return self.grid[index]
		# Use lookup table if string
		if isinstance(index, str):
			return self.grid[self.lookup[index]]
		raise ValueError(f'SpriteSheet[] recieved bad value: {index}')

	@property
	def item_width(self) -> int:
		"""Width of single item"""
		return self.grid.item_width

	@property
	def item_height(self) -> int:
		"""Height of single item"""
		return self.grid.item_height

	@property
	def item_dim(self) -> tuple[int, int]:
		"""Dimensions of single item"""
		return self.item_width, self.item_height
