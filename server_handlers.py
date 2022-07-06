#coding: utf-8

import os
from http.server import BaseHTTPRequestHandler
import simplejson
import json


class Server_handlers(BaseHTTPRequestHandler):

	default_routes = {'get': 'index', 'post': 'wrong_post'}

	def __init__(self, *args, **kwargs):
		self.html_store_path = self.led_server.user_settings.html_store_path
		self.main_output_process = self.led_server.main_output_process
		self.letters_codes = self.led_server.letters_codes
		self.saved_messages_library = self.led_server.saved_messages_library
		self.routes = {'index': ('get', self.return_page, 'index.html'),
						'send_message': ('get', self.return_page, 'send_message.html'),
						'letters': ('get', self.return_page, 'letters.html'),
						"dictionary": ('get', self.return_page, 'dictionary.html'),
						"learn_words": ('get', self.return_page, 'learn_words.html'),
						
						'unknown_letters': ('get', self.return_unknown_letters_json),
						'letters_codes': ('get', self.return_letters_codes_json),
						'volumes_names': ('get', self.return_volume_names_json),
						'working_processes_names': ('get', self.return_working_processes_names),
						'main_output_process_properties': ('get', self.return_main_output_process_properties),
						'volume_sources': ('post', self.return_volume_sources_json),
						'download_message': ('post', self.return_message_json),
						'save_unknown_letters': ('post', self.save_unknown_letters),
						'change_letters': ('post', self.change_letters),
						'wrong_post': ('post', self.wrong_post),
						'volumes': ('post', self.command_to_volumes),
						'applications_servers': ('get', self.return_applications_servers),
						'': ('post', self.command_to_led)
				}
		#  __init__ requires 3 arguments: request, client_address, and server
		super().__init__(*args, **kwargs)

	def createHeaders(self):
		self.send_header('Access-Control-Allow-Origin', '*')
		self.send_header('Access-Control-Allow-Headers', 'Content-Type,Authorization')
		self.send_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS,DELETE')
		self.end_headers()

	def extract_url(self):
		return self.path.split('/')[1]

	def run_view(self, url, method):
		if url in self.routes:
			if self.routes[url][0] == method:
				if len(self.routes[url]) > 2:
					return self.routes[url][1](self.routes[url][2])
				else:
					return self.routes[url][1]()
			else:
				return self.run_view(self.default_routes[method], method)
		else:
			return self.run_view(self.default_routes[method], method)

	def run_default_view_for_method(self, method):
		return self.run_view(self.default_routes[method], method)

	def create_full_path(self, file_name):
		return os.path.join(self.html_store_path, file_name)

	def extract_json(self, variable):
		return json.dumps(variable).encode()

	def do_GET(self):
		self.send_response(200)
		self.createHeaders()
		response_body = self.run_view(self.extract_url(), 'get')
		self.wfile.write(response_body)

	def return_page(self, page_name):
		path_file_name = self.create_full_path(page_name)
		if not os.path.exists(path_file_name):
			path_file_name = self.create_full_path(self.routes[self.default_routes['get']][2])
		with open(path_file_name, 'r') as file:
			body = file.read()
		return body.encode()

	def return_unknown_letters_json(self):
		return self.extract_json(self.letters_codes.unknown_letters)

	def return_letters_codes_json(self):
		return self.extract_json(self.letters_codes.letters_codes)

	def	return_volume_names_json(self):
		return self.extract_json(self.saved_messages_library.volumes_names)

	def return_applications_servers(self):
		return self.extract_json(self.led_server.user_settings.servers_addresses)

	def return_working_processes_names(self):
		return self.extract_json(self.main_output_process.all_working_processes_names_with_types)

	def return_main_output_process_properties(self):
		return self.extract_json(self.main_output_process.properties)

	def return_volume_sources_json(self):
		return 200, self.extract_json(self.saved_messages_library.get_volume_properties(self.post_dict))

	def return_message_json(self):
		return 200, self.extract_json(self.saved_messages_library.get_message(self.post_dict))

	def do_POST(self):
		post_body = self.rfile.read(int(self.headers['Content-Length']))
		self.post_dict = simplejson.loads(post_body)
		url = self.extract_url()
		print('PATH:', url)
		print("POST RECEIVED:", self.post_dict)

		response_code, response_body = self.run_view(url, 'post')
		self.send_response(response_code)

		self.createHeaders()
		if isinstance(response_body, str):
			response_body = response_body.encode()
		self.wfile.write(response_body)

	def wrong_post(self):
		if 'string' in self.post_dict:
			return self.command_to_led()
		else:
			return 200, 'Wrong address'

	def command_to_led(self):
		message_dict = self.post_dict
		response_code = 200
		if 'string' in message_dict: # RECEIVE A MESSAGE
			response_body = self.main_output_process.recieve_message(message_dict)
		elif 'command' in message_dict: # RECEIVE A CONTROL COMMAND
			response_body = self.main_output_process.control_command(message_dict)
		else:
			response_body = 'Wrong message format'
		return response_code, response_body

	def command_to_volumes(self):
		message_dict = self.post_dict
		response_body = 'Command has been received'
		response_code = 200
		if 'source' in message_dict and 'volume' in message_dict:
			response_body = self.saved_messages_library.change_message(message_dict)
		elif 'command' in message_dict and message_dict['command'] == 'save_all':
			response_body = self.saved_messages_library.save_all_volumes()
		elif 'command' in message_dict and message_dict['command'] == 'save_volume':
			self.saved_messages_library.save_volume(message_dict)
		else:
			response_body = 'Wrong message format for this command'
		return response_code, response_body

	def save_unknown_letters(self):
		response_body = self.main_output_process.letters_codes.save_new_letter(self.post_dict)
		self.main_output_process.show_text(self.post_dict['letter'])
		return 200, response_body

	def change_letters(self):
		response_body = self.main_output_process.letters_codes.change_letter(self.post_dict)
		self.main_output_process.show_text(self.post_dict['letter'])
		return 200, response_body

	def do_OPTIONS(self):
		pass