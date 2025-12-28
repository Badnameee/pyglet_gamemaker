from pyglet.graphics import Batch, Group
from ..types import *
from .hitbox import HitboxRender


class Rect(HitboxRender):
	"""A rendered rectangle.

	Has attributes for each vertex (`.bottomleft`, `.bottomright`, `.topright`, `.topleft`)

	To create a rectangle without a render, use `shapes.Hitbox.from_rect`.
	"""

	def __init__(
		self,
		x: float,
		y: float,
		width: float,
		height: float,
		color: Color,
		batch: Batch,
		group: Group,
		anchor_pos: Point2D = (0, 0),
	) -> None:
		"""Create a rectangle.

		Args:
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			color (Color):
				The color of the hitbox render
			batch (Batch):
				The batch for rendering
			group (Group):
				The group for rendering
			anchor_pos (Point2D, optional):
				The starting anchor position. Defaults to (0, 0).
		"""

		super().__init__(
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			color,
			batch,
			group,
			anchor_pos,
			subtype='rect',
		)

	@property
	def x(self) -> float:
		"""The x position of the rect. Does not represent the actual position.

		To be more specific, the x translation added to the local coords.
		"""
		return self.hitbox._trans_pos[0]

	@x.setter
	def x(self, val: float) -> None:
		self.move_to(x=val)

	@property
	def y(self) -> float:
		"""The y position of the rect. Does not represent the actual position.

		To be more specific, the y translation added to the local coords.
		"""
		return self.hitbox._trans_pos[1]

	@y.setter
	def y(self, val: float) -> None:
		self.move_to(y=val)

	@property
	def pos(self) -> Point2D:
		"""The position of the rect. Does not represent the actual position.

		To be more specific, the translation added to the local coords.
		"""
		return self.hitbox._trans_pos

	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.move_to(*val)

	@property
	def bottomleft(self) -> Point2D:
		"""The bottomleft vertex of the rect. Does not represent the actual position.

		To be more specific, the *unrotated* AND *unanchored* vertex position.
		"""
		return self.hitbox._raw_coords[0]

	@property
	def bottomright(self) -> Point2D:
		"""The bottomright vertex of the rect. Does not represent the actual position.

		To be more specific, the *unrotated* AND *unanchored* vertex position.
		"""
		return self.hitbox._raw_coords[1]

	@property
	def topright(self) -> Point2D:
		"""The topright vertex of the rect. Does not represent the actual position.

		To be more specific, the *unrotated* AND *unanchored* vertex position.
		"""
		return self.hitbox._raw_coords[2]

	@property
	def topleft(self) -> Point2D:
		"""The topleft vertex of the rect. Does not represent the actual position.

		To be more specific, the *unrotated* AND *unanchored* vertex position.
		"""
		return self.hitbox._raw_coords[3]

	@property
	def width(self) -> float:
		"""The width of the *unrotated* rectangle."""
		return self.hitbox._raw_coords[1][0] - self.hitbox._raw_coords[0][0]

	@width.setter
	def width(self, val: float) -> None:
		# Set raw coords instead of local coords because ._calc_coords
		# updates local coords. Updates to local coords would
		# get overwritten when calling ._calc_coords
		self.hitbox._raw_coords = (
			self.hitbox._raw_coords[0],
			(self.hitbox._raw_coords[0][0] + val, self.hitbox._raw_coords[1][1]),
			(self.hitbox._raw_coords[3][0] + val, self.hitbox._raw_coords[2][1]),
			self.hitbox._raw_coords[3],
		)
		self._calc_coords()

	@property
	def height(self) -> float:
		"""The height of the *unrotated* rectangle."""
		return self.hitbox._raw_coords[3][1] - self.hitbox._raw_coords[0][1]

	@height.setter
	def height(self, val: float) -> None:
		# Set raw coords instead of local coords because ._calc_coords
		# updates local coords. Updates to local coords would
		# get overwritten when calling ._calc_coords
		self.hitbox._raw_coords = (
			self.hitbox._raw_coords[0],
			self.hitbox._raw_coords[1],
			(self.hitbox._raw_coords[2][0], self.hitbox._raw_coords[1][1] + val),
			(self.hitbox._raw_coords[3][0], self.hitbox._raw_coords[0][1] + val),
		)
		self._calc_coords()
