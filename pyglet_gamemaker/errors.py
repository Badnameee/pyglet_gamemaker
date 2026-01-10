from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from pathlib import PurePath
	from typing import Any


class MissingConfigKey(KeyError):
	"""Missing configuration key in .yaml file."""

	hierarchy: Any | tuple[Any, ...]

	def __init__(self, hierarchy: Any | tuple[Any, ...]) -> None:
		self.hierarchy = hierarchy

	def __str__(self) -> str:
		if isinstance(self.hierarchy, tuple):
			s = ' -> '.join(map(str, self.hierarchy))
		else:
			s = str(self.hierarchy)
		return f'{self.__class__.__name__}: {s}'


class InvalidConfigKeyType(TypeError):
	"""Invalid key type in .yaml file."""

	hierarchy: Any | tuple[Any, ...]
	expected: type | tuple[type, ...]
	actual: type

	def __init__(
		self,
		hierarchy: Any | tuple[Any, ...],
		expected: type | tuple[type, ...],
		actual: type,
	) -> None:
		self.hierarchy, self.expected, self.actual = hierarchy, expected, actual

	def __str__(self) -> str:
		if isinstance(self.hierarchy, tuple):
			s = ' -> '.join(map(str, self.hierarchy))
		else:
			s = str(self.hierarchy)

		s += '  |  Expected key type '
		if isinstance(self.expected, tuple):
			s += ' | '.join(map(lambda type: type.__name__, self.expected))
		else:
			s += self.expected.__name__

		s += f', got type {self.actual} instead.'
		return f'{self.__class__.__name__}: {s}'


class InvalidConfigValueType(TypeError):
	"""Invalid value type in .yaml file."""

	hierarchy: Any | tuple[Any, ...]
	expected: type | tuple[type, ...]
	actual: type

	def __init__(
		self,
		hierarchy: Any | tuple[Any, ...],
		expected: type | tuple[type, ...],
		actual: type,
	) -> None:
		self.hierarchy, self.expected, self.actual = hierarchy, expected, actual

	def __str__(self) -> str:
		if isinstance(self.hierarchy, tuple):
			s = ' -> '.join(map(str, self.hierarchy))
		else:
			s = self.hierarchy

		s += '  |  Expected value type '
		if isinstance(self.expected, tuple):
			s += ' | '.join(map(lambda type: type.__name__, self.expected))
		else:
			s += self.expected.__name__

		s += f', got type {self.actual} instead.'
		return f'{self.__class__.__name__}: {s}'


class InvalidConfigValue(TypeError):
	"""Invalid value in .yaml file."""

	hierarchy: Any | tuple[Any, ...]
	expected: str
	actual: Any

	def __init__(
		self, hierarchy: Any | tuple[Any, ...], expected_format: str, actual: Any
	) -> None:
		self.hierarchy, self.expected_format, self.actual = (
			hierarchy,
			expected_format,
			actual,
		)

	def __str__(self) -> str:
		if isinstance(self.hierarchy, tuple):
			s = ' -> '.join(map(str, self.hierarchy))
		else:
			s = str(self.hierarchy)

		s += f'  |  Expected value of format "{self.expected_format}", got {self.actual} instead.'
		return f'{self.__class__.__name__}: {s}'


class InvalidConfigFile(RuntimeError):
	file_path: PurePath
	errors: list[Exception]

	def __init__(self, file_path: PurePath, errors: list[Exception]) -> None:
		self.errors = errors
		self.file_path = file_path

	def __str__(self) -> str:
		s = f'{len(self.errors)} config errors determined inside "{self.file_path}":\n'
		for error in self.errors:
			s += f'\n{error}'

		return s


class EmptyConfigFile(ValueError):
	"""Empty .yaml file."""

	file_path: PurePath

	def __init__(self, file_path: PurePath) -> None:
		self.file_path = file_path

	def __str__(self) -> str:
		s = f'Empty config file at "{self.file_path}".'

		return s
