#coding: utf-8

import json
import os
import functools
from led_text import Text

class Saved_Messages_Library():

	def __init__(self, led_server):
		self.volumes = {'newsline': Newsline_saved_messages(led_server),
						'notes': Notes(led_server)}
		self.matrix_settings = led_server.matrix_settings
		self.user_settings = led_server.user_settings
		self.letters_codes = led_server.letters_codes

	@property
	def volumes_names(self):
		volumes_names = []
		for volume_name in self.volumes.keys():
			volume = {'name': volume_name, 'type': self.volumes[volume_name].type}
			volumes_names.append(volume)
		return volumes_names

	def get_volumes(self, volumes_names):
		volumes = []
		for volume_name in volumes_names:
			volumes.append(self.volumes[volume_name])
		return volumes

	def library_method_decorator(library_method):

		@functools.wraps(library_method)
		def wrapped(self, request_dict):
			if request_dict['volume']:
				volume_name = request_dict['volume']
				if volume_name in self.volumes:
					volume = self.volumes[volume_name]
					return library_method(self, volume, request_dict)
				else:
					return 'No this volume'
			else:
				return 'Volume hasn\'t been set'

		return wrapped

	@library_method_decorator
	def get_volume_properties(self, volume, request_dict):
		return volume.get_properties(request_dict)

	@library_method_decorator
	def change_message(self, volume, request_dict):
		return volume.change_message(request_dict)

	@library_method_decorator
	def save_volume(self, volume, request_dict):
		return volume.save()

	@library_method_decorator
	def get_message(self, volume, request_dict):
		return volume.get_message(request_dict)

	def save_all_volumes(self):
		for volume_name in self.volumes:
			self.volumes[volume_name].save()
		return 'All volumes have been saved'

class Saved_Messages_Volume():

	volume_name = None
	volume_filename = None
	messages = None
	
	def __init__(self, led_server):
		self.matrix_settings = led_server.matrix_settings
		self.letters_codes = led_server.letters_codes
		self.read_messages()

	def create_new_message(self, message_dict):
		text_object = Text(self.matrix_settings, self.letters_codes)
		message_dict_for_saving = text_object.prepare_message_for_saving(message_dict)
		return self.create_full_message_dict(message_dict_for_saving)

	def __len__(self):
		return len(self.messages)

	def __getitem__(self, identificator):
		return self.messages[identificator]

	@property
	def type(self):
		return self.messages.__class__.__name__

	def file_exists(self, file_name):
		return os.path.exists(file_name)

	def create_full_message_dict(self, message):
		text_object = Text(self.matrix_settings, self.letters_codes)
		full_message_dict = {'message': message,
							'text_object': text_object.get_pure_text(message)}
		return full_message_dict

	def read_messages(self):
		if self.file_exists(self.volume_filename):
			with open(self.volume_filename, 'r', encoding='utf-8') as file:
				saved_messages = json.load(file)
			self.create_messages_container(saved_messages)
		else:
			self.create_empty_messages_container()
	
	def create_messages_container(self, saved_messages):
		pass

	def create_empty_messages_container(self):
		pass

	def get_properties(self, *args, **kwargs):
		pass

	def change_message(self, message_dict):
		pass
	
	def save(self):
		pass

	def get_message(self, message_dict):
		pass

	def get_message_string_short(self, message):
		if isinstance(message, dict):
			string = message['string']
		elif isinstance(message, str):
			string = message
		if len(string) >= 21:
			string = string[0:21]
		return string

class Saved_Messages_Volume_Dict(Saved_Messages_Volume):

	volume_name = None
	volume_filename = None
	messages = dict()
	sources = []

	def __getitem__(self, identificator):
		identificator = self.sources[identificator]
		return super().__getitem__(identificator)

	def create_messages_container(self, saved_messages):
		for source, message in saved_messages.items():
			self.messages[source] = self.create_full_message_dict(message)

	def create_empty_messages_container(self):
		for source in self.sources:
			self.messages[source] = self.create_full_message_dict(source.capitalize())
			self.messages[source]['text_object'].volume_name = self.volume_name

	def get_properties(self, *args, **kwargs):
		return [{'source': source_name,
				'string': self.get_message_string_short(self.messages[source_name]['message']),
				} for source_name in self.sources]

	def get_message_string_short(self, message):
		return super().get_message_string_short(message)

	def get_message_background_color(self, index):
		return self.messages[self.sources[index]]["text_object"].background_color

	def get_first_message_background_color(self):
		return self.get_message_background_color(0)

	def get_last_message_background_color(self):
		return self.get_message_background_color(-1)

	def change_message(self, request_dict):
		if 'string' in request_dict and 'source' in request_dict:
			source = request_dict['source']
			if source in self.sources:
				self.messages[source] = self.create_new_message(request_dict)
				return 'Message has been changed'
			else:
				return 'There\'s no source with this name'
		else:
			return 'Message format error'

	def get_message(self, request_dict):
		if 'source' in request_dict:
			source = request_dict['source']
			message_dict = self.messages[source]['message']
			return message_dict

	def save(self):
		saving_messages = {}
		for source, message in self.messages.items():
			saving_messages[source] = message['message']
		with open(self.volume_filename, 'w', encoding='utf-8') as file:
			json.dump(saving_messages, file, ensure_ascii=False)
		return 'Volume has been saved'

class Saved_Messages_Volume_List(Saved_Messages_Volume):

	volume_name = None
	volume_filename = None
	messages = list()

	def get_properties(self, *args, **kwargs):
		return [self.get_message_string_short(i) for i in range(len(self.messages))]

	def get_message_string_short(self, index):
		message = self.messages[index]['message']
		return super().get_message_string_short(message)

	def create_messages_container(self, saved_messages):
		if len(saved_messages) > 0:
			self.messages = saved_messages
			for i in range(len(self.messages)):
				self.messages[i] = self.create_full_message_dict(self.messages[i])
		else:
			self.create_empty_messages_container()

	def create_empty_messages_container(self):
		self.messages.append(self.create_full_message_dict('No messages in {}'.format(self.volume_name.capitalize())))

	def change_message(self, request_dict):
		if 'string' in request_dict and 'source' in request_dict:
			source = request_dict['source']
			if source == 'add':
				self.messages.append(self.create_new_message(request_dict))
				return 'New message has been added'
			else:
				try:
					message_number = int(source)
				except:
					return 'Wrong message number format'
				else:
					if message_number >= len(self.messages):
						return 'There\'s no message with this number'
					else:
						self.messages[message_number] = self.create_full_message_dict(request_dict)
						return 'Message has been changed'
		else:
			return 'Message format error'
	
	def get_message(self, request_dict):
		if 'source' in request_dict:
			source = request_dict['source']
			if source != 'add':
				try:
					message_number = int(source)
				except:
					pass
				return self.messages[message_number]['message']

	def save(self):
		saving_messages = []
		for i in range(len(self.messages)):
			saving_messages.append(self.messages[i]['message'])
		with open(self.volume_filename, 'w', encoding='utf-8') as file:
			json.dump(saving_messages, file, ensure_ascii=False)
		return 'Volume has been saved'

class Newsline_saved_messages(Saved_Messages_Volume_Dict):

	volume_name = 'newsline'
	volume_filename = 'data/saves/newsline.json'
	sources = ['date_time',
				'plans']
	
class Notes(Saved_Messages_Volume_List):

	volume_name = 'notes'
	volume_filename = 'data/saves/notes.json'