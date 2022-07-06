#coding: utf-8

from color_codes import color_codes
from matrix_settings import Matrix_Settings


class Letter:
	def __init__(self, text):
		self.text = text
		self.letters_codes = text.letters_codes
		self.matrix_settings = text.matrix_settings
		self.color_objects = ['main_color', 'background_color']
		self.background_colored = False

	def set_new_letter(self, letter_index):
		self.letter = self.text.string[letter_index]
		self.letter_index = letter_index
		symbols_array = []
		if self.letter_index in self.text.transformed_decorations:
			decoration_symbols = self.text.transformed_decorations[self.letter_index]
			for decoration_symbol in decoration_symbols:
				self.letter_code = self.letters_codes[decoration_symbol]
				symbols_array.append(self.letter_code)
				symbols_array.append([0])
		
		self.letter_code = self.letters_codes[self.letter]

		if self.text.letters_colors:
			self.get_color_code_from_letters_colors()
		else:
			self.main_color = self.text.main_color
			self.background_color = self.text.background_color

		symbols_array.append(self.letter_code)
		self.letter_code = self.merge_letters(symbols_array)
		self.letter_array = self.get_colored_letter_array()
		self.width = len(self.letter_array)

	def merge_letters(self, full_text_array):
		merged_output_array = []
		for letter in full_text_array:
			for column in letter:
				merged_output_array.append(column)
		return merged_output_array

	def get_color_code_from_letters_colors(self):
		for color_object in self.color_objects:
			if color_object in self.text.letters_colors:
				self.__dict__[color_object] = self.get_color_code_from_letters_colors_for_color_object(color_object)
			else:
				self.__dict__[color_object] = self.text.__dict__[color_object]
		
	def get_color_code_from_letters_colors_for_color_object(self, color_object):
		if self.letter_index in self.text.letters_colors[color_object]:
			color_code = color_codes[self.text.letters_colors[color_object][self.letter_index]]
			if color_object == 'background_color':
				self.background_colored = color_code
			else:
				self.background_colored = False
		else:
			color_code = self.text.__dict__[color_object]
		return color_code
	
	def get_colored_letter_array(self):
		colored_letter_code = []
		for column in self.letter_code:
			colored_letter_column_code = [self.background_color for row in range(self.matrix_settings.height)]
			if (column == type(str())):
				binary_row = column
			else:
				binary_row = bin(column)[2:]
			row_number = self.matrix_settings.height - len(binary_row)
			for bit in binary_row:
				if int(bit):
					colored_letter_column_code[row_number] = self.main_color
				row_number += 1
			colored_letter_code.append(colored_letter_column_code)
		return colored_letter_code