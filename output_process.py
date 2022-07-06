#coding: utf-8

import time
from datetime import datetime
import json
import os
import functools
import urllib.request
import random
from matrix_array import get_matrix_array
from led_text import Text


class Mode:
	def __init__(self, scrolling_function, use_gap=False, insert_end_break=False):
		self.scrolling_function = scrolling_function
		self.use_gap = use_gap
		self.insert_end_break = insert_end_break

class Main_Output_Process:

	on = True
	autorun_standby_process_status = True
	scrolling = False
	motion_status = True
	column_number = None
	motion_status = True
	refresh_message_status = False
	deny_receiving_status = False

	output_process_settings_names = ['language',
									'direction',
									'mode',
									'cycles',
									'change_direction']
	directions = {'l': True,
				'r': False,
				'ru': True,
				'en': True,
				'he': False,
				}
	mode_object = False
	output_done = False
	current_cycle = 0
	text = None
	current_working_process_name = None
	previous_current_working_process_name = None
	default_settings_names = ['default_language',
							'default_direction',
							'default_mode',
							'default_cycles',
							'default_change_direction',
							'standby_working_process_name',
							'default_scrolling_delay_time',
							]
	working_processes = {}
	all_working_processes_names = []
	messages_store = None
	
	def __init__(self, led_server):
		self.led_server = led_server
		self.pixels = led_server.pixels
		self.set_global_settings(led_server)
		self.set_default_settings()
		self.set_output_process_settings_as_default()
		self.matrix_array = get_matrix_array(self.matrix_settings)
		self.necessery_basic_working_processes_classes = [Message,
														Messages_Store]
		self.message_working_process_name = Message.__name__.lower()
		self.message_store_working_process_name = Messages_Store.__name__.lower()
		self.date_time_working_process_name = Date_Time.__name__.lower()
		self.basic_working_processes_classes = [Dictionary,
												Date_Time,
												Volumes_Messages_Newsline,
												Volumes_Messages_Queue,
												Mind_Calculator]
		self.create_modes()
		self.create_working_processes()
		self.create_messages_store()
		self.show_default_message()

	def set_global_settings(self, parent_object):
		self.matrix_settings = parent_object.matrix_settings
		self.user_settings = parent_object.user_settings
		self.letters_codes = parent_object.letters_codes

	def set_output_process_default_settings(self):
		for default_setting_name in self.default_settings_names:
			if not self.__class__.__dict__.get(default_setting_name):
				self.__dict__[default_setting_name] = self.user_settings.__dict__[default_setting_name]

	def set_default_settings(self):
		self.set_output_process_default_settings()

		if self.user_settings.default_message:
			default_message = self.user_settings.default_message
		else:
			default_message = self.led_server.host_IP

		if isinstance(default_message, dict) and 'string' in default_message:
			self.default_message = default_message
		else:
			self.default_message = {'string': '🦉' + str(default_message),
									'letters_colors': {'main_color': {'blue':["0"]}},
									'add_in_stack': False}

		if self.user_settings.default_start_delay_time:
			self.default_start_delay_time = self.user_settings.default_start_delay_time
		else:
			self.default_start_delay_time = self.matrix_settings.width / 32

	def set_output_process_settings_as_default(self):
		for setting_name in self.output_process_settings_names:
			self.__dict__[setting_name] = self.user_settings.__dict__['default_' + setting_name]

	def create_modes(self):
		self.modes = {'loop_with_gap': Mode(self.loop_with_gap_scrolling_function, True, False),
					'loop': Mode(self.loop_scrolling_function, False, True),
					'single': Mode(self.single_scrolling_function, False, False)}

	def create_working_processes(self):
		self.basic_working_processes_classes = self.necessery_basic_working_processes_classes + self.basic_working_processes_classes
		for working_process_class in self.basic_working_processes_classes:
			self.add_working_process(working_process_class)
		self.add_working_process(Mixed_Working_Process, 'mixed')
		self.add_working_process(self.get_working_process(self.standby_working_process_name), 'default_standby', False)

	def add_working_process(self, working_process_class, working_process_name=False, create_instance=True):
		if not working_process_name:
			working_process_name = working_process_class.__name__.lower()
		working_process_instance = working_process_class(self) if create_instance else working_process_class
		self.working_processes[working_process_name] = working_process_instance
		self.all_working_processes_names.append(working_process_name)

	def create_messages_store(self):
		self.messages_store = self.get_working_process(self.message_store_working_process_name)

	@property
	def all_working_processes_names_with_types(self):
		all_working_processes_names_with_types = []
		for working_process_name in self.all_working_processes_names:
			all_working_processes_names_with_types.append({'name': working_process_name,
															'queue': self.get_working_process(working_process_name).queue})
		return all_working_processes_names_with_types

	@property
	def properties(self):
		return {'standby_working_process_name': self.standby_working_process_name,
				'repeat_message_status': self.current_working_process.repeat_message_status,
				'repeat_message_status_message': self.get_working_process(self.message_working_process_name).repeat_message_status,
				'repeat_message_status_standby': self.get_working_process(self.standby_working_process_name).repeat_message_status,
				'scrolling_delay_time': round(self.default_scrolling_delay_time, 2),
				'refresh_message_status': self.current_working_process.refresh_message_status,
				'deny_receiving_status': self.deny_receiving_status}

	def get_working_process(self, name):
		return self.working_processes[name]

	def start_process_decorator(start_process_method):

		@functools.wraps(start_process_method)
		def wrapped(self, *args, **kwargs):
			if self.on:
				self.stop_output_process()
				self.start_message_time = self.current_time
				respond_body = start_process_method(self, *args, **kwargs)
				self.set_start_process_properties()
				self.start_output_process()
				return respond_body
		return wrapped

	@start_process_decorator
	def start_working_process(self, working_process_name, *args, **kwargs):
		self.previous_current_working_process_name = self.current_working_process_name
		self.current_working_process_name = working_process_name
		self.current_working_process = self.get_working_process(working_process_name)
		previous_repeat_message_status = self.current_working_process.repeat_message_status
		self.reset_statuses()
		self.current_working_process.repeat_message_status = previous_repeat_message_status
		self.text = self.current_working_process.start(*args, **kwargs)

	def get_next_text(self):
		if self.queue:
			self.get_next_text_from_queue()

	@start_process_decorator
	def get_next_text_from_queue(self):
		text = self.current_working_process.get_next_text()
		if text:
			self.text = text

	def get_previous_text(self):
		if self.queue:
			self.get_previous_text_from_queue()

	@start_process_decorator
	def get_previous_text_from_queue(self):
		text = self.current_working_process.get_previous_text()
		if text:
			self.text = text

	def show_next_received_message(self):
		if self.current_working_process_name == self.message_working_process_name:
			if self.previous_current_working_process_name != self.current_working_process_name:
				self.messages_store.set_beginning_indexes()
		else:
			self.messages_store.set_ending_indexes()
		message_dict = self.messages_store.get_next_text().message_dict
		message_dict['add_in_stack'] = False
		self.start_working_process(self.message_working_process_name, message_dict)

	def show_previous_received_message(self):
		if self.current_working_process_name == self.message_working_process_name:
			if self.previous_current_working_process_name != self.current_working_process_name:
				self.messages_store.set_ending_indexes()
		else:
			self.messages_store.set_beginning_indexes()
		message_dict = self.messages_store.get_previous_text().message_dict
		message_dict['add_in_stack'] = False
		self.start_working_process(self.message_working_process_name, message_dict)

	def refresh_text(self):
		self.text = self.current_working_process.refresh_text()

	def set_start_process_properties(self):
		self.current_cycle = 0
		self.output_done = False
		self.previous_time = self.current_time
		self.delay_time = self.default_start_delay_time

		if self.matrix_settings.width >= self.text.width:
			self.scrolling = False
		else:
			self.scrolling = True

	def start_output_process(self):
		if not self.scrolling: # without scrolling
			self.show(self.text)
			self.output_done = True
		else: # scrolling mode
			self.modes[self.mode].scrolling_function()

	def show(self, text):
		column_number = 0
		for letter_column_number in range(len(text)):
			column = text[letter_column_number]
			for row_number in range(self.matrix_settings.height):
				color = column[row_number]
				led_number = self.matrix_array[row_number][column_number]
				self.pixels[led_number] = color
			column_number += 1
		self.pixels.show()

	def stop_output_process(self):
		self.column_number = None
		self.scrolling = False

	def end_output_process(self):
		self.stop_output_process()
		self.start_working_process(self.message_working_process_name, '')

	def loop_with_gap_scrolling_function(self):
		if self.column_number == None:
			self.show_start_frame(self.default_start_delay_time)
		elif self.column_number == self.text.useful_width:
			self.output_done = True
			self.current_cycle += 1
			if self.queue and self.ready_to_stop:
				self.get_next_text()
			else:
				self.show_start_frame(self.default_start_delay_time)
		else:
			self.show_next_frame()

	def loop_scrolling_function(self):
		if self.column_number == None:
			if self.current_cycle > 0:
				delay_time = self.default_scrolling_delay_time
			else:
				delay_time = self.default_start_delay_time
			self.show_start_frame(delay_time)

		elif self.column_number == self.text.width - self.matrix_settings.width:

			if self.current_cycle > 0:
				self.text.delete_columns_before()

			self.current_cycle += 1
			self.output_done = True

			if self.queue and self.ready_to_stop:
				self.get_next_text()
			else:
				if self.refreshable:
					self.refresh_text()
				self.text.insert_array_before(self.frame_text_array)
				self.show_start_frame(self.default_scrolling_delay_time)
		else:
			self.show_next_frame()

	def single_scrolling_function(self):
		if self.column_number == None:
			self.show_start_frame(self.default_start_delay_time)
		elif self.column_number == self.text.width - self.matrix_settings.width - 1:
			self.show_next_frame(self.default_start_delay_time)
		elif self.column_number == self.text.width - self.matrix_settings.width:
			self.output_done = True
			self.current_cycle += 1
			if self.queue and self.ready_to_stop:
				self.get_next_text()
			else:
				if self.refreshable:
					self.refresh_text()
				self.show_start_frame(self.default_start_delay_time)
		else:
			self.show_next_frame()

	def show_start_frame(self, start_time):
		self.column_number = 0
		self.delay_time = start_time
		self.show_frame()

	def show_next_frame(self, delay_time=False):
		self.column_number += 1
		if delay_time:
			self.delay_time = delay_time
		else:
			self.delay_time = self.default_scrolling_delay_time
		self.show_frame()

	def show_frame(self):
		self.frame_text_array = self.text.get_frame(self.column_number)
		self.show(self.frame_text_array)
		self.previous_time = self.current_time

	@property
	def current_time(self):
		return datetime.now()

	def refresh_scrolling(self):
		current_time = self.current_time
		if self.scrolling or self.column_number != None:
			if self.motion_status and (current_time - self.previous_time).total_seconds() >= self.delay_time:
				self.start_output_process()

	@property
	def ready_to_stop(self):
		if self.output_done: # text has been shown at least 1 time
			if self.scrolling:
				return self.current_cycle >= self.cycles
			else:
				return (self.current_time - self.start_message_time).total_seconds() >= self.not_scrolling_message_waiting_time * self.cycles
		else:
			return False

	def refresh_standby_process(self):
		if self.on and self.ready_to_stop:
			if self.current_working_process_name != self.standby_working_process_name: # For Message process when CURRENT standby process is not Message
				if not self.motion_status: # PAUSE FOR NOT SCROLLING MESSAGE
					self.start_message_time = self.current_time
				elif self.current_working_process.repeat_message_status:
					if self.scrolling: # REPEAT SCROLLING MESSAGE 
						self.output_done = False
					else: # KEEP SHOWING NOT SCROLLING MESSAGE
						self.start_message_time = self.current_time
				elif self.autorun_standby_process_status: # run CURRENT standby process if standby process autorunning activated
					self.start_working_process(self.standby_working_process_name)
				else: # stop outputting if standby process autorunning deactivated
					self.end_output_process()
			elif self.queue and self.motion_status:
				self.get_next_text()
			elif self.refreshable:
				pass

	@property
	def refreshable(self):
		return self.current_working_process.refreshable

	@property
	def queue(self):
		return self.current_working_process.queue

	@property
	def not_scrolling_message_waiting_time(self):
		return self.current_working_process.not_scrolling_message_waiting_time_value

	def show_default_message(self):
		self.start_working_process(self.message_working_process_name, self.default_message)

	def recieve_message(self, message_dict):
		if not self.deny_receiving_status:
			self.start_working_process(self.message_working_process_name, message_dict)
			return 'Message has been received'
		else:
			return 'Receiving messages is denied. Message can\'t be received'

	def show_text(self, text):
		self.start_working_process(self.message_working_process_name, text)

	def reset_repeat_message_status(self):
		self.current_working_process.reset_repeat_message_status()

	def reset_refresh_message_status(self):
		self.current_working_process.reset_refresh_message_status()

	def reset_autorun_standby_process_status(self):
		self.autorun_standby_process_status = True

	def reset_motion_status(self):
		self.motion_status = True

	def reset_statuses(self):
		self.reset_repeat_message_status()
		self.reset_refresh_message_status()
		self.reset_motion_status()

	def control_command(self, message_dict):
		command = message_dict['command']
		if not self.on and command == 'on':
			response_body = self.on_command()
		elif not self.on and command != 'on':
			response_body = 'The system has been switched off. Command can\'t be received. Switch on the system'
		elif self.on and command == 'off':
			response_body = self.off_command()
		else:
			response_body = 'Command has been received'
			if command == 'speed_up':
				self.speed_up()
			elif command == 'slow_down':
				self.slow_down()
			elif command == 'set_delay_time':
				response_body = self.set_delay_time(message_dict)
			elif command == 'pause':
				self.pause_command()
			elif command == 'stop':
				self.stop_command()
			elif command == 'wait':
				self.wait_command()
			elif command == 'standby':
				self.start_default_standby_working_process()
			elif command == 'date_time':
				self.show_date_time()
			elif command == 'change_repeat_message_status':
				self.change_repeat_message_status(message_dict)
			elif command == 'change_refresh_message_status':
				self.change_refresh_message_status()
			elif command == 'change_deny_receiving_status':
				self.change_deny_receiving_status()
			elif command == 'next_message':
				self.next_message()
			elif command == 'previous_message':
				self.previous_message()
			elif command == 'next_received_message':
				self.next_received_message()
			elif command == 'previous_received_message':
				self.previous_received_message()
			elif command == 'switch_process':
				response_body = self.switch_working_process_command(message_dict)
			elif command == 'process_beginning':
				response_body = self.start_process_with_beginning(message_dict)
			elif command == 'next_process':
				self.set_next_process()
			elif command == 'previous_process':
				self.set_previous_process()
			elif command == 'show_messages_from_volume':
				self.show_messages_from_volume(message_dict);
			else:
				response_body = 'No this command'
		return response_body

	def on_command(self):
		self.on = True
		self.reset_autorun_standby_process_status()
		self.show_default_message()
		return 'The system has been swiched on'

	def off_command(self):
		self.end_output_process()
		self.on = False
		return 'The system has been swiched off'

	def speed_up(self):
		if self.scrolling and self.default_scrolling_delay_time - 0.01 > 0:
			self.default_scrolling_delay_time = round(self.default_scrolling_delay_time - 0.01, 2)

	def slow_down(self):
		if self.scrolling and self.default_scrolling_delay_time + 0.01 <= 2:
			self.default_scrolling_delay_time = round(self.default_scrolling_delay_time + 0.01, 2)

	def set_delay_time(self, message_dict):
		value = message_dict.get('value')
		if not value:
			return 'No scrolling delay time value'
		else:
			try:
				value = float(value)
			except:
				return 'Wrong scrolling delay time value'
			else:
				if value >= 0 and value <= 2:
					self.default_scrolling_delay_time = round(value, 2)
					return 'New scrolling delay time is {}'.format(value)
				else:
					return 'New scrolling delay time is out of range between 0 and 2'

	def pause_command(self): # PAUSE STATE
		self.motion_status = not self.motion_status

	def stop_command(self): # stop outputing a current message and run the CURRENT standby process
		if self.autorun_standby_process_status:
			self.start_working_process(self.standby_working_process_name)

	def wait_command(self): # start WAITING STATE: stop outputing current message and forbid running CURRENT standby process and wait message to show only for MESSAGE working process
		self.autorun_standby_process_status = False
		self.end_output_process()

	def start_default_standby_working_process(self): # run DEFAULT standby working process even in WAITING STATE
		self.reset_autorun_standby_process_status()
		self.start_working_process('default_standby')

	def show_date_time(self):
		date_time_message_dict = self.get_working_process(self.date_time_working_process_name).get_text_object().message_dict
		date_time_message_dict["add_in_stack"] = False
		self.start_working_process(self.message_working_process_name, date_time_message_dict)

	def change_repeat_message_status(self, message_dict): 
		""" If REPEAT status is ON, it will show a message till status switched off in any working process.
		If REPEAT status is OFF, it will show a next message, if a working process has the QUEUE-type,
		If a working process doesn't have (Message), it will launch the current standby mode"""

		if "process_name" in message_dict and message_dict["process_name"] in ("message", "standby"):
			process_name = message_dict["process_name"]
			process_name = self.message_working_process_name if process_name == "message" else self.standby_working_process_name
			process = self.get_working_process(process_name)
		else:
			process = self.current_working_process
		process.change_repeat_message_status()

	def change_refresh_message_status(self):
		self.current_working_process.change_refresh_message_status()

	def change_deny_receiving_status(self):
		self.deny_receiving_status = not self.deny_receiving_status

	def move_message_decorator(move_message_method):

		@functools.wraps(move_message_method)
		def wrapped(self):
			if self.current_working_process_name != self.standby_working_process_name:
				working_process = self.get_working_process(self.standby_working_process_name)
			else:
				working_process = self
			
			if working_process.queue:
				working_process.reset_queue_element_internal_params = False
				move_message_method(working_process)
			else:
				previous_repeat_message_status = False
			
			if self.current_working_process_name != self.standby_working_process_name:
				self.stop_command()
				if self.queue:
					self.reset_queue_element_internal_params = True

		return wrapped

	def keep_repeat_message_status(move_message_method):

		@functools.wraps(move_message_method)
		def wrapped(self):
			standby_working_process = self.get_working_process(self.standby_working_process_name)
			previous_repeat_message_status = standby_working_process.repeat_message_status
			if previous_repeat_message_status:
				standby_working_process.reset_repeat_message_status()
			move_message_method(self)
			self.current_working_process.repeat_message_status = previous_repeat_message_status

		return wrapped

	@keep_repeat_message_status
	@move_message_decorator
	def next_message(self):
		self.get_next_text()
	
	@keep_repeat_message_status
	@move_message_decorator
	def previous_message(self):
		self.get_previous_text()

	def next_received_message(self):
		self.show_next_received_message()

	def previous_received_message(self):
		self.show_previous_received_message()

	def switch_working_process_command(self, message_dict): # run choosen working process even in WAITING STATE
		working_process_name = message_dict.get('process_name')
		if working_process_name and working_process_name in self.working_processes:
			self.standby_working_process_name = working_process_name
			self.reset_autorun_standby_process_status()
			self.start_working_process(working_process_name)
			return '{} as the current standby working process has been set'.format(working_process_name.upper())
		elif working_process_name:
			return 'No this working process'
		else:
			return 'No working process in the message'

	@start_process_decorator
	def start_process_with_beginning(self, message_dict): # run CURRENT working process with the beginning. Can't be runned in WAITING STATE

		def switch_working_process(message_dict):
			return self.switch_working_process_command(message_dict) + " with beginning"

		if self.autorun_standby_process_status:
			working_process_name = message_dict.get('process_name')
			if working_process_name == self.current_working_process_name or not working_process_name:
				self.reset_statuses()
				self.text = self.current_working_process.start_with_beginning()
				return '{} as current working process has been set with beginning'.format(self.current_working_process_name.upper())
			elif working_process_name == self.standby_working_process_name:
				standby_working_process = self.get_working_process(self.standby_working_process_name)
				standby_working_process.start_with_beginning()
				return switch_working_process(message_dict)
			else:
				return switch_working_process(message_dict)
		else:
			return "Working process can't be set because waiting mode has been started"

	def set_next_process(self):
		working_process_index = self.all_working_processes_names.index(self.standby_working_process_name)
		working_process_index += 1
		if working_process_index >= len(self.all_working_processes_names):
			working_process_index = 0
		next_working_process_name = self.all_working_processes_names[working_process_index]
		self.switch_working_process_command({'process_name': next_working_process_name})

	def set_previous_process(self):
		working_process_index = self.all_working_processes_names.index(self.standby_working_process_name)
		working_process_index -= 1
		if working_process_index < 0:
			working_process_index = len(self.all_working_processes_names) - 1
		previous_working_process_name = self.all_working_processes_names[working_process_index]
		self.switch_working_process_command({'process_name': previous_working_process_name})

	def show_messages_from_volume(self, message_dict):
		volume_name = message_dict['volume']
		volume = self.led_server.saved_messages_library.volumes[volume_name]
		text_dict = volume.get_message(message_dict)
		self.start_working_process(self.message_working_process_name, text_dict)

class Basic_Output_Process_Mode(Main_Output_Process):
	output_process_properties_for_message = {}
	queue = False
	repeat_message_status = False
	refresh_message_status = False
	refresh_output_process_mode_and_cycles = False
	refreshable = False
	full_screen = True
	add_mixed_process = True

	def __init__(self, main_output_process):
		self.main_output_process = main_output_process
		self.modes = main_output_process.modes
		self.set_user_settings(main_output_process)
		self.set_not_scrolling_message_waiting_time()
		self.set_global_settings(main_output_process)
		self.set_output_process_default_settings()
		self.set_output_process_settings_as_default()

	def set_user_settings(self, main_output_process):
		self.user_settings = main_output_process.user_settings

	def set_not_scrolling_message_waiting_time(self):
		if self.queue:
			not_scrolling_message_waiting_time_key = 'queue'
		else:
			not_scrolling_message_waiting_time_key = 'default'
		self.not_scrolling_message_waiting_time_value = self.user_settings.not_scrolling_message_waiting_time_values[not_scrolling_message_waiting_time_key]

	def create_text_object(self):
		self.text = Text(self.matrix_settings, self.letters_codes, self)

	def refresh_output_process_properties_for_message(self, text): # call from Text object

		for setting_name in self.output_process_settings_names:
			self.output_process_properties_for_message[setting_name] = text.__dict__[setting_name]
		self.define_language_and_direction()
		self.define_change_direction()
		if self.refresh_output_process_mode_and_cycles:
			self.define_mode()
			self.define_cycles(text)

		self.refresh_main_output_process_properties() # copy op props to main op

	def define_language_and_direction(self):
		self.direction = self.default_direction
		language = self.output_process_properties_for_message['language']
		direction = self.output_process_properties_for_message['direction']
		if language and language in self.directions:
			self.direction = self.directions[language]
		elif direction and direction in self.directions:
			self.direction = self.directions[direction]

	def define_mode(self):
		self.mode = self.default_mode
		mode = self.output_process_properties_for_message['mode']
		if mode in self.modes:
			self.mode = mode
		self.mode_object = self.modes[self.mode]

	def define_cycles(self, text):
		self.cycles = self.default_cycles
		cycles = self.output_process_properties_for_message['cycles']
		if cycles:
			try:
				cycles = int(cycles)
			except:
				self.cycles = self.default_cycles
			else:
				if cycles > 0:
					self.cycles = cycles
				else:
					self.cycles = self.default_cycles

	def define_change_direction(self):
		self.change_direction = self.default_change_direction
		if self.output_process_properties_for_message['change_direction']:
			self.change_direction = True

	def refresh_main_output_process_properties(self):
		for setting_name in self.output_process_settings_names:
			self.main_output_process.__dict__[setting_name] = self.__dict__[setting_name]

	def change_repeat_message_status(self):
		self.repeat_message_status = not self.repeat_message_status

	def reset_repeat_message_status(self):
		self.repeat_message_status = False

	def change_refresh_message_status(self):
		self.refresh_message_status = not self.refresh_message_status

	def reset_refresh_message_status(self):
		self.refresh_message_status = False

class Queue_Working_Process(Basic_Output_Process_Mode):
	default_mode = 'loop_with_gap'
	queue = True
	reset_queue_element_internal_params = True

	def get_text_object(self):
		return self.text.refresh_text('Queue class working process is running')

	def set_beginning_indexes(self):
		pass

	def set_ending_indexes(self):
		pass

	def get_next_text(self):
		return self.get_text_object()

	def get_previous_text(self):
		return self.get_text_object()

	def start(self):
		return self.get_text_object()

	def start_with_beginning(self):
		return self.get_text_object()

	@property
	def is_first_message(self):
		return True

	@property
	def is_last_message(self):
		return True

class Dictionary_Queue_Working_Process(Queue_Working_Process):
	repeat_dictionary_status = False # ADD THIS COMMAND IN JS, MAIN OUTPUT_PROCESS, DICTIONARY_O_P

class Message(Basic_Output_Process_Mode):
	default_mode = 'loop_with_gap'

	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.create_text_object()

	def start(self, *args, **kwargs):
		text_object = self.text.refresh_text(*args, **kwargs)
		self.main_output_process.messages_store.add_message(text_object.message_dict)
		return text_object

	def start_with_beginning(self):
		return self.text

class Date_Time(Queue_Working_Process, Message):
	not_scrolling_message_waiting_time_value = 60

	def get_date_time_dict(self):
		return {"string": self.current_time.strftime("%H:%M %d.%m.%y"),
				"letters_colors": {"main_color": {"red":["0-4"],
												"orange":["6-13"]}},
									"direction": "l",
									"mode": "loop_with_gap"}

	def get_text_object(self):
		return self.text.refresh_text(self.get_date_time_dict())

class Volumes_Messages_Queue(Queue_Working_Process):
	refresh_output_process_mode_and_cycles = False # if a message in a volume has distinct mode or a value of cycles
	volumes_names = ['notes', 'newsline']

	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.volumes = main_output_process.led_server.saved_messages_library.get_volumes(self.volumes_names)
		self.set_beginning_indexes()

	def set_messages_volume(self):
		self.volume_messages = self.volumes[self.volume_index]

	def set_messages_volume_with_beginning(self):
		self.set_messages_volume()
		self.message_index = 0
	
	def set_messages_volume_with_ending(self):
		self.set_messages_volume()
		self.message_index = len(self.volume_messages) - 1

	def set_next_messages_volume(self):
		self.volume_index += 1
		if self.volume_index >= len(self.volumes):
			self.volume_index = 0
		self.set_messages_volume_with_beginning()

	def set_previous_messages_volume(self):
		self.volume_index -= 1
		if self.volume_index < 0:
			self.volume_index = len(self.volumes) - 1
		self.set_messages_volume_with_ending()

	def get_message_text_object(self):
		return self.volume_messages[self.message_index]['text_object']

	def get_text_object(self):
		text_object = self.get_message_text_object()
		text_object.wrap_pure_text(self)
		return text_object

	def start(self):
		return self.get_text_object()

	def start_with_beginning(self):
		self.set_beginning_indexes()
		return self.get_text_object()

	def set_beginning_indexes(self):
		self.volume_index = 0
		self.set_messages_volume_with_beginning()

	def set_ending_indexes(self):
		self.volume_index = len(self.volumes) - 1
		self.set_messages_volume_with_ending()

	def get_next_text(self):
		if not self.repeat_message_status:
			self.set_next_message_index()
			return self.get_text_object()
		elif self.refresh_message_status:
			return self.get_text_object()

	def set_next_message_index(self):
		self.message_index += 1
		if self.message_index >= len(self.volume_messages):
			self.set_next_messages_volume()

	def get_previous_text(self):
		if not self.repeat_message_status:
			self.set_previous_message_index()
			return self.get_text_object()

	def set_previous_message_index(self):
		self.message_index -= 1
		if self.message_index < 0:
			self.set_previous_messages_volume()

	@property
	def is_first_volume(self):
		return self.volume_index == 0

	@property
	def is_first_volume_message(self):
		return self.message_index == 0

	@property
	def is_first_message(self):
		return self.is_first_volume and self.is_first_volume_message

	@property
	def is_last_volume(self):
		return self.volume_index == len(self.volumes) - 1

	@property
	def is_last_volume_message(self):
		return self.message_index == len(self.volume_messages) - 1

	@property
	def is_last_message(self):
		return self.is_last_volume and self.is_last_volume_message

class Volumes_Messages_Newsline(Basic_Output_Process_Mode):
	default_mode = 'loop'
	full_screen = False
	refreshable = True
	volumes_names = ['newsline', 'notes']

	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.create_text_object()
		self.volumes = main_output_process.led_server.saved_messages_library.get_volumes(self.volumes_names)

	def get_volumes_border_background_colors(self):
		first_background_color = self.volumes[0].get_first_message_background_color()
		last_background_color = self.volumes[-1].get_last_message_background_color()
		return first_background_color, last_background_color

	def start(self, *args, **kwargs):
		return self.start_with_beginning()

	def start_with_beginning(self):
		return self.refresh_text()

	def refresh_text(self):
		full_text_array = []

		for volume in self.volumes:
			for message in volume:
				text_object = message['text_object']
				text_object.wrap_pure_text(self)
				full_text_array += text_object.full_text_array

		self.text.full_text_array = full_text_array
		self.text.useful_width = self.text.width

		if self.matrix_settings.width >= self.text.width:
			self.text.place_pieces_to_center_to_scrolling()
		self.main_output_process.mode = self.default_mode

		return self.text

class Mixed_Working_Process(Queue_Working_Process):	
	working_processes_names_queue = []
	
	def __init__(self, main_output_process):
		self.set_user_settings(main_output_process)
		self.set_not_scrolling_message_waiting_time()
		self.create_working_process_names(main_output_process.basic_working_processes_classes)
		self.working_processes = main_output_process.working_processes
		self.set_first_working_process()

	def create_working_process_names(self, basic_working_processes_classes):
		main_process_basic_working_processes_names = self.extract_working_processes_names(basic_working_processes_classes)
		if isinstance(self.working_processes_names_queue, list):
			self.basic_working_processes_names = []
			for working_process_name in self.working_processes_names_queue:
				if working_process_name in main_process_basic_working_processes_names:
					self.basic_working_processes_names.append(working_process_name)
			if len(self.basic_working_processes_names) == 0:
				self.basic_working_processes_names = main_process_basic_working_processes_names
		else:
			self.basic_working_processes_names = main_process_basic_working_processes_names

	def extract_working_processes_names(self, basic_working_processes_classes):
		working_processes_names = []
		for basic_working_process_class in basic_working_processes_classes:
			if basic_working_process_class.add_mixed_process:
				working_processes_names.append(basic_working_process_class.__name__.lower())
		return working_processes_names

	def set_first_working_process(self):
		self.set_beginning_indexes()
		self.set_working_process()

	def set_beginning_indexes(self):
		self.working_process_index = 0
		self.working_process_is_queue = False
		self.set_next_working_process_ready_status = False
		self.set_previous_working_process_ready_status = True

	def set_working_process(self):
		working_process_name = self.basic_working_processes_names[self.working_process_index]
		self.working_process = self.get_working_process(working_process_name)

	def start(self):
		return self.get_next_text()

	def start_with_beginning(self):
		self.set_first_working_process()
		self.set_working_process()
		self.refresh_queue_working_processes_indexes()
		return self.get_next_text()

	def set_next_working_process_index(self):
		self.working_process_index += 1
		if self.working_process_index >= len(self.basic_working_processes_names):
			self.working_process_index = 0
	
	def set_previous_working_process_index(self):
		self.working_process_index -= 1
		if self.working_process_index < 0:
			self.working_process_index = len(self.basic_working_processes_names) - 1

	def set_next_working_process(self):
		self.set_next_working_process_index()
		self.set_working_process()
		self.refresh_queue_working_processes_indexes()

	def set_previous_working_process(self):
		self.set_previous_working_process_index()
		self.set_working_process()
		self.refresh_queue_working_processes_indexes(False)

	def refresh_queue_working_processes_indexes(self, position=True):
		if self.working_process.queue:
			self.working_process_is_queue = False
			if position:
				self.working_process.set_beginning_indexes()
			else:
				self.working_process.set_ending_indexes()

	def get_next_text(self):
		if self.set_next_working_process_ready_status:
			self.set_next_working_process()
		if self.working_process.queue:
			if not self.working_process_is_queue and self.working_process.is_first_message: # START QUEUE PROCESS
				self.working_process_is_queue = True
				self.set_next_working_process_ready_status = False
				self.set_previous_working_process_ready_status = True
				return self.working_process.get_text_object()
			elif self.working_process_is_queue and not self.working_process.is_last_message:
				self.set_next_working_process_ready_status = False
				self.set_previous_working_process_ready_status = False
				return self.working_process.get_next_text()
			else: # STOP QUEUE PROCESS AND SET NEXT PROCESS
				self.set_next_working_process_ready_status = True
				self.set_previous_working_process_ready_status = False
				return self.get_next_text()
		else:
			self.set_previous_working_process_ready_status = True
			self.set_next_working_process_ready_status = True
			return self.working_process.start()

	def get_previous_text(self):
		if self.set_previous_working_process_ready_status:
			self.set_previous_working_process()
		if self.working_process.queue:
			if not self.working_process_is_queue and self.working_process.is_last_message:
				self.working_process_is_queue = True
				self.set_previous_working_process_ready_status = False
				self.set_next_working_process_ready_status = True
				return self.working_process.get_text_object()
			elif self.working_process_is_queue and not self.working_process.is_first_message:
				self.set_previous_working_process_ready_status = False
				self.set_next_working_process_ready_status = False
				return self.working_process.get_previous_text()
			else:
				self.set_previous_working_process_ready_status = True
				self.set_next_working_process_ready_status = False
				return self.get_previous_text()
		else:
			self.set_previous_working_process_ready_status = True
			self.set_next_working_process_ready_status = True
			return self.working_process.start()

class Messages_Store(Message, Queue_Working_Process):
	add_mixed_process = False

	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.stack_limit_value = self.user_settings.message_store_limit_value
		self.messages = []
		self.create_text_object()
		self.set_beginning_indexes()

	def set_beginning_indexes(self):
		self.message_index = 0

	def set_ending_indexes(self):
		self.message_index = len(self.messages) - 1

	def get_message_text_object(self):
		if len(self.messages) > 0:
			message_dict = self.messages[self.message_index]
		else:
			message_dict = {'string': 'No received messages',
							'add_in_stack': False}
		return self.text.refresh_text(message_dict)

	def add_message(self, message_dict):
		if message_dict['add_in_stack']:
			if len(self.messages) >= self.stack_limit_value:
				self.messages = self.messages[1:]
			self.messages.append(message_dict)

	def set_next_message_index(self):
		self.message_index += 1
		if self.message_index >= len(self.messages):
			self.message_index = 0

	def set_previous_message_index(self):
		self.message_index -= 1
		if self.message_index < 0:
			self.message_index = len(self.messages) - 1

	def start(self):
		return self.get_text_object()

	def start_with_beginning(self):
		self.set_beginning_indexes()
		return self.get_text_object()

	def get_next_text(self):
		if not self.repeat_message_status:
			self.set_next_message_index()
			return self.get_text_object()

	def get_previous_text(self):
		if not self.repeat_message_status:
			self.set_previous_message_index()
			return self.get_text_object()

	def get_text_object(self):
		return self.get_message_text_object()

	@property
	def is_first_message(self):
		return self.message_index == 0

	@property
	def is_last_message(self):
		return self.message_index == len(self.messages) - 1

class Dictionary(Dictionary_Queue_Working_Process):
	styles_keys = ["main_color", "background_color", "letters_colors", "decorations"]
	path = "api/playlist_set_with_elements_from_queue/?format=json"

	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.set_request_base_url = "{}/{}".format(self.user_settings.servers_addresses['dictionary'], self.path)
		self.attempt = 0
		self.main_part_styles_message_dict = False
		self.create_text_object()
		self.download_dictionary()

	@staticmethod
	def create_dictionary_element(message_text, color=None):
		return {'parts': [{'part': {'content': message_text, 'style': color}}]}

	def create_dictionaty_with_error(self, message_text, color=None):
		self.dictionary = {'elements': [self.create_dictionary_element(message_text, color)]}
		self.parts_languages = {1: 'en'}

	def create_request_url(self):
		self.set_request_url = '{}&attempt={}'.format(self.set_request_base_url, self.attempt)

	def download_dictionary(self, direction=True):
		if direction:
			self.attempt += 1
		else:
			self.attempt -= 1
		
		self.create_request_url()
		try:
			connection = urllib.request.urlopen(self.set_request_url)
			body = connection.read().decode("utf-8")
		except:
			self.create_dictionaty_with_error('Can\'t connect to Dictionary server')
		else:
			if connection.status == 200 and connection.headers['content-type'] == 'application/json':
				self.dictionary = json.loads(body)
				if 'elements' in self.dictionary and 'set' in self.dictionary:
					set_title = self.dictionary['set']['set_properties']['title']
					set_color = {"main_color": self.dictionary['set']['set_properties']['color']}
					if len(self.dictionary['elements']) == 0:
						self.create_dictionaty_with_error('This set \'{}\' doesn\'t have any elements'.format(set_title),
															set_color)
					else:
						self.dictionary['elements'].insert(0, self.create_dictionary_element('Set "{}" beginning'.format(set_title), set_color))
						self.dictionary['elements'].append(self.create_dictionary_element('Set "{}" ending'.format(set_title), set_color))
						self.create_parts_languages()
				elif 'message' in self.dictionary:
					self.create_dictionaty_with_error(self.dictionary["message"])
				else:
					self.create_dictionaty_with_error('Wrong set format')
			elif connection.status == 404:
				self.create_dictionaty_with_error('Set can\'t be found on Dictionary server')
			else:
				self.create_dictionaty_with_error('Dictionary server error')
		self.set_beginning_indexes() if direction else self.set_ending_indexes()

	def create_parts_languages(self):
		self.parts_languages = {}
		for part_type in self.dictionary['set']['parts_types']:
			self.parts_languages[part_type['position']] = part_type['type']['language']['code']

	def set_beginning_indexes(self):
		self.element_index = 0
		self.set_element_with_beginning()

	def set_ending_indexes(self):
		self.element_index = len(self.dictionary['elements']) - 1
		self.set_element_with_ending()

	def set_element_with_beginning(self):
		self.set_element()
		self.part_index = 0

	def set_element_with_ending(self):
		self.set_element()
		self.part_index = len(self.element['parts']) - 1

	def set_element(self):
		self.main_part_styles_message_dict = False
		self.element = self.dictionary['elements'][self.element_index]

	def set_next_part_index(self):
		self.part_index += 1
		if self.part_index >= len(self.element['parts']):
			self.set_next_element()

	def set_previous_part_index(self):
		self.part_index -= 1
		if self.part_index < 0:
			self.set_previous_element()

	def set_next_element(self):
		self.element_index += 1
		if self.element_index >= len(self.dictionary['elements']):
			if self.repeat_dictionary_status:
				self.set_beginning_indexes()
			else:
				self.download_dictionary()
		self.set_element_with_beginning()

	def set_previous_element(self):
		self.element_index -= 1
		if self.element_index < 0:
			if self.repeat_dictionary_status:
				self.set_ending_indexes()
			else:
				pass
				self.download_dictionary(direction=False)
		self.set_element_with_ending()

	def get_message_dict(self, part_index):

		def copy_colors_styles():
			for color_style_key in self.main_part_styles_message_dict:
				message_dict[color_style_key] = self.main_part_styles_message_dict[color_style_key]

		def refresh_styles_for_part_without_styles(part_index):
			if self.main_part_styles_message_dict: # for direct moving
				copy_colors_styles()
			elif part_index != 0: # for reverse moving
				self.get_message_dict(0) # set colors for first part
				if self.main_part_styles_message_dict: # copy colors for this part
					copy_colors_styles()

		def handle_styles(style):
			if len(style) > 0:
				for style_key in self.styles_keys:
					if style_key in style:
						message_dict[style_key] = style[style_key]
				if part_index == 0:
					main_part_styles_message_dict = {}
					for style_key_index in range(2):
						style_key = self.styles_keys[style_key_index]
						if style_key in message_dict:
							main_part_styles_message_dict[style_key] = message_dict[style_key]
					if len(main_part_styles_message_dict) > 0:
						self.main_part_styles_message_dict = main_part_styles_message_dict
			else:
				refresh_styles_for_part_without_styles(part_index)


		part_dict = self.element['parts'][part_index]['part']
		string = part_dict['content']
		language = self.parts_languages[part_index + 1]
		message_dict = {'string': string,
						'language': language,
						'add_in_stack': False}

		if isinstance(part_dict['style'], dict):
			handle_styles(part_dict['style'])
		else:
			try:
				style = json.loads(part_dict['style'])
			except:
				refresh_styles_for_part_without_styles(part_index)
			else:
				handle_styles(style)

		return message_dict

	def get_text_object(self):
		message_dict = self.get_message_dict(self.part_index)
		return self.text.refresh_text(message_dict)	

	def get_next_text(self):
		if not self.repeat_message_status:
			self.set_next_part_index()
			return self.get_text_object()

	def get_previous_text(self):
		if not self.repeat_message_status:
			self.set_previous_part_index()
			return self.get_text_object()

	def start(self, *args, **kwargs):
		if self.reset_queue_element_internal_params and self.part_index > 0:
			self.part_index = 0
		return self.get_text_object()

	def start_with_beginning(self):
		self.set_beginning_indexes()
		return self.get_text_object()

	@property
	def is_first_element(self):
		return self.element_index == 0

	@property
	def is_first_part(self):
		 return self.part_index == 0

	@property
	def is_first_message(self):
		return self.is_first_element and self.is_first_part

	@property
	def is_last_element(self):
		return self.element_index == len(self.dictionary['elements']) - 1

	@property
	def is_last_part(self):
		return self.part_index == len(self.element['parts']) - 1

	@property
	def is_last_message(self):		
		return self.is_last_element and self.is_last_part

class Mind_Calculator(Queue_Working_Process):
	task_tuple = ()
	math_methods = {"+": (lambda x, y: x + y, 'green'),
					"-": (lambda x, y: x - y, 'red'),
					"*": (lambda x, y: x * y, 'orange'),
					"/": (lambda x, y: x / y, 'yellow')}
	
	def __init__(self, main_output_process):
		super().__init__(main_output_process)
		self.create_text_object()

	def create_task(self):
		self.task = (random.randint(2, 99), random.randint(2, 99), random.choice(list(self.math_methods.items())))

	def create_message_dict(self):
		if self.step == 0:
			text = '{} {} {}'.format(self.task[0], self.task[2][0], self.task[1])
			main_color = self.task[2][1][1]
		else:
			result = self.task[2][1][0](self.task[0], self.task[1])
			if result // 1 == 0:
				round_value = 6
			else:
				round_value = 2
			text = str(round(result, round_value))
			main_color = self.task[2][1][1]
		return {'string': text,
				'main_color': main_color}

	def start_new_task(self):
		self.step = 0
		self.create_task()

	def get_text_object(self):
		message_dict = self.create_message_dict()
		return self.text.refresh_text(message_dict)

	def set_beginning_indexes(self):
		self.start_new_task()

	def set_ending_indexes(self):
		self.step = 1
		self.create_task()

	def get_next_text(self):
		self.step += 1
		if self.step > 1:
			self.start_new_task()
		return self.get_text_object()

	def get_previous_text(self):
		self.step -= 1
		if self.step < 0:
			self.step = 0
		return self.get_text_object()

	def start(self):
		self.start_new_task()
		return self.get_text_object()

	def start_with_beginning(self):
		return self.start()

	@property
	def is_first_message(self):
		return self.step == 0

	@property
	def is_last_message(self):
		return self.step == 1