from __future__ import annotations
from typing import Literal
import math

import pyglet
from pyglet.math import Vec2
from pyglet.graphics import Batch, Group
from pyglet.shapes import Polygon, Circle
from ..types import *


class Hitbox:
	"""Store a convex hitbox that uses SAT (Separating Axis Theorem) method for collision.

	Can use `from_rect` to get coords for rectangle
	"""

	_global_anchor_pos: Point2D = 0, 0
	_anchor_coords: tuple[Point2D, ...] = tuple()
	_raw_coords: tuple[Point2D, ...] = tuple()
	_anchor_pos: Point2D = 0, 0
	_angle: float = 0

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
		if len(coords) <= 2:
			raise ValueError(f'Hitbox needs at least 2 coordinates ({len(coords)} passed).')

		self.coords: tuple[Point2D, ...] = coords
		self._global_anchor_pos = coords[0]
		self._raw_coords = coords
		self.anchor_pos = anchor_pos

		self._forced_axes: list[Vec2] = []
		self.is_circle = circle
		self.is_rect = rect

	@staticmethod
	def from_rect(x: float, y: float, width: float, height: float) -> tuple[Point2D, Point2D, Point2D, Point2D]:
		"""Create coords for rectangle hitbox. Not a classmethod due to inheritance issues.

		Args:
			x (float): x position
			y (float): y position
			width (float): Width of rect
			height (float): Height of rect

		Returns:
			tuple[Point2D, Point2D, Point2D, Point2D]: The coords
		"""
		return ((x, y), (x+width, y), (x+width, y+height), (x, y+height))

	def _get_axes(self, remove_dupes: bool) -> list[Vec2]:
		"""Get the normal axes of the hitbox (for SAT). These are perpendicular vectors to each edge.

		Returns:
			list[Vec2]: All of the normal axes as vectors.
		"""

		# Circle only has 1 axis, from forced
		if self.is_circle:
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
		"""Checks if two lines intersect (for SAT). If you want to get the length of intersection, use .get_intersection_length()

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
		"""Gets the length of intersection between 2 lines. (call ._intersect() first) (for SAT)

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
			The object method is invoked on should be the one that will move after the algorithm runs. If not, then use -MTV.
			https://dyn4j.org/2010/01/sat

		Args:
			other (Hitbox): The other hitbox to detect collision with
			sacrifice_MTV (bool, optional): Whether to optimize speed in exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether collision passed and MTV (None if no collision)
		"""

		#* Step 1: Get the normal axes of each edge
		axes = self._get_axes(sacrifice_MTV)
		other_axes = other._get_axes(sacrifice_MTV)

		# These store the length and axis for the MTV
		# MTV: Minimum Translation Vector: Add to current position of self to get out of colliding.
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
			
			#* Step 4: For MTV - Get the smallest intersection length and store it along with the axis
			overlap = self._get_intersection_length(l1, l2)
			if abs(overlap) < abs(MTV_len):
				MTV_len = overlap
				MTV_axis = axis

		return True, MTV_axis * MTV_len
	
	def collide_any(self, hitboxes: list[Hitbox], sacrifice_MTV: bool=False) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to check if self colliding with any of the hitboxes

		Args:
			hitboxes (list[Hitbox]): List of hitboxes to check collision with self
			sacrifice_MTV (bool, optional): Whether to optimize speed in exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether collision passed and MTV (None if no collision)
		"""
		for rect in hitboxes:
			if (collision_info:= self.collide(rect, sacrifice_MTV))[0]:
				return collision_info
			
		return False, None
	
	@staticmethod
	def circle_collide(circle: Circle, hitbox: Hitbox, sacrifice_MTV) -> tuple[Literal[False], None] | tuple[Literal[True], Vec2]:
		"""Runs the SAT algorithm to check if circle colliding with hitbox

		Args:
			circle (Circle): Circle
			hitbox (Hitbox): Hitbox to check collision with
			sacrifice_MTV (bool, optional): Whether to optimize speed in exchange for no MTV. Defaults to False.

		Returns:
			tuple[Literal[False], None] | tuple[Literal[True], Vec2]: Whether collision passed and MTV (None if no collision)
		"""

		def get_projection(v1: Vec2, v2: Vec2) -> Vec2:
			"""Projects v1 onto v2, but clamps 1D value before multiplying by v2

			Args:
				v1 (Vec2): Vector #1
				v2 (Vec2): Vector #2

			Returns:
				Vec2: The projection
			"""
			return pyglet.math.clamp(v1.dot(v2) / v2.length_squared(), 0, 1) * v2
		
		# Save for later
		center = circle.position

		# Convert to hitbox
		converted_circle = Hitbox((center, (circle.radius, 0)), circle=True)

		# Get closest point to other hitbox
		least = Vec2(0, 0), float('inf')
		for i in range(len(hitbox.coords)): # Loop through each axis on polygon
			# Grabbing vertex positions
			p1, p2 = hitbox.coords[i], hitbox.coords[(i+1) % len(hitbox.coords)]

			# Calculates the vector between them
			vec = Vec2(p2[0] - p1[0], p2[1] - p1[1])

			# Vector from vertex to center of circle
			pre_proj = Vec2(
				center[0] - p1[0],
				center[1] - p1[1]
			)
			
			proj = get_projection(pre_proj, vec)
			diff = proj - pre_proj

			# Update least
			if (length:= diff.length()) < least[1]:
				least = diff, length

		converted_circle._forced_axes.append(least[0])
		return converted_circle.collide(hitbox, sacrifice_MTV)

	def calc_coords(self) -> None:
		"""Updates coordinates based on new start_coords, angle, and/or anchor_pos"""
		self._calc_anchor_coords()

		# Get actual vertices
		self.coords = []
		for x, y in self._anchor_coords:
			new_x = x * math.cos(self.angle) - y * math.sin(self.angle)
			new_y = x * math.sin(self.angle) + y * math.cos(self.angle)
			self.coords.append((new_x + self._raw_coords[0][0], new_y + self._raw_coords[0][1]))

	def _calc_anchor_coords(self) -> None:
		"""Updates anchor coordinates (when anchor position changes)"""
		bottomleft_anchor = -self.anchor_x, -self.anchor_y
		self._anchor_coords = tuple(
			(
				bottomleft_anchor[0] + coord[0] - self._global_anchor_pos[0],
				bottomleft_anchor[1] + coord[1] - self._global_anchor_pos[1],
			)
			for coord in self._raw_coords
		)

	def move_to(self, x: float, y: float) -> None:
		"""Move the hitbox to a location based on anchor

		Args:
			pos (Point2D): The anchored position to move to
		"""
		# Calculate translation using old and new pos
		trans = x - self._global_anchor_pos[0], y - self._global_anchor_pos[1]
		print(trans)
		# Translate coords
		self._raw_coords = tuple((coord[0] + trans[0], coord[1] + trans[1]) for coord in self._raw_coords)
		
		self._global_anchor_pos = x, y
		self.calc_coords()

	@property
	def anchor_x(self) -> float:
		"""Anchor on x-axis"""
		return self._anchor_pos[0]
	@anchor_x.setter
	def anchor_x(self, val: float) -> None:
		trans = self.anchor_x - val
		self._anchor_pos = val, self.anchor_y
		self.move_to(self._global_anchor_pos[0] + trans, self._global_anchor_pos[1])

	@property
	def anchor_y(self) -> float:
		"""Anchor on y-axis"""
		return self._anchor_pos[1]
	@anchor_y.setter
	def anchor_y(self, val: float) -> None:
		trans = self.anchor_y - val
		self._anchor_pos = self.anchor_x, val
		self.move_to(self._global_anchor_pos[0], self._global_anchor_pos[1] + trans)

	@property
	def anchor_pos(self) -> Point2D:
		"""Anchor position (x, y)"""
		return self._anchor_pos
	@anchor_pos.setter
	def anchor_pos(self, val: Point2D) -> None:
		trans = self.anchor_x - val[0], self.anchor_y - val[1]
		self._anchor_pos = val
		self.move_to(self._global_anchor_pos[0] + trans[0], self._global_anchor_pos[1] + trans[1])

	@property
	def angle(self) -> float:
		"""Angle, in radians, of hitbox"""
		return self._angle
	@angle.setter
	def angle(self, val: float) -> None:
		self._angle = val
		self.calc_coords()


class HitboxRender(Hitbox):
	"""Holds a Hitbox with a `render` object to render the hitbox"""

	_hitbox_color = Color.BLACK
	
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

	def calc_coords(self):
		super().calc_coords()

		# Update polygon render
		self.render._coordinates = self._raw_coords
		self.render._update_vertices()
		self.render.x = self._raw_coords[0][0]
		self.render.y = self._raw_coords[0][1]

	@property
	def hitbox_color(self) -> Color:
		"""Color of hitbox"""
		return self._hitbox_color
	@hitbox_color.setter
	def hitbox_color(self, val: Color) -> None:
		self._hitbox_color = val
		self.render.color = val.value
