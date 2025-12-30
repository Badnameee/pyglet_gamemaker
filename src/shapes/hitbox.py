from typing import Literal, Self
import math

import pyglet
from pyglet.math import Vec2
from pyglet.graphics import Batch, Group
from pyglet.shapes import Polygon, Circle
from ..types import *


class Hitbox:
	"""Store a convex hitbox that uses SAT (Separating Axis Theorem) method for collision.

	Can use `.from_rect()` to get coords for rectangle.
	Use `hitbox.HitboxCircle` for circle collisions.

	For _coord vars (ex. `._local_coords`), there are 3 types of transformation
	- translated: Adding global position of hitbox to local position (moving in 2D space)
	- rotated: Adding the rotation of the hitbox
	- anchored: Shifting global position to account for anchor position of hitbox
	"""

	_local_coords: tuple[Point2D, ...] = tuple()
	"""Holds the *untransformed* coords relative to first coordinate"""
	_raw_coords: tuple[Point2D, ...] = tuple()
	"""Holds the *unrotated* AND *unanchored*, but *translated/global* coords"""
	_unanchored_coords: tuple[Point2D, ...] = tuple()
	"""Holds the *unanchored*, *translated/global* coords"""
	_anchor_coords: tuple[Point2D, ...] = tuple()
	"""Holds the *untransformed* coords relative to anchor pos"""
	_rotation_amount: tuple[Point2D, ...] = tuple()
	"""Holds the translation due to rotation of each point"""
	_anchor_pos: Point2D = 0, 0
	_angle: float = 0

	coords: tuple[Point2D, ...]
	"""The final coordinates of the hitbox"""
	_trans_pos: Point2D
	"""Holds the translation amount from (0, 0)"""
	subtype: str | None
	"""Subtype (ex. 'rect') of hitbox"""

	def __init__(
		self,
		coords: tuple[Point2D, ...],
		anchor_pos: Point2D = (0, 0),
		*,
		_subtype: str | None = None,
	) -> None:
		"""Create a hitbox.

		Args:
			coords (tuple[Point2D, ...]):
				The coordinates of the hitbox
			anchor_pos (Point2D, optional):
				The starting anchor position.
				Defaults to (0, 0).
		"""

		if len(coords) < 2:
			raise ValueError(
				f'Hitbox needs at least 2 coordinates ({len(coords)} passed).'
			)

		self._trans_pos = coords[0]
		self._raw_coords = coords
		self.anchor_pos = anchor_pos
		self.subtype = _subtype

	@classmethod
	def from_rect(
		cls, x: float, y: float, width: float, height: float, anchor_pos: Point2D
	) -> Self:
		"""Create a hitbox from rectangle args.

		Args:
			x (float):
				x position
			y (float):
				y position
			width (float):
				Width of rect
			height (float):
				Height of rect
			anchor_pos (Point2D):
				Anchor position
		"""
		return cls(
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			anchor_pos,
			_subtype='rect',
		)

	def _get_axes(self, remove_dupes: bool) -> list[Vec2]:
		"""Get the normal axes of the hitbox (for SAT).

		These are perpendicular vectors to each edge.

		Args:
			remove_dupes (bool):
				If true, remove duplicate axes (only works for rect) to
				optimize speed and sacrifice MTV.

		Returns:
			list[Vec2]: All of the normal axes as vectors.
		"""

		axes = []

		# Loops through vertices and gets all adjacent pairs
		for i in range(
			len(self.coords) // (2 if remove_dupes and self.subtype == 'rect' else 1)
		):
			# Grabbing vertex positions
			p1, p2 = self.coords[i], self.coords[(i + 1) % len(self.coords)]

			# Calculates the vector between them
			vec = p1[0] - p2[0], p1[1] - p2[1]
			# Gets perpendicular vector and normalizes it
			# Normalizing helps get MTV
			axes.append(Vec2(-vec[1], vec[0]).normalize())

		return axes

	def _project(self, axis: Vec2) -> tuple[float, float]:
		"""Projects the hitbox onto an axis (use self._get_axes()) (for SAT)

		Args:
			axis (Vec2):
				The normal axis to project onto

		Returns:
			tuple[float, float]: The left and right side, respectively, of the projected line
		"""

		# Stores the left (minimum) and right (maximum) of line
		maximum = minimum = axis.dot(Vec2(*self.coords[0]))

		# Gets projections for each vertice
		# Vertice with lowest and highest projections are used in line
		for i in range(1, len(self.coords)):
			# Projection using dot product
			pos = axis.dot(Vec2(*self.coords[i]))
			maximum = max(maximum, pos)
			minimum = min(minimum, pos)

		return minimum, maximum

	@staticmethod
	def _intersect(l1: tuple[float, float], l2: tuple[float, float]) -> bool:
		"""Checks if two lines intersect (for SAT).

		Returns:
			bool: If True, lines intersect
		"""

		# Left of line1 inside line2
		if l2[0] <= l1[0] < l2[1]:
			return True

		# Right of line1 inside line2
		if l2[0] < l1[1] <= l2[1]:
			return True

		# Line2 completely inside line1
		if l1[0] < l2[0] and l1[1] > l2[1]:
			return True

		return False

	@staticmethod
	def _get_intersection_length(
		l1: tuple[float, float], l2: tuple[float, float]
	) -> float:
		"""Gets the length of intersection between 2 lines. (for SAT)

		Returns:
			float: The length of intersection
		"""

		# Left of line1 inside line2
		if l2[0] <= l1[0] < l2[1]:
			return l2[1] - l1[0]

		# Right of line1 inside line2
		elif l2[0] < l1[1] <= l2[1]:
			return -(l1[1] - l2[0])

		# Line2 completely inside line1
		elif l1[0] < l2[0] and l1[1] > l2[1]:
			# Finds which way is shorter
			if l1[1] - l2[0] < l2[1] - l1[0]:
				return -(l1[1] - l2[0])
			return l2[1] - l1[0]

		#! Should only return 0 if no intersection, should never happen
		return 0

	@staticmethod
	def _contains(l1: tuple[float, float], l2: tuple[float, float]) -> bool:
		"""Checks if one of the lines in completely contained inside the other (for SAT)

		Returns:
			bool: If True, one of the lines is completely contained within other line
		"""
		return (l1[0] < l2[0] and l1[1] > l2[1]) or (l2[0] < l1[0] and l2[1] > l1[1])

	def collide(
		self,
		other: Hitbox | HitboxRender | HitboxRenderCircle,
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox | HitboxRender | HitboxRenderCircle):
				The other hitbox to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""

		# Get hitbox if not subclass
		if not isinstance(other, Hitbox):
			other = other.hitbox

		# Get special circle collision axis
		if isinstance(self, HitboxCircle):
			self._set_collision_axis(other)
		if isinstance(other, HitboxCircle):
			other._set_collision_axis(self)

		# * Step 1: Get the normal axes of each edge
		axes = self._get_axes(sacrifice_MTV)
		other_axes = other._get_axes(sacrifice_MTV)

		# These store the length and axis for the MTV
		MTV_len = float('inf')
		MTV_axis = Vec2(0, 0)

		# * Step 2: Project the shapes onto each axis
		for axis in axes + other_axes:
			l1 = self._project(axis)
			l2 = other._project(axis)

			# * Step 3: Check for intersection
			# * If the projections do not intersect, there cannot be a collision
			if not self._intersect(l1, l2):
				return False, None

			# * Step 4: For MTV - Get the smallest intersection length
			# *	and store it along with the axis
			overlap = self._get_intersection_length(l1, l2)
			if abs(overlap) < abs(MTV_len):
				MTV_len = overlap
				MTV_axis = axis

		return True, MTV_axis * MTV_len

	def collide_any(
		self,
		others: list[Hitbox | HitboxRender | HitboxRenderCircle],
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm on a list of others.

		Args:
			others (list[Hitbox | HitboxRender | HitboxRenderCircle]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""
		for rect in others:
			if (collision_info := self.collide(rect, sacrifice_MTV))[0]:
				return collision_info

		return False, None

	def _calc_coords(self) -> None:
		"""Updates coordinates based on new position, angle, and/or anchor_pos"""

		# Steps:
		# 1. Update local coords
		# 2. Update anchor coords
		# 3. Get displacement caused by rotation of anchor coords
		# 4. Add translation to local to get raw
		# 5. Add anchor rotation displacement to raw to get unanchored
		# 6. Add anchor to unanchored to get final

		# Use the raw coords, which are precalculated in __init__
		# before first ._calc_coords call
		self._local_coords = tuple(
			(
				coord[0] - self._raw_coords[0][0],
				coord[1] - self._raw_coords[0][1],
			)
			for coord in self._raw_coords
		)

		self._anchor_coords = tuple(
			(coord[0] - self.anchor_x, coord[1] - self.anchor_y)
			for coord in self._local_coords
		)

		self._rotation_amount = tuple(
			(
				self._get_rotated_pos(coord, 'x') - coord[0],  # type: ignore[operator]
				self._get_rotated_pos(coord, 'y') - coord[1],  # type: ignore[operator]
			)
			for coord in self._anchor_coords
		)

		self._raw_coords = tuple(
			(coord[0] + self._trans_pos[0], coord[1] + self._trans_pos[1])
			for coord in self._local_coords
		)

		self._unanchored_coords = tuple(
			(coord[0] + rotation[0], coord[1] + rotation[1])
			for coord, rotation in zip(self._raw_coords, self._rotation_amount)
		)

		self.coords = tuple(
			(coord[0] - self.anchor_x, coord[1] - self.anchor_y)
			for coord in self._unanchored_coords
		)

	def _get_rotated_pos(self, coord: Point2D, axis: Axis) -> float | Point2D:
		"""Gets the rotated point using `.angle`.

		Args:
			coord (Point2D):
				The coordinate to rotate
			axis (Axis):
				The axis to calculate it on

		Returns:
			float | Point2D: The rotated point or single-axis coord
		"""

		if axis == 'x':
			return coord[0] * math.cos(self.angle) - coord[1] * math.sin(self.angle)
		if axis == 'y':
			return coord[0] * math.sin(self.angle) + coord[1] * math.cos(self.angle)

		return (
			coord[0] * math.cos(self.angle) - coord[1] * math.sin(self.angle),
			coord[0] * math.sin(self.angle) + coord[1] * math.cos(self.angle),
		)

	@property
	def x(self) -> float:
		"""The x position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._trans_pos[0]
	
	@x.setter
	def x(self, val: float) -> None:
		self._trans_pos = val, self._trans_pos[1]
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self._trans_pos[1]
	
	@y.setter
	def y(self, val: float) -> None:
		self._trans_pos = self._trans_pos[0], val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of the anchor point."""
		return self._trans_pos
	
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self._trans_pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor_pos[0]

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self._anchor_pos = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self._anchor_pos[1]

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self._anchor_pos = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor_pos(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self._anchor_pos

	@anchor_pos.setter
	def anchor_pos(self, val: Point2D) -> None:
		self._anchor_pos = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""Angle, in radians, of hitbox"""
		return self._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self._angle = val
		self._calc_coords()


class HitboxCircle(Hitbox):
	"""Holds a hitbox for circle-polygon collisions.

	Do not try to access `.coords` as they are not real coords.
	"""

	axis: Vec2
	"""The axis between the center and the closest point on last hitbox checked for collision."""
	radius: float
	"""The radius of the circle"""

	def __init__(
		self, x: float, y: float, radius: float, anchor_pos: Point2D = (0, 0)
	) -> None:
		"""Create a hitbox from a circle.

		Args:
			x (float):
				Center x
			y (float):
				Center y
			radius (float):
				The radius of the circle
			anchor_pos (Point2D, optional):
				The anchor position.
				Defaults to (0, 0).
		"""
		super().__init__(((x, y), (radius, 0)), anchor_pos, _subtype='circle')
		self.axis = Vec2(0, 0)
		self.radius = radius

	def _get_axes(self, sacrifice_MTV: bool) -> list[Vec2]:
		return [self.axis.normalize()]

	def _project(self, axis: Vec2) -> tuple[float, float]:
		proj = axis.dot(Vec2(*self.coords[0]))
		return proj - self.radius, proj + self.radius

	def collide_any(
		self,
		others: list[Hitbox | HitboxRender | HitboxRenderCircle],
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		for rect in others:
			if (collision_info := self.collide(rect, sacrifice_MTV))[0]:
				return collision_info

		return False, None

	def _set_collision_axis(
		self, hitbox: Hitbox | HitboxRender | HitboxRenderCircle
	) -> None:
		"""Gets closest point on hitbox to circle

		Args:
			hitbox (Hitbox | HitboxRender | HitboxRenderCircle):
				Hitbox to check collision with

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""

		def get_projection(v1: Vec2, v2: Vec2) -> Vec2:
			# Clamping forces the projection to be within the 2 vertices of the polygon
			# (or 2 endpoints of v2) by forcing scale factor to be from 0-1
			# This facilitates finding closest points on polygon to circle center
			return pyglet.math.clamp(v1.dot(v2) / v2.length_squared(), 0, 1) * v2

		# Get hitbox if not subclass
		if not isinstance(hitbox, Hitbox):
			hitbox = hitbox.hitbox

		#* Special case: circle-circle collision
		#*	To calculate collision axis, use line between centers
		if isinstance(hitbox, HitboxCircle):
			# Get vector pointing from the center of circle #1 to...
			self.axis = Vec2(
				self.coords[0][0] - hitbox.coords[0][0],
				self.coords[0][1] - hitbox.coords[0][1]
			)
			# ... the edge of circle #2
			self.axis = self.axis.normalize() * (self.axis.length() - hitbox.radius)
			return

		# Get closest point to other hitbox
		least = Vec2(0, 0), float('inf')
		for i in range(len(hitbox.coords)):
			# Loop through each axis on polygon
			# Grabbing vertex positions
			p1, p2 = hitbox.coords[i], hitbox.coords[(i + 1) % len(hitbox.coords)]

			# Calculates the vector between vertices
			vec = Vec2(p2[0] - p1[0], p2[1] - p1[1])

			# Vector from vertex to center of circle
			pre_proj = Vec2(self.coords[0][0] - p1[0], self.coords[0][1] - p1[1])

			# Proj holds the vector from p1 to the closest point
			# on the polygon to the circle center
			proj = get_projection(pre_proj, vec)
			# Subtracting pre_proj gives vector from circle center to closest point
			diff = proj - pre_proj

			# Update least
			if (length := diff.length()) < least[1]:
				least = diff, length

		self.axis = least[0]

	def _calc_coords(self):
		# Same algorithm as in Hitbox, but optimized for single center coordinate of circle
		self._local_coords = ((0, 0),)
		self._anchor_coords = ((-self.anchor_x, -self.anchor_y),)
		self._rotation_amount = (
			(
				self._get_rotated_pos(self._anchor_coords[0], 'x')
				- self._anchor_coords[0][0],  # type: ignore[operator]
				self._get_rotated_pos(self._anchor_coords[0], 'y')
				- self._anchor_coords[0][1],  # type: ignore[operator]
			),
		)
		self._raw_coords = (self._trans_pos,)
		self._unanchored_coords = (
			(
				self._raw_coords[0][0] + self._rotation_amount[0][0],
				self._raw_coords[0][1] + self._rotation_amount[0][1],
			),
		)
		self.coords = (
			(
				self._unanchored_coords[0][0] - self.anchor_x,
				self._unanchored_coords[0][1] - self.anchor_y,
			),
		)


class HitboxRender:
	"""Holds a Hitbox with `.hitbox` and `.render` objects"""

	_hitbox_color: Color

	hitbox: Hitbox
	"""The hitbox object"""
	render: Polygon
	"""The render object"""
	subtype: str | None
	"""Subtype (ex. 'rect') of hitbox"""

	def __init__(
		self,
		coords: tuple[Point2D, ...],
		color: Color,
		batch: Batch,
		group: Group,
		anchor_pos: Point2D = (0, 0),
		*,
		subtype: str | None = None,
	) -> None:
		"""Create a hitbox render.

		Args:
			coords (tuple[Point2D, ...]):
				The coordinates of the hitbox
			color (Color):
				The color of the hitbox render
			batch (Batch):
				The batch for rendering
			group (Group):
				The group for rendering
			anchor_pos (Point2D, optional):
				The starting anchor position.
				Defaults to (0, 0).
			circle (bool, optional):
				If True, hitbox is a circle (for SAT).
				Defaults to False.
			rect (bool, optional):
				If True, hitbox is a rectangle (for SAT).
				Defaults to False.
		"""
		self.render = Polygon(*coords, color=color.value, batch=batch, group=group)
		self.hitbox = Hitbox(coords, anchor_pos, _subtype=subtype)

		self.subtype = subtype
		self._hitbox_color = color

	@classmethod
	def from_rect(
		cls,
		x: float,
		y: float,
		width: float,
		height: float,
		color: Color,
		batch: Batch,
		group: Group,
		anchor_pos: Point2D = (0, 0),
	) -> Self:
		"""Create a hitbox render from rectangle dimensions.

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
			anchor_pos (Point2D):
				Anchor position
		"""
		return cls(
			((x, y), (x + width, y), (x + width, y + height), (x, y + height)),
			color,
			batch,
			group,
			anchor_pos,
			subtype='rect',
		)

	def collide(
		self,
		other: Hitbox | HitboxRender | HitboxRenderCircle,
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox | HitboxRender | HitboxRenderCircle):
				The other hitbox to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""
		return self.hitbox.collide(other, sacrifice_MTV)

	def collide_any(
		self,
		others: list[Hitbox | HitboxRender | HitboxRenderCircle],
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm on a list of others.

		Args:
			others (list[Hitbox | HitboxRender | HitboxRenderCircle]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""
		return self.hitbox.collide_any(others, sacrifice_MTV)

	def _calc_coords(self):
		self.hitbox._calc_coords()

		# Update polygon render
		self.render._coordinates = self.hitbox.coords
		self.render._update_vertices()
		self.render.x = self.hitbox.coords[0][0]
		self.render.y = self.hitbox.coords[0][1]

	@property
	def x(self) -> float:
		"""The x position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.hitbox._trans_pos[0]
	
	@x.setter
	def x(self, val: float) -> None:
		self.hitbox._trans_pos = val, self.hitbox._trans_pos[1]
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.hitbox._trans_pos[1]
	
	@y.setter
	def y(self, val: float) -> None:
		self.hitbox._trans_pos = self.hitbox._trans_pos[0], val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of the anchor point."""
		return self.hitbox._trans_pos
	
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.hitbox._trans_pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self.hitbox.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self.hitbox._anchor_pos = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self.hitbox.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self.hitbox._anchor_pos = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor_pos(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self.hitbox._anchor_pos

	@anchor_pos.setter
	def anchor_pos(self, val: Point2D) -> None:
		self.hitbox._anchor_pos = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""Angle, in radians, of hitbox"""
		return self.hitbox._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self.hitbox._angle = val
		self._calc_coords()

	@property
	def hitbox_color(self) -> Color:
		"""Color of hitbox"""
		return self._hitbox_color

	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val.value


class HitboxRenderCircle:
	"""Holds a Circle Hitbox with `.hitbox` and `.render` objects"""

	_hitbox_color: Color

	hitbox: HitboxCircle
	"""The hitbox object"""
	render: Circle
	"""The render object"""
	subtype: str | None
	"""Subtype (ex. 'rect') of hitbox"""

	def __init__(
		self,
		x: float,
		y: float,
		radius: float,
		color: Color,
		batch: Batch,
		group: Group,
		anchor_pos: Point2D = (0, 0),
	) -> None:
		"""Create a circular hitbox render

		Args:
			x (float):
				Center x
			y (float):
				Center y
			radius (float):
				The radius of the circle
			color (Color):
				The color of the hitbox render
			batch (Batch):
				The batch for rendering
			group (Group):
				The group for rendering
			anchor_pos (Point2D, optional):
				The anchor position.
				Defaults to (0, 0).
		"""
		self.render = Circle(x, y, radius, color=color.value, batch=batch, group=group)
		self.hitbox = HitboxCircle(x, y, radius, anchor_pos)

		self.subtype = 'circle'
		self._hitbox_color = color

	def collide(
		self,
		other: Hitbox | HitboxRender | HitboxRenderCircle,
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to determine if 2 objects are colliding.

		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox | HitboxRender | HitboxRenderCircle):
				The other hitbox to detect collision with
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""
		return self.hitbox.collide(other, sacrifice_MTV)

	def collide_any(
		self,
		others: list[Hitbox | HitboxRender | HitboxRenderCircle],
		sacrifice_MTV: bool = False,
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm on a list of others.

		Args:
			others (list[Hitbox | HitboxRender | HitboxRenderCircle]):
				List of others to check collision with self
			sacrifice_MTV (bool, optional):
				If True, optimize speed in exchange for no MTV.
				Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
				collision passed and MTV (None if no collision)
		"""
		return self.hitbox.collide_any(others, sacrifice_MTV)

	def _calc_coords(self):
		self.hitbox._calc_coords()
		self.render.position = self.hitbox.coords[0]

	@property
	def x(self) -> float:
		"""The x position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.hitbox.x
	
	@x.setter
	def x(self, val: float) -> None:
		self.hitbox.x = val
		self._calc_coords()

	@property
	def y(self) -> float:
		"""The y position of the anchor point.
		
		To set both `.x` and `.y`, use `.pos`.
		"""
		return self.hitbox.y
	
	@y.setter
	def y(self, val: float) -> None:
		self.hitbox.y = val
		self._calc_coords()

	@property
	def pos(self) -> Point2D:
		"""The position of the anchor point."""
		return self.hitbox.pos
	
	@pos.setter
	def pos(self, val: Point2D) -> None:
		self.hitbox.pos = val
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""The x anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self.hitbox.anchor_x

	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self.hitbox._anchor_pos = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""The y anchor of the hitbox.

		To set both `.anchor_x` and `.anchor_y`, use `.anchor_pos`
		"""
		return self.hitbox.anchor_y

	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self.hitbox._anchor_pos = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor_pos(self) -> Point2D:
		"""The anchor of the hitbox."""
		return self.hitbox._anchor_pos

	@anchor_pos.setter
	def anchor_pos(self, val: Point2D) -> None:
		self.hitbox._anchor_pos = val
		self._calc_coords()

	@property
	def angle(self) -> float:
		"""The angle, in radians, of the hitbox"""
		return self.hitbox._angle

	@angle.setter
	def angle(self, val: float) -> None:
		self.hitbox._angle = val
		self._calc_coords()

	@property
	def hitbox_color(self) -> Color:
		"""The color of the hitbox"""
		return self._hitbox_color

	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val.value
