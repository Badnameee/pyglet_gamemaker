from __future__ import annotations

from pathlib import PurePath
from typing import TYPE_CHECKING

import yaml

from ..errors import (
	EmptyConfigFile,
	InvalidConfigFile,
	InvalidConfigKeyType,
	InvalidConfigValue,
	InvalidConfigValueType,
	MissingConfigKey,
)

if TYPE_CHECKING:
	from pathlib import Path
	from typing import Callable

	from ..types import YAMLDict, YAMLValidationType


class YAMLValidator:
	file_path: Path
	yaml: YAMLDict
	validation_func: Callable[..., list[Exception]]

	def __init__(self, file_path: Path, validation_type: YAMLValidationType) -> None:
		self.file_path = file_path

		with open(self.file_path) as file:
			self.yaml = yaml.safe_load(file)

		if validation_type == 'Anim':
			self.validation_func = self._validate_anim
			return

		raise NotImplementedError(
			f'{validation_type} not in currently supported validation types'
		)

	def validate(self) -> list[Exception]:
		return self.validation_func()

	def _validate_anim(self) -> list[Exception]:
		# See `~pgm.sprite.animation.AnimationList` for more on format
		# NOTE: I tried to automate this but the validation was too specific

		if self.yaml is None:
			raise EmptyConfigFile(self.file_path)

		errors: list[Exception] = []

		# Conditions of yaml file that affect future validation
		conditions = {
			'rows': False,
			'cols': False,
			'delimiter': False,
			'void': False,
			'anim-data': False,
		}

		# rows: {int > 0}
		if 'rows' not in self.yaml:
			errors.append(MissingConfigKey('rows'))
		elif not isinstance(self.yaml['rows'], int):
			errors.append(InvalidConfigValueType('rows', int, type(self.yaml['rows'])))
		elif self.yaml['rows'] <= 0:
			errors.append(InvalidConfigValue('rows', '{value} > 0', self.yaml['rows']))
		else:
			conditions['rows'] = True

		# cols: {int > 0}
		if 'cols' not in self.yaml:
			errors.append(MissingConfigKey('cols'))
		elif not isinstance(self.yaml['cols'], int):
			errors.append(InvalidConfigValueType('cols', int, type(self.yaml['cols'])))
		elif self.yaml['cols'] <= 0:
			errors.append(InvalidConfigValue('cols', '{value} > 0', self.yaml['cols']))
		else:
			conditions['cols'] = True

		# row-padding: {int >= 0}
		if 'row-padding' not in self.yaml:
			errors.append(MissingConfigKey('row-padding'))
		elif not isinstance(self.yaml['row-padding'], int):
			errors.append(
				InvalidConfigValueType('row-padding', int, type(self.yaml['row-padding']))
			)
		elif self.yaml['row-padding'] < 0:
			errors.append(
				InvalidConfigValue('row-padding', '{value} >= 0', self.yaml['row-padding'])
			)

		# col-padding: {int >= 0}
		if 'col-padding' not in self.yaml:
			errors.append(MissingConfigKey('col-padding'))
		elif not isinstance(self.yaml['col-padding'], int):
			errors.append(
				InvalidConfigValueType('col-padding', int, type(self.yaml['col-padding']))
			)
		elif self.yaml['col-padding'] < 0:
			errors.append(
				InvalidConfigValue('col-padding', '{value} >= 0', self.yaml['col-padding'])
			)

		# top-down: {bool}
		if 'top-down' not in self.yaml:
			errors.append(MissingConfigKey('top-down'))
		elif not isinstance(self.yaml['top-down'], bool):
			errors.append(
				InvalidConfigValueType('top-down', bool, type(self.yaml['top-down']))
			)

		# delimiter: {str}
		if 'delimiter' not in self.yaml:
			errors.append(MissingConfigKey('delimiter'))
		elif not isinstance(self.yaml['delimiter'], str):
			errors.append(
				InvalidConfigValueType('delimiter', str, type(self.yaml['delimiter']))
			)
		else:
			conditions['delimiter'] = True

		# void: {str}
		if 'void' not in self.yaml:
			errors.append(MissingConfigKey('void'))
		elif not isinstance(self.yaml['void'], str):
			errors.append(InvalidConfigValueType('void', str, type(self.yaml['void'])))
		else:
			conditions['void'] = True

		# anim-data: {dict}
		if 'anim-data' not in self.yaml:
			errors.append(MissingConfigKey('anim-data'))
		elif not isinstance(self.yaml['anim-data'], dict):
			errors.append(
				InvalidConfigValueType('anim-data', dict, type(self.yaml['anim-data']))
			)

		# anim-data -> {str}: {dict}
		else:
			conditions['anim-data'] = True
			for alias, data in self.yaml['anim-data'].items():
				if not isinstance(alias, str):
					errors.append(
						InvalidConfigValueType(('anim-data', alias), str, type(alias))
					)
				if not isinstance(data, dict):
					errors.append(
						InvalidConfigValueType(('anim-data', alias), dict, type(data))
					)

				# void -> alias: { name: {str}, fps: {float > 0}, loop: {bool} }
				else:
					if 'name' not in self.yaml['anim-data'][alias]:
						errors.append(MissingConfigKey(('anim-data', alias, 'name')))
					elif not isinstance(self.yaml['anim-data'][alias]['name'], str):
						errors.append(
							InvalidConfigValueType(
								('anim-data', alias, 'name'),
								str,
								type(self.yaml['anim-data'][alias]['name']),
							)
						)

					if 'fps' not in self.yaml['anim-data'][alias]:
						errors.append(MissingConfigKey(('anim-data', alias, 'fps')))
					elif not isinstance(self.yaml['anim-data'][alias]['fps'], float | int):
						errors.append(
							InvalidConfigValueType(
								('anim-data', alias, 'fps'),
								(float, int),
								type(self.yaml['anim-data'][alias]['fps']),
							)
						)
					elif self.yaml['anim-data'][alias]['fps'] <= 0:
						errors.append(
							InvalidConfigValue(
								'col-padding', '{value} >= 0', self.yaml['col-padding']
							)
						)

		# data: {list}
		if 'data' not in self.yaml:
			errors.append(MissingConfigKey('data'))
		elif not isinstance(self.yaml['data'], list):
			errors.append(InvalidConfigValueType('data', list, type(self.yaml['data'])))

		# data -> list[ {list} * {rows} ]
		else:
			if conditions['rows'] and len(self.yaml['data']) != self.yaml['rows']:
				errors.append(
					InvalidConfigValue(
						'data', f'len() == {self.yaml["rows"]}', len(self.yaml['data'])
					)
				)

			for row_num, row in enumerate(self.yaml['data']):
				# Get row number error message
				row_num_error = f'{{Row #{row_num + 1}}}'

				if not isinstance(row, list):
					errors.append(
						InvalidConfigValueType(('data', row_num_error), list, type(row))
					)

				# data -> list[ list[ ... * {cols} ] ]
				else:
					if conditions['cols'] and len(row) != self.yaml['cols']:
						errors.append(
							InvalidConfigValue(
								('data', row_num_error),
								f'len() == {self.yaml["cols"]}',
								len(self.yaml['data']),
							)
						)

					# data -> list[
					# 	list[
					# 		{
					# 			{alias}{delimiter}{int > 0} | {void}
					# 		} * cols
					# ]
					# ]
					for col_num, id in enumerate(row):
						# Get column number error message
						col_num_error = f'{{Col #{col_num + 1}}}'

						if not isinstance(id, str):
							errors.append(
								InvalidConfigValueType(
									('data', row_num_error, col_num_error),
									list,
									type(row),
								)
							)
						else:
							if conditions['void'] and id == self.yaml['void']:
								continue

							if not conditions['delimiter']:
								conditions

							alias, delimiter, frame_num = id.partition(
								self.yaml['delimiter']
							)

							if (
								(
									conditions['anim-data']
									and alias not in self.yaml['anim-data']
								)
								or delimiter != self.yaml['delimiter']
								or not frame_num.isdigit()
								or int(frame_num) <= 0
							):
								errors.append(
									InvalidConfigValue(
										('data', row_num_error, col_num_error),
										f'{{alias}}{self.yaml["delimiter"]}{{int > 0}} | {self.yaml["void"]}',
										id,
									)
								)

		(
			MissingConfigKey,
			InvalidConfigValueType,
			InvalidConfigFile,
			InvalidConfigValue,
			InvalidConfigKeyType,
		)

		return errors
