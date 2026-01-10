"""Module holding SpriteSheet class.

Use `~pgm.sprite.SpriteSheet` instead of `~pgm.sprite.sprite_sheet.SpriteSheet`
"""

from __future__ import annotations

from pathlib import Path, PurePath
from typing import TYPE_CHECKING

import pyglet
import yaml

from ..errors import InvalidConfigFile
from .image_grid import ImageGrid
from .yaml_validator import YAMLValidator

if TYPE_CHECKING:
	from typing import Any, Self, SupportsIndex

	from pyglet.image import Texture, TextureRegion


class SpriteSheet:
	"""An object holding a rectangular sheet of common sprites.

	Index to get specific sprite to render.
	Allows indexing by name using `.name()`.
	"""

	path: Path
	"""Path of original image"""
	yaml_path: Path
	"""Path of .yaml config file"""
	rows: int
	"""Number of rows in sheet"""
	cols: int
	"""Number of cols in sheet"""
	row_padding: int
	"""Padding between sprite rows"""
	col_padding: int
	"""Padding between sprite columns"""
	top_down: bool
	"""If True, parse spritesheet from top-to-bottom.
	If False, parse from bottom-to-top.
	"""
	atlas: bool
	"""If True, spritesheet is stored in a global atlas. False if not.
	See `~pgm.sprite.SpriteSheet` for more info."""
	img: Texture
	"""Stores the original image"""
	image_grid: ImageGrid
	"""Stores the unoptimized image grid"""
	lookup: dict[str, int] = {}
	"""The lookup table to convert aliases to integers for indexing"""

	yaml: Any | None = None

	def __init__(
		self,
		file_path: str,
		rows: int,
		cols: int,
		row_padding: int = 0,
		col_padding: int = 0,
		top_down: bool = True,
		atlas: bool = True,
		yaml: bool = False,
	) -> None:
		"""Create a sprite sheet from a file.

		Args:
			file_path (str):
				The path to the sprite sheet
			rows (int):
				The number of rows for sprites
			cols (int):
				The number of columns for sprites
			row_padding (int, optional):
				The amount to pad between rows of sprites. Does not include edge of sheet.
				Defaults to 0.
			col_padding (int, optional):
				The amount to pad between columns of sprites. Does not include edge of sheet.
				Defaults to 0.
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			atlas (bool, optional):
				If True, add spritesheet to atlas for more efficient rendering but less fine control.
				Ex. Cannot set texture parameters without setting for entire atlas.
				If False, create separate texture. Slower but allows for more customization.
				Defaults to True.
		"""
		self.path, self.rows, self.cols = Path(file_path), rows, cols
		self.row_padding, self.col_padding = row_padding, col_padding
		self.top_down = top_down
		self.img = pyglet.resource.image(file_path, atlas=atlas)
		self.image_grid = ImageGrid(
			self.img, rows, cols, row_padding, col_padding, self.top_down
		)

		if yaml:
			self.yaml_file = Path(file_path).absolute().with_suffix('.yaml')

	@classmethod
	def from_yaml(
		cls, file_path: str, top_down: bool = True, atlas: bool = True
	) -> Self:
		"""Load a spritesheet using the associated yaml file.

		Args:
			file_path (str):
				The path of the image. Name stem must be the same as the .yaml file
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
			atlas (bool, optional):
				If True, add spritesheet to atlas for more efficient rendering but less fine control.
				Ex. Cannot set texture parameters without setting for entire atlas.
				If False, create separate texture. Slower but allows for more customization.
				Defaults to True.
		"""
		yaml_path = Path(file_path).absolute().with_suffix('.yaml')


		errors = YAMLValidator(yaml_path, 'Anim').validate()
		if errors:
			raise InvalidConfigFile(PurePath(yaml_path), errors)

		yaml = cls._raw_yaml(yaml_path)
		self = cls(
			file_path,
			yaml['rows'],
			yaml['cols'],
			yaml['row-padding'],
			yaml['col-padding'],
			top_down,
			atlas,
			yaml=True,
		)
		self._name_from_yaml()

		return self

	def name(self, *args: str) -> None:
		"""Name all of the grid parts instead of indexing with numbers.

		Args:
			*args (str):
				The names of the grid parts. Must be in same order as regular indexing.
		"""
		# Must be same number of names as parts of the grid
		if len(args) != len(self.image_grid):
			raise ValueError(
				f'SpriteSheet.name() takes {len(self.image_grid)} args, but {len(args)} were given.'
			)

		# Add all to lookup table
		self.lookup = {name: i for i, name in enumerate(args)}

	@staticmethod
	def _raw_yaml(file_path: Path) -> Any:
		with open(file_path) as file:
			return yaml.safe_load(file)

	def _name_from_yaml(self) -> None:
		with open(self.path.absolute().with_suffix('.yaml')) as file:
			self.yaml = yaml.safe_load(file)

			# Parse data for names
			self.lookup.clear()
			for row_num, row in enumerate(self.yaml['data']):
				for col_num, name in enumerate(row):
					# Void, not a sprite
					if name == self.yaml['void']:
						continue
					self.lookup[name] = row_num * self.cols + col_num

	def __getitem__(
		self,
		index: str
		| int
		| slice[SupportsIndex | None, SupportsIndex | None, SupportsIndex | None],
	) -> TextureRegion:
		"""Get the sprite at position `index`.

		Either a normal index or a string matching an index (using `.name()`) can be used.
		"""
		# Note: guaranteed to return TextureRegion because
		# 	resource.image returns a Texture, and image grid takes region of it

		# Slice and int can be directly used
		if isinstance(index, slice | int):
			return self.image_grid[index]  # type: ignore[return-value]
		# Use lookup table if string
		if isinstance(index, str):
			return self.image_grid[self.lookup[index]]  # type: ignore[return-value]
		raise ValueError(f'SpriteSheet[] recieved bad value: {index}')

	@property
	def item_width(self) -> int:
		"""Width of single sprite."""
		return self.image_grid.item_width

	@property
	def item_height(self) -> int:
		"""Height of single sprite."""
		return self.image_grid.item_height

	@property
	def item_dim(self) -> tuple[int, int]:
		"""Dimensions of single sprite."""
		return self.image_grid.item_width, self.image_grid.item_height
