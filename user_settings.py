#coding: utf-8

class User_Settings:

	mode = False # True - Work, False - Test
	port = 12345

	default_message = False # False - show IP
	default_language = 'en'
	default_direction = True # True - l to r, False - r to l
	default_mode = 'loop_with_gap' # Output mode: 'loop_with_gap', 'loop', 'single'
	default_cycles = 1 # Number of cycles
	default_change_direction = False # False - the same direction as a direction (language) / True - opposite direction
	standby_working_process_name = 'volumes_messages_newsline' # Standby processes names:
																# message
																# date_time
																# volumes_messages_newsline
																# volumes_messages_queue
																# mixed
																# dictionary
																# mind_calculator

	default_start_delay_time = False # (seconds) False - matrix width / 32
	default_scrolling_delay_time = 0.05 # (seconds) Scrolling step time
	not_scrolling_message_waiting_time_values = {'default': 5,
												'queue': 5}
	message_store_limit_value = 10
	servers_addresses = {'dictionary': 'http://127.0.0.1:8050'}
	html_store_path = 'data'
	pieces_filename = 'data/info/info_pieces.json'
	unknown_letters_filename = 'data/letters/unknown_letters.json'
	letters_codes_filename = 'data/letters/letters_codes.json'