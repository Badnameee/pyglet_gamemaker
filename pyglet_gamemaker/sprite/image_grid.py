"""Module holding ImageGrid class.

Use `~pgm.sprite.ImageGrid` instead of `~pgm.sprite.image_grid.ImageGrid`
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyglet.image import ImageGrid as _ImageGrid

if TYPE_CHECKING:
	from pyglet.image import AbstractImage


class ImageGrid(_ImageGrid):
	"""A wrapper for `~pyglet.image.ImageGrid` to create an image grid from an image/spritesheet.

	This cuts up the image/spritesheet into separate images/sprites to be indexed.
	Used internally in `~pgm.sprite.SpriteSheet`.
	"""

	top_down: bool
	"""If True, parse spritesheet from top-to-bottom.
	If False, parse from bottom-to-top.
	"""

	def __init__(
		self,
		image: AbstractImage,
		rows: int,
		columns: int,
		row_padding: int,
		col_padding: int,
		top_down: bool,
	) -> None:
		"""Create an ImageGrid from an image.

		Args:
			image (AbstractImage):
				The image to use. Can be a raw image using image.load or resource.image.
			rows (int):
				The number of rows for the grid
			columns (int):
				The number of columns for the grid
			row_padding (int, optional):
				The amount to pad between rows of sprites. Does not include edge of sheet.
				Defaults to 0.
			col_padding (int, optional):
				The amount to pad between columns of sprites. Does not include edge of sheet.
				Defaults to 0.
			top_down (bool, optional):
				If True, parse spritesheet from top-to-bottom. If False, parse from bottom-to-top.
				Defaults to True.
		"""
		super().__init__(
			image, rows, columns, row_padding=row_padding, column_padding=col_padding
		)

		self.top_down = top_down

	def _update_items(self) -> None:
		# Only load items once
		if not self._items:
			for row in range(self.rows):
				# Calculate y top-down if necessary
				if self.top_down:
					y = (
						self.image.height
						- self.item_height
						- (self.item_height + self.row_padding) * row
					)
				else:
					y = (self.item_height + self.row_padding) * row

				for col in range(self.columns):
					self._items.append(
						self.image.get_region(
							(self.item_width + self.column_padding) * col,
							y,
							self.item_width,
							self.item_height,
						)
					)
