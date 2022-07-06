#coding: utf-8

from color_codes import color_codes
from led_letter import Letter


class Text:
	message_fields = ['string',
					'main_color',
					'background_color',
					'letters_colors',
					'decorations',
					'add_in_stack',
					'language',
					'direction',
					'mode',
					'cycles',
					'change_direction']
	end_break_symbol = ' || '
	
	def __init__(self, matrix_settings, letters_codes, output_process=False):
		self.matrix_settings = matrix_settings
		self.letters_codes = letters_codes
		self.wrapped_output_processes = {}
		self.set_output_process(output_process)

	def set_output_process(self, output_process):
		if output_process:
			self.output_process = output_process
			self.get_modes()

	def get_modes(self):
		self.modes = self.output_process.main_output_process.modes

	@property
	def width(self):
		return len(self)

	def refresh_text_properties(self):
		for field in self.message_fields:
			self.__dict__[field] = None

	def fill_text_properties_from_message(self):
		if isinstance(self.message_dict, dict):
			for field in self.message_fields:
				if field in self.message_dict:
					self.__dict__[field] = self.message_dict[field]
			if not ('string' in self.message_fields):
				self.string = 'No message'
				self.message_dict['add_in_stack'] = False
		else:
			message_dict = {}
			try:
				self.string = str(self.message_dict)
			except:
				self.string = 'No message'
				message_dict['add_in_stack'] = False
			message_dict['string'] = self.string
			self.message_dict = message_dict

	def set_text_properties(self, message_dict):
		self.message_dict = message_dict
		self.refresh_text_properties()
		self.fill_text_properties_from_message()

		if self.main_color and self.main_color in color_codes:
			self.main_color = color_codes[self.main_color]
		else:
			self.main_color = color_codes[self.matrix_settings.main_color]
		if self.background_color and self.background_color in color_codes:
			self.background_color = color_codes[self.background_color]
		else:
			self.background_color = color_codes[self.matrix_settings.background_color]

		transformed_letters_colors = {}
		if self.letters_colors:
			for color_object in self.letters_colors:
				transformed_letters_colors[color_object] = self.transform_letters_colors(color_object)
		self.letters_colors = transformed_letters_colors

		transformed_decorations = {}
		if self.decorations:
			transformed_decorations = self.transform_decorations()
		self.transformed_decorations = transformed_decorations

		if self.add_in_stack is None:
			self.add_in_stack = self.message_dict['add_in_stack'] = True

	def render_full_text_array(self):
		self.full_text_array = self.render_text_array()
		self.useful_width = self.width		

		if self.output_process.full_screen:
			self.render_full_text_array_for_fullscreen()
		else:
			self.make_piece()
	
	def render_full_text_array_for_fullscreen(self):
		if self.matrix_settings.width >= self.width:
			self.place_to_center()
		else:
			self.prepare_to_scrolling()

	def render_full_text_array_for_piece(self):
		self.make_piece()

	def refresh_text(self, *args, **kwargs):
		message_dict = self.get_message_dict(*args)
		self.set_text_properties(message_dict)
		self.refresh_output_process_properties_for_message()
		self.render_full_text_array()
		return self

	def refresh_output_process_properties_for_message(self):
		self.output_process.refresh_output_process_properties_for_message(self)

	def get_message_dict(self, *args):
		if len(args) >= 1:
			message_dict = args[0]
		else:
			message_dict = "{} PROCESS".format(self.output_process.__class__.__name__.upper())
			message_dict = {'string': '🦉' + 'philingvo',
							'main_color': 'blue',
							'add_in_stack': False
							}
		return message_dict


	def get_pure_text(self, message_dict):
		self.set_text_properties(message_dict)
		self.full_text_array = self.render_text_array()
		self.full_pure_text_array = self.copy_full_text_array()
		return self

	def wrap_pure_text(self, output_process):
		self.full_text_array = self.full_pure_text_array
		self.set_output_process(output_process)
		self.refresh_output_process_properties_for_message()
		self.useful_width = self.width
		if self.output_process.full_screen:
			self.render_full_text_array_for_fullscreen()
		else:
			self.make_piece()

	def copy_full_text_array(self):
		full_text_array = []
		for column in self.full_text_array:
			full_text_array.append(column)
		return full_text_array

	def transform_letters_colors(self, color_object):
		transformed_letters_colors = {}		
		for color in self.letters_colors[color_object]:
			if color in color_codes:
				numbers = self.letters_colors[color_object][color]
				for number in numbers:
					if '-' in number:
						range_numbers = list(map(int, number.split('-')));
						for subnumber in range(range_numbers[0], range_numbers[1]+1):
							transformed_letters_colors[subnumber] = color
					else:
						transformed_letters_colors[int(number)] = color
		return transformed_letters_colors

	def transform_decorations(self):
		string_dict = {}
		decorated_numbers = {}
		decorations = self.decorations
		for decoration in decorations:
			numbers_for_deсoration = []
			numbers = decorations[decoration]
			for number in numbers:
				if '-' in number:
					range_numbers = list(map(int, number.split('-')));
					for subnumber in range(range_numbers[0], range_numbers[1]+1):
						if subnumber in string_dict:
							string_dict[subnumber] = string_dict[subnumber] + decoration
						else:
							string_dict[subnumber] = decoration
				else:
					number = int(number)
					if number in string_dict:
						string_dict[number] = string_dict[number] + decoration
					else:
						string_dict[number] = decoration
		
		return string_dict

	def __next__(self, i = 0):
		if i < self.width-1:
			i += 1
			return self.full_text_array[i]
		raise StopIteration();
	
	def __getitem__(self, index):
		return self.full_text_array[index]
	
	def __len__(self):
		return len(self.full_text_array)
	
	def print(self):
		print(self.full_text_array)
		
	def get_empty_column(self, color=False):
		return self.get_colums(1, color)

	def get_colums(self, spaces, color=False):
		if not color:
			color = self.background_color
		return [[color for row in range(self.matrix_settings.height)] for column in range(spaces)]
	
	def insert_spaces_before(self, spaces):
		self.full_text_array = self.get_colums(spaces) + self.full_text_array
		
	def insert_spaces_after(self, spaces):
		self.full_text_array = self.full_text_array + self.get_colums(spaces)
	
	def prepare_to_scrolling(self):
		mode_object = self.modes[self.output_process.mode]
		if self.scrolling_direction:
			insert_spaces_before, insert_spaces_after = self.insert_spaces_before, self.insert_spaces_after
		else:
			insert_spaces_after, insert_spaces_before = self.insert_spaces_before, self.insert_spaces_after

		insert_spaces_before(self.matrix_settings.spaces_before)
		
		if mode_object.insert_end_break:
			if self.output_process.cycles > 1:
				self.make_piece()

		if mode_object.use_gap:
			insert_spaces_after(self.matrix_settings.width)

	def get_difference_width(self):
		total_difference_width = self.matrix_settings.width - self.width
		start_difference_width = total_difference_width // 2
		end_difference_width = total_difference_width - start_difference_width
		return start_difference_width, end_difference_width
	
	def place_to_center(self):
		start_difference_width, end_difference_width = self.get_difference_width()
		if self.scrolling_direction:
			insert_spaces_before, insert_spaces_after = self.insert_spaces_before, self.insert_spaces_after
		else:
			insert_spaces_after, insert_spaces_before = self.insert_spaces_before, self.insert_spaces_after
		
		insert_spaces_before(start_difference_width)
		insert_spaces_after(end_difference_width)
	
	def merge_letters(self, full_text_array):
		merged_output_array = []
		for letter in full_text_array:
			for column in letter:
				merged_output_array.append(column)
		return merged_output_array
	
	def render_text_array(self):
		full_text_array = []
		for letter_index in range(len(self.string)):
			self.letter = Letter(self)
			self.letter.set_new_letter(letter_index)
			full_text_array.append(self.letter.letter_array)
			if letter_index < len(self.string) - 1:
				if self.letter.background_colored:
					background_color = self.letter.background_colored
				else:
					background_color = self.background_color
				full_text_array.append(self.get_empty_column(background_color))
		return self.merge_letters(full_text_array)

	def create_empty_text_array(self):
		self.full_text_array = [[(0, 0, 0) for row in range(self.matrix_settings.height)] for column in range(self.matrix_settings.width)]

	def get_frame(self, first_column_number):
		return self.slice_full_text_array(first_column_number, self.matrix_settings.width)

	@property
	def scrolling_direction(self):
		return (not (self.output_process.direction == self.output_process.change_direction))

	def slice_full_text_array(self, first_column_number, distance):
		if self.scrolling_direction:
			return self.full_text_array[first_column_number:first_column_number+distance]
		else:
			first_column_number = self.width - first_column_number
			last_column_number = first_column_number - distance
			return self.full_text_array[last_column_number:first_column_number]

	def merge(self, other_text):
		self.full_text_array = self.full_text_array + other_text.full_text_array
		return self

	def insert_array_before(self, text_array):
		if self.scrolling_direction:
			self.full_text_array = text_array + self.full_text_array
		else:
			self.full_text_array = self.full_text_array + text_array
		return self

	def delete_columns_before(self):
		if self.scrolling_direction:			
			self.full_text_array = self.slice_full_text_array(self.matrix_settings.width, self.width)
		else:			
			self.full_text_array = self.full_text_array[0:self.width - self.matrix_settings.width]

	def prepare_message_for_saving(self, message_dict):
		message_dict_for_saving = {}
		for field_name in self.message_fields:
			if field_name in message_dict:
			   message_dict_for_saving[field_name] = message_dict.get(field_name)
		return message_dict_for_saving
	
	def insert_end_break(self):
		if self.scrolling_direction:
			self.string += self.end_break_symbol
		else:
			self.string = self.end_break_symbol + self.string

	def make_piece(self):
		if self.scrolling_direction:
			self.full_text_array = self.get_colums(2, self.main_color) + self.wrap_with_singular_columns()
		else:
			self.full_text_array = self.wrap_with_singular_columns() + self.get_colums(2, self.main_color)

	def wrap_with_singular_columns(self):
		return self.get_empty_column() + self.full_text_array + self.get_empty_column()

	def place_pieces_to_center_to_scrolling(self):
		first_background_color, last_background_color = self.output_process.get_volumes_border_background_colors()

		start_difference_width, end_difference_width = self.get_difference_width()
		if start_difference_width <= end_difference_width:
			end_difference_width += 1

		self.full_text_array = self.get_colums(start_difference_width, first_background_color) + self.full_text_array
		self.full_text_array += self.get_colums(end_difference_width, last_background_color)

	def refresh_piece_text(self, message_dict):
		self.handled_message_dict = self.prepare_message_for_saving(message_dict)
		return self.refresh_text(self.handled_message_dict)