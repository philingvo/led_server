#!/usr/bin/python3
#coding: utf-8

from threading import Thread
import socketserver
import socket
from server_handlers import Server_handlers
from matrix_settings import Matrix_Settings
from user_settings import User_Settings
from letters_codes import Letters_Codes
from saved_messages_library import Saved_Messages_Library
from output_process import Main_Output_Process


class LED_Server:

	matrix_settings = Matrix_Settings
	user_settings = User_Settings
	port = User_Settings.port
	mode = User_Settings.mode

	def __init__(self):
		if self.mode: # LED mode
			import board
			import neopixel
			self.pixels = neopixel.NeoPixel(board.D18, self.matrix_settings.pixels_total, brightness=self.matrix_settings.brightness, auto_write=False)
		else: # Test mode
			from test_mode import TestMatrix
			self.pixels = TestMatrix()
			print('local testing mode')

		Server_handlers.led_server = self
		self.letters_codes = Letters_Codes(self)
		self.saved_messages_library = Saved_Messages_Library(self)
		self.main_output_process = Main_Output_Process(self)

	def refresh(self):
		while True:
			self.main_output_process.refresh_standby_process()
			self.main_output_process.refresh_scrolling()

	@property
	def host_IP(self):
		try:
			connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #This assumes you have the internet access, and that there is no local proxy.
			connection.connect(("8.8.8.8", 80))
			host_ip = connection.getsockname()[0]
			connection.close()
			return host_ip
		except:
			return "IP hasn't been found"

	def run(self):

		refresh_thread = Thread(target=self.refresh)
		refresh_thread.start()

		try:
			httpd = socketserver.TCPServer(("0.0.0.0", self.port), Server_handlers)
			httpd.serve_forever()
		finally:
			httpd = socketserver.TCPServer(("0.0.0.0", self.port), Server_handlers)
			httpd.server_close()

if __name__ == '__main__':
	led_server = LED_Server()
	led_server.run()