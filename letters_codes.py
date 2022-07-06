#coding: utf-8

import os
import json


class Letters_Codes():

	letters_codes = {
		" ": [0b0, 0b0],
		"+": [0b00001000, 0b00011100, 0b00001000],
		"-": [0b00001000, 0b00001000],
		"–": [0b00001000, 0b00001000, 0b00001000],
		"_": [0b00000001, 0b00000001, 0b00000001],
		"!": [0b11111101],
		"?": [0b01000000, 0b10001101, 0b01110000],
		".": [0b00000001],
		",": [0b00000011],
		"=": [0b00010100, 0b00010100],
		"(": [0b01111110, 0b10000001],
		")": [0b10000001, 0b01111110],
		"[": [0b11111111, 0b10000001],
		"]": [0b10000001, 0b11111111],
		":": [0b00010100],
		";": [0b00010011],
		"{": [0b00001000, 0b01111110, 0b10000001],
		"}": [0b10000001, 0b01111110, 0b00001000],
		"<": [0b00001000, 0b00010100, 0b00100010],
		">": [0b00100010, 0b00010100, 0b00001000],
		"/": [0b00000111, 0b00111000, 0b11000000],
		"|": [0b11111111],
		"\\": [0b11000000, 0b00111000, 0b00000111],
		"'": [0b11000000],
		'"': [0b11000000, 0b11000000],
		"\"": [0b00110000, 0b00110000],
		"*": [0b00101010, 0b00011100, 0b00111110, 0b00011100, 0b00101010],
		"#": [0b00010100, 0b00111110, 0b00010100, 0b00111110, 0b00010100],
		"№": [0b11111111, 0b00100000, 0b00010000, 0b00001000, 0b11111111, 0b0, 0b00110100, 0b00110100],
		"$": [0b01110010, 0b010100010, 0b1111111, 0b01010010, 0b01011110],
		"%": [0b10000111, 0b00111000, 0b11000001],
		"^": [0b00100000, 0b01000000, 0b00000000, 0b01000000, 0b00100000],
		"&": [0b01101110, 0b10010001, 0b10010001, 0b01101110, 0b00000101],
		"`": [0b10000000, 0b01000000],
		"~": [0b00001000, 0b00010000, 0b00001000, 0b00010000],
		"\t": [0b0, 0b0, 0b0, 0b0],
		"\n": [0b0, 0b0, 0b0, 0b0],
		"\r": [0b0, 0b0, 0b0, 0b0],
		"\0": [0b0, 0b0, 0b0, 0b0],
		"□": [0b01111110, 0b01000010, 0b01111110],
		"Ɒ": [0b01111110, 0b01000010, 0b01111110],
		"0": [0b11111111, 0b10000001, 0b10000001, 0b11111111],
		"1": [0b01000001, 0b11111111, 0b00000001],
		"2": [0b01100011, 0b10000101, 0b10001001, 0b01110001],
		"3": [0b01100010, 0b10000001, 0b10010001, 0b01101110],
		"4": [0b00110000, 0b01010000, 0b10010000, 0b11111111],
		"5": [0b11110001, 0b10010001, 0b10010001, 0b10001110],
		"6": [0b01111110, 0b10010001, 0b10010001, 0b01001110],
		"7": [0b10000000, 0b10011111, 0b10100000, 0b11000000],
		"8": [0b01101110, 0b10010001, 0b10010001, 0b01101110],
		"9": [0b01110010, 0b10001001, 0b10001001, 0b01111110],
		"A": [0b00111111, 0b01001000, 0b10001000, 0b01001000, 0b00111111],
		"Â": [0b00000111, 0b01001010, 0b10010010, 0b01001010, 0b00000111],
		"À": [0b00000111, 0b10001010, 0b01010010, 0b00001010, 0b00000111],
		"B": [0b11111111, 0b10010001, 0b10010001, 0b01101110],
		"C": [0b11111111, 0b10000001, 0b10000001, 0b10000001],
		"Ç": [0b11111100, 0b10000101, 0b10000111, 0b10000100],
		"Ć": [0b00011111, 0b01010001, 0b10010001, 0b00010001],
		"D": [0b11111111, 0b10000001, 0b10000001, 0b01111110],
		"E": [0b11111111, 0b10010001, 0b10010001, 0b10010001],
		"É": [0b00011111, 0b01010101, 0b10010101, 0b00010001],
		"È": [0b00011111, 0b10010101, 0b01010101, 0b00010001],
		"Ê": [0b00011111, 0b01010101, 0b10010101, 0b01010001],
		"Ë": [0b10111111, 0b00101001, 0b00101001, 0b10100001],
		"F": [0b11111111, 0b10010000, 0b10010000, 0b10010000],
		"G": [0b11111111, 0b10000001, 0b10001001, 0b11001111],
		"H": [0b11111111, 0b00010000, 0b00010000, 0b11111111],
		"I": [0b10000001, 0b11111111, 0b10000001],
		"Ì": [0b10010001, 0b01011111, 0b00010001],
		"Î": [0b01010001, 0b10011111, 0b01010001],
		"Ï": [0b10100001, 0b00111111, 0b10100001],
		"J": [0b00000110, 0b00000001, 0b00000001, 0b11111110],
		"K": [0b11111111, 0b00010000, 0b00010000, 0b00101000, 0b11000111],
		"L": [0b11111111, 0b00000001, 0b00000001, 0b00000001],
		"M": [0b11111111, 0b01000000, 0b00100000, 0b01000000, 0b11111111],
		"N": [0b11111111, 0b00100000, 0b00010000, 0b00001000, 0b11111111],
		"O": [0b11111111, 0b10000001, 0b10000001, 0b11111111],
		"Ö": [0b10111111, 0b00100001, 0b00100001, 0b10111111],
		"P": [0b11111111, 0b10010000, 0b10010000, 0b11110000],
		"Q": [0b11111100, 0b10000111, 0b10000101, 0b11111100],
		"R": [0b11111111, 0b10011000, 0b10010100, 0b11110011],
		"S": [0b11110001, 0b10010001, 0b10010001, 0b10011111],
		"T": [0b10000000, 0b10000000, 0b11111111, 0b10000000, 0b10000000],
		"U": [0b11111110, 0b00000001, 0b00000001, 0b11111110],
		"Ü": [0b10111110, 0b00000001, 0b00000001, 0b10111110],
		"Û": [0b00011110, 0b01000000, 0b10000001, 0b01000000, 0b00011110],
		"Ù": [0b00011110, 0b10000001, 0b01000001, 0b00011110],
		"V": [0b11111100, 0b00000010, 0b00000001, 0b00000010, 0b11111100],
		"W": [0b11111100, 0b00000010, 0b00000001, 0b00000110, 0b00000001, 0b00000010, 0b11111100],
		"X": [0b11000111, 0b00101000, 0b00010000, 0b00101000, 0b11000111],
		"Y": [0b11100000, 0b00010000, 0b00001111, 0b00010000, 0b11100000],
		"Ÿ": [0b00110000, 0b10001000, 0b00000111, 0b10001000, 0b00110000],
		"Z": [0b10000011, 0b10001101, 0b10110001, 0b11000001],
		"e": [0b11111, 0b10101, 0b11101],
		"x": [0b11011, 0b100, 0b11011],
		"t": [0b10000, 0b111111, 0b10001],
		"А": [0b00111111, 0b01001000, 0b10001000, 0b01001000, 0b00111111],
		"Б": [0b11111111, 0b10010001, 0b10010001, 0b10011111],
		"В": [0b11111111, 0b10010001, 0b10010001, 0b01101110],
		"Г": [0b11111111, 0b10000000, 0b10000000, 0b10000000],
		"Д": [0b00000011, 0b11111110, 0b10000010, 0b11111110, 0b00000011],
		"Е": [0b11111111, 0b10010001, 0b10010001, 0b10000001],
		"Ё": [0b10111111, 0b00101001, 0b00101001, 0b10100001],
		"Ж": [0b11101111, 0b00010000, 0b11111111, 0b00010000, 0b11101111],
		"З": [0b10000001, 0b10010001, 0b10010001, 0b01101110],
		"И": [0b11111111, 0b00001000, 0b00010000, 0b00100000, 0b11111111],
		"Й": [0b00111111, 0b10000100, 0b10001000, 0b10010000, 0b00111111],
		"К": [0b11111111, 0b00010000, 0b00010000, 0b00101000, 0b11000111],
		"Л": [0b00111111, 0b01000000, 0b10000000, 0b01000000, 0b00111111],
		"М": [0b11111111, 0b01000000, 0b00100000, 0b01000000, 0b11111111],
		"Н": [0b11111111, 0b00010000, 0b00010000, 0b11111111],
		"О": [0b11111111, 0b10000001, 0b10000001, 0b11111111],
		"П": [0b11111111, 0b10000000, 0b10000000, 0b11111111],
		"Р": [0b11111111, 0b10010000, 0b10010000, 0b11110000],
		"С": [0b11111111, 0b10000001, 0b10000001, 0b10000001],
		"Т": [0b10000000, 0b10000000, 0b11111111, 0b10000000, 0b10000000], #0xd2
		"У": [0b11110001, 0b00010001, 0b00010001, 0b11111111],
		"Ф": [0b01110000, 0b10001000, 0b11111111, 0b10001000, 0b01110000],
		"Х": [0b11000111, 0b00101000, 0b00010000, 0b00101000, 0b11000111],
		"Ц": [0b11111110, 0b00000010, 0b00000010, 0b11111110, 0b00000011],
		"Ч": [0b11110000, 0b00010000, 0b00010000, 0b11111111],
		"Ш": [0b11111111, 0b00000001, 0b11111111, 0b00000001, 0b11111111],
		"Щ": [0b11111110, 0b00000010, 0b11111110, 0b00000010, 0b11111110, 0b00000011],
		"Ъ": [0b10000000, 0b11111111, 0b00001001, 0b00001001, 0b00001111],
		"Ы": [0b11111111, 0b00001001, 0b00001111, 0b00000000, 0b11111111],
		"Ь": [0b11111111, 0b00001001, 0b00001001, 0b00001111],
		"Э": [0b10010001, 0b10010001, 0b10010001, 0b01111110],
		"Ю": [0b11111111, 0b00010000, 0b01111110, 0b10000001, 0b01111110],
		"Я": [0b11110011, 0b10010100, 0b10011000, 0b11111111],
		"е": [0b11111, 0b10101, 0b11101], #0xe5
		"к": [0b11111, 0b00100, 0b01010, 0b10001], #0xea
		"с": [0b11111, 0b10001, 0b10001], #с
		"т": [0b10000, 0b11111, 0b10000] #т
	}

	unknown_letters = {"unknown_letters": []}
	unknown_letter_substitution_code = [0b11111110, 0b10000010, 0b11111110]

	def __init__(self, led_server):
		self.unknown_letters_filename = led_server.user_settings.unknown_letters_filename
		self.letters_codes_filename = led_server.user_settings.letters_codes_filename
		self.read_letters_codes_file()
		self.read_unknown_letters_file()

	def file_exists(self, filename):
		return os.path.exists(filename)

	def read_letters_codes_file(self):
		# if letter_codes.json doesn't exist create the file and copy default codes into the file
		if self.file_exists(self.letters_codes_filename):
			with open(self.letters_codes_filename, 'r', encoding='utf-8') as file:
				self.letters_codes = json.load(file)
		else:
			self.save_letters_codes()

	def read_unknown_letters_file(self):
		if self.file_exists(self.unknown_letters_filename):
			with open(self.unknown_letters_filename, 'r', encoding='utf-8') as file:
				self.unknown_letters = json.load(file)
			self.unknown_letters["unknown_letters"] = set(self.unknown_letters["unknown_letters"])
			self.unknown_letters["unknown_letters"] = list(self.unknown_letters["unknown_letters"])
			for letter in self.unknown_letters["unknown_letters"]:
				if letter in self.letters_codes:
					self.unknown_letters["unknown_letters"].remove(letter)
		else:			
			self.save_unknown_letters()

	def save_letters_codes(self):
		with open(self.letters_codes_filename, 'w', encoding='utf-8') as file:
			json.dump(self.letters_codes, file, ensure_ascii=False)

	def save_unknown_letters(self):
		with open(self.unknown_letters_filename, 'w', encoding='utf-8') as file:
			json.dump(self.unknown_letters, file, ensure_ascii=False)

	def save_new_letter(self, letter_dict):
		letter = letter_dict['letter']
		if not letter in self.letters_codes:
			self.letters_codes[letter] = letter_dict['code']
			self.save_letters_codes()
			if letter in self.unknown_letters["unknown_letters"]:
				self.unknown_letters["unknown_letters"].remove(letter)
				self.save_unknown_letters()
			response = 'OK'
		else:
			response = 'This letter has already been saved before'
		return response

	def change_letter(self, letter_dict):
		letter = letter_dict['letter']
		if (letter in self.letters_codes):
			self.letters_codes[letter] = letter_dict['code']
			self.save_letters_codes()
			response = 'OK'
		else:
			response = self.save_new_letter(letter_dict)
		return response

	def __getitem__(self, letter):
		code = self.__try_find_letter_code(letter)
		if not code:
			if (letter.isupper()):
				code = self.__try_find_letter_code(letter.lower())
			elif (letter.islower()):
				code = self.__try_find_letter_code(letter.upper())
			if not code:
				code = self.unknown_letter_substitution_code
		return code

	def __find_letter_code(self, letter):
		return self.letters_codes.get(letter)

	def __try_find_letter_code(self, letter):
		code = self.__find_letter_code(letter)
		if not code:
			if not letter in self.unknown_letters:
				self.unknown_letters["unknown_letters"].append(letter)
				self.save_unknown_letters()
		return code