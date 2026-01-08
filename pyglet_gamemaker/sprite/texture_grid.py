from typing import TYPE_CHECKING
from pyglet.image import TextureGrid as _TextureGrid

if TYPE_CHECKING:
	from .image_grid import ImageGrid


class TextureGrid(_TextureGrid):

	def __init__(self, grid: ImageGrid) -> None:
		super().__init__(grid)

		# Manually parse grid using top_down flag
		self.items = []
		for row in range(self.rows):
			# Flip row
			if grid.top_down:
				row = self.rows - 1 - row
			for col in range(self.columns):
				print(row, col, (self.item_width + grid.column_padding) * col,
					(self.item_height + grid.row_padding) * row,
					self.item_width, self.item_height)
				self.items.append(self.get_region(
					(self.item_width + grid.column_padding) * col,
					(self.item_height + grid.row_padding) * row,
					self.item_width, self.item_height
				))
