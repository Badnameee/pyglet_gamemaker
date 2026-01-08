from typing import TYPE_CHECKING
from pyglet.image import ImageGrid as _ImageGrid

if TYPE_CHECKING:
	from pyglet.image import AbstractImage


class ImageGrid(_ImageGrid):

	def __init__(self, image: AbstractImage, rows: int, columns: int, row_padding: int, column_padding: int, top_down: bool) -> None:
		super().__init__(image, rows, columns, row_padding=row_padding, column_padding=column_padding)

		self.top_down = top_down

	def _update_items(self) -> None:
		# Only load items once
		if not self._items:
			for row in range(self.rows):
				# Flip row
				if self.top_down:
					row = self.rows - 1 - row
				for col in range(self.columns):
					self._items.append(self.image.get_region(
						(self.item_width + self.column_padding) * col,
						(self.item_height + self.row_padding) * row,
						self.item_width, self.item_height
					))
