from __future__ import annotations
from typing import Literal, Self, NoReturn
import math

import pyglet
from pyglet.math import Vec2
from pyglet.graphics import Batch, Group
from pyglet.shapes import Polygon, Circle
from ..types import *


class Hitbox:
	"""Store a convex hitbox that uses SAT (Separating Axis Theorem) method for collision.

	Can use `from_rect` to get coords for rectangle or `from_circle` for a circle hitbox
	(coords are not accurate but optimized for collisions)

	For _coord vars, there are 3 types of transformation
	
	- translated: Adding global position of hitbox to local position (moving in 2D space)
	
	- rotated: Adding the rotation of the hitbox
	
	- anchored, shifting global position to account for anchor position of hitbox
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
	_forced_axes: list[Vec2]
	"""The axes that are forcibly added on top of normal axes (used for circles)"""
	is_circle: bool
	"""Whether hitbox is a circle (for SAT)"""
	is_rect: bool
	"""Whether hitbox is a rectangle (for SAT)"""

	def __init__(self,
			coords: tuple[Point2D, ...],
			anchor_pos: Point2D=(0, 0),
			*, circle: bool=False, rect: bool=False
	) -> None:
		"""Create a hitbox.

		Args:
			coords (tuple[Point2D, ...]): The coordinates of the hitbox
			anchor_pos (Point2D, optional): The starting anchor position. Defaults to (0, 0).
			circle (bool, optional): Whether hitbox is a circle (for SAT). Defaults to False.
			rect (bool, optional): Whether hitbox is a rectangle (for SAT). Defaults to False.
		"""

		if circle and rect:
			raise ValueError(f'Hitbox cannot be both a circle and rectangle.')
		if len(coords) < 2:
			raise ValueError(f'Hitbox needs at least 2 coordinates ({len(coords)} passed).')

		self._trans_pos = coords[0]
		self._raw_coords = coords
		self.anchor_pos = anchor_pos

		self._forced_axes = []
		self.is_circle = circle
		self.is_rect = rect

	@classmethod
	def from_rect(cls,
			x: float,
			y: float,
			width: float,
			height: float,
			anchor_pos: Point2D
	) -> Self:
		"""Create a hitbox from rectangle args.

		Args:
			x (float): x position
			y (float): y position
			width (float): Width of rect
			height (float): Height of rect
			anchor_pos (Point2D): Anchor position
		"""
		return cls(
			(x, y),
			(x+width, y),
			(x+width, y+height),
			(x, y+height),
			anchor_pos, rect=True
		)

	@classmethod
	def from_circle(cls, circle: Circle) -> Self:
		"""Create a hitbox from a circle.

		Args:
			circle (Circle): The circle to make the hitbox from
		"""
		return cls(((circle.x - circle.anchor_x, circle.y - circle.anchor_y), (circle.radius, 0)), circle=True)

	def _get_axes(self, remove_dupes: bool) -> list[Vec2]:
		"""Get the normal axes of the hitbox (for SAT).
		
		These are perpendicular vectors to each edge.

		Returns:
			list[Vec2]: All of the normal axes as vectors.
		"""

		# Circle only has 1 axis, from forced
		if self.is_circle:
			print(self._forced_axes)
			return self._get_forced_axes()

		axes = []

		# Loops through vertices and gets all adjacent pairs
		for i in range(len(self.coords) // (2 if remove_dupes and self.is_rect else 1)):
			# Grabbing vertex positions
			p1, p2 = self.coords[i], self.coords[(i+1) % len(self.coords)]

			# Calculates the vector between them
			vec = p1[0] - p2[0], p1[1] - p2[1]
			# Gets perpendicular vector and normalizes it
			# Normalizing helps get MTV
			axes.append(Vec2(-vec[1], vec[0]).normalize())

		return axes + self._get_forced_axes()
	
	def _get_forced_axes(self) -> list[Vec2]:
		"""Gets the normalized (NOT NORMALS) forced axes (for SAT)

		Returns:
			list[Vec2]: The normals of the forced axes
		"""
		return list(map(lambda axis: axis.normalize(), self._forced_axes))
	
	def _project(self, axis: Vec2) -> tuple[float, float]:
		"""Projects the hitbox onto an axis (use self._get_axes()) (for SAT)

		Args:
			axis (Vec2): The normal axis to project onto

		Returns:
			tuple[float, float]: The left and right side, respectively, of the projected line
		"""

		# Circle has simple projection
		if self.is_circle:
			proj = axis.dot(Vec2(*self.coords[0]))
			return proj - self.coords[1][0], proj + self.coords[1][0]

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

		Args:
			l1 (tuple[float, float]): Line #1
			l2 (tuple[float, float]): Line #2

		Returns:
			bool: Whether lines intersect
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
	def _get_intersection_length(l1: tuple[float, float], l2: tuple[float, float]) -> float:
		"""Gets the length of intersection between 2 lines. (for SAT)

		Args:
			l1 (tuple[float, float]): Line #1
			l2 (tuple[float, float]): Line #2

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

		Args:
			l1 (tuple[float, float]): Line #1
			l2 (tuple[float, float]): Line #2

		Returns:
			bool: Whether one of the lines is completely contained within other line
		"""
		return (l1[0] < l2[0] and l1[1] > l2[1]) or (l2[0] < l1[0] and l2[1] > l1[1])
	
	def collide(self, other: Hitbox, sacrifice_MTV: bool=False) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to determine if 2 objects are colliding.
		
		The object method is invoked on should be the one that will move after
			the algorithm runs. If not, then make MTV negative. https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox): The other hitbox to detect collision with
			sacrifice_MTV (bool, optional): Whether to optimize speed in
				exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
			collision passed and MTV (None if no collision)
		"""

		#* Step 1: Get the normal axes of each edge
		axes = self._get_axes(sacrifice_MTV)
		other_axes = other._get_axes(sacrifice_MTV)

		# These store the length and axis for the MTV
		MTV_len = float('inf')
		MTV_axis = Vec2(0, 0)

		#* Step 2: Project the shapes onto each axis
		for axis in axes + other_axes:
			l1 = self._project(axis)
			l2 = other._project(axis)

			#* Step 3: Check for intersection
			#* If the projections do not intersect, there cannot be a collision
			if not self._intersect(l1, l2):
				return False, None
			
			#* Step 4: For MTV - Get the smallest intersection length
			#*	and store it along with the axis
			overlap = self._get_intersection_length(l1, l2)
			if abs(overlap) < abs(MTV_len):
				MTV_len = overlap
				MTV_axis = axis

		return True, MTV_axis * MTV_len
	
	def collide_any(self,
			hitboxes: list[Hitbox],
			sacrifice_MTV: bool=False
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm on a list of hitboxes.

		Args:
			hitboxes (list[Hitbox]): List of hitboxes to check collision with self
			sacrifice_MTV (bool, optional): Whether to optimize speed in
				exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
			collision passed and MTV (None if no collision)
		"""
		for rect in hitboxes:
			if (collision_info:= self.collide(rect, sacrifice_MTV))[0]:
				return collision_info
			
		return False, None
	
	@staticmethod
	def circle_collide(
			circle: Circle,
			hitbox: Hitbox,
			sacrifice_MTV: bool=False
	) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to check if circle colliding with hitbox

		Args:
			circle (Circle): Circle
			hitbox (Hitbox): Hitbox to check collision with
			sacrifice_MTV (bool, optional): Whether to optimize speed in
				exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether
			collision passed and MTV (None if no collision)
		"""

		def get_projection(v1: Vec2, v2: Vec2) -> Vec2:
			"""Projects v1 onto v2, but clamps 1D value before multiplying by v2

			Args:
				v1 (Vec2): Vector #1
				v2 (Vec2): Vector #2

			Returns:
				Vec2: The projection
			"""

			# Clamping forces the projection to be within the 2 vertices of the polygon
			#	(or 2 endpoints of v2) by forcing scale factor to be from 0-1
			#	This facilitates finding closest points on polygon to circle center
			return pyglet.math.clamp(v1.dot(v2) / v2.length_squared(), 0, 1) * v2

		# Convert to hitbox
		converted_circle = Hitbox.from_circle(circle)

		# Get closest point to other hitbox
		least = Vec2(0, 0), float('inf')
		for i in range(len(hitbox.coords)): # Loop through each axis on polygon
			# Grabbing vertex positions
			p1, p2 = hitbox.coords[i], hitbox.coords[(i+1) % len(hitbox.coords)]

			# Calculates the vector between vertices
			vec = Vec2(p2[0] - p1[0], p2[1] - p1[1])

			# Vector from vertex to center of circle
			pre_proj = Vec2(
				circle.x - p1[0],
				circle.y - p1[1]
			)
			
			# Proj holds the vector from p1 to the closest point
			#	on the polygon to the circle center
			proj = get_projection(pre_proj, vec)
			# Subtracting pre_proj gives vector from circle center to closest point
			diff = proj - pre_proj

			# Update least
			if (length:= diff.length()) < least[1]:
				least = diff, length

		converted_circle._forced_axes.append(least[0])
		return converted_circle.collide(hitbox, sacrifice_MTV)

	def _calc_coords(self) -> None:
		"""Updates coordinates based on new , angle, and/or anchor_pos"""

		# Steps:
		#	1. Update local coords
		#	2. Update anchor coords
		#	3. Get displacement caused by rotation of anchor coords
		#	4. Add translation to local to get raw
		#	5. Add anchor rotation displacement to raw to get unanchored
		#	6. Add anchor to unanchored to get final

		# Use the raw coords, which are precalculated in __init__
		#	before first ._calc_coords call
		self._local_coords = tuple(
			(
				coord[0] - self._raw_coords[0][0],
				coord[1] - self._raw_coords[0][1],
			)
			for coord in self._raw_coords
		)

		self._anchor_coords = tuple(
			(
				coord[0] - self.anchor_x,
				coord[1] - self.anchor_y
			)
			for coord in self._local_coords
		)

		self._rotation_amount = tuple(
			(
				self._get_rotated_pos(coord, 'x') - coord[0], # type: ignore[operator]
				self._get_rotated_pos(coord, 'y') - coord[1] # type: ignore[operator]
			)
			for coord in self._anchor_coords
		)

		self._raw_coords = tuple(
			(
				coord[0] + self._trans_pos[0],
				coord[1] + self._trans_pos[1]
			)
			for coord in self._local_coords
		)

		self._unanchored_coords = tuple(
			(
				coord[0] + rotation[0],
				coord[1] + rotation[1]
			)
			for coord, rotation in zip(self._raw_coords, self._rotation_amount)
		)

		self.coords = tuple(
			(
				coord[0] - self.anchor_x,
				coord[1] - self.anchor_y
			)
			for coord in self._unanchored_coords
		)

	def _get_rotated_pos(self, coord: Point2D, axis: Axis) -> float | Point2D:
		"""Gets the rotated point using `angle`.

		Args:
			coord (Point2D): The coordinate to rotate
			axis (Axis): The Axis to calculate it on
		
		Returns:
			float | Point2D: The rotated point or single-axis coord
		"""

		if axis == 'x':
			return coord[0] * math.cos(self.angle) - coord[1] * math.sin(self.angle)
		if axis == 'y':
			return coord[0] * math.sin(self.angle) + coord[1] * math.cos(self.angle)
		
		return (
			coord[0] * math.cos(self.angle) - coord[1] * math.sin(self.angle),
			coord[0] * math.sin(self.angle) + coord[1] * math.cos(self.angle)
		)

	def move_to(self, x: float, y: float) -> None:
		"""Move the hitbox to a location based on anchor

		Args:
			pos (Point2D): The anchored position to move to
		"""
		self._trans_pos = x, y		
		self._calc_coords()

	@property
	def anchor_x(self) -> float:
		"""Anchor on x-axis"""
		return self._anchor_pos[0]
	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		self._anchor_pos = val, self.anchor_y
		self._calc_coords()

	@property
	def anchor_y(self) -> float:
		"""Anchor on y-axis"""
		return self._anchor_pos[1]
	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		self._anchor_pos = self.anchor_x, val
		self._calc_coords()

	@property
	def anchor_pos(self) -> Point2D:
		"""Anchor position (x, y)"""
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


class HitboxRender(Hitbox):
	"""Holds a Hitbox with a `render` object to render the hitbox"""

	_hitbox_color: Color
	
	def __init__(self,
			coords: tuple[Point2D, ...],
			color: Color, batch: Batch, group: Group,
			anchor_pos: Point2D=(0, 0),
			*, circle: bool=False, rect: bool=False
	) -> None:
		"""_summary_

		Args:
			coords (tuple[Point2D, ...]): The coordinates of the hitbox
			color (Color): The color of the hitbox render
			batch (Batch): The batch for rendering
			group (Group): The group for rendering
			anchor_pos (Point2D, optional): The starting anchor position. Defaults to (0, 0).
			circle (bool, optional): Whether hitbox is a circle (for SAT). Defaults to False.
			rect (bool, optional): Whether hitbox is a rectangle (for SAT). Defaults to False.
		"""
		self.render = Polygon(*coords, color=color.value, batch=batch, group=group)
		super().__init__(coords, anchor_pos, circle=circle, rect=rect)

		self._hitbox_color = color

	@classmethod
	def from_rect(cls,
			x: float, y: float,
			width: float, height: float,
			color: Color, batch: Batch, group: Group,
			anchor_pos: Point2D=(0, 0)
	) -> Self:
		"""Create a hitbox render from rectangle dimensions.

		Args:
			x (float): x position
			y (float): y position
			width (float): Width of rect
			height (float): Height of rect
			color (Color): The color of the hitbox render
			batch (Batch): The batch for rendering
			group (Group): The group for rendering
			anchor_pos (Point2D): Anchor position
		"""
		
		coords = (x, y), (x+width, y), (x+width, y+height), (x, y+height)
		return cls(coords, color, batch, group, anchor_pos, rect=True)

	@classmethod
	def from_circle(cls, circle: Circle) -> NoReturn:
		return NotImplementedError(
			'HitboxRender.from_circle() not implemented as it is only used for SAT algorithm.'
		)

	def _calc_coords(self):
		super()._calc_coords()

		# Update polygon render
		self.render._coordinates = self.coords
		self.render._update_vertices()
		self.render.x = self.coords[0][0]
		self.render.y = self.coords[0][1]

	@property
	def hitbox_color(self) -> Color:
		"""Color of hitbox"""
		return self._hitbox_color
	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val.value
