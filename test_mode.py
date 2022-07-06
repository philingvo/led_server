#coding: utf-8

import pygame
import sys
from pygame.locals import *
from color_codes import color_codes
from matrix_settings import Matrix_Settings
from matrix_array import get_matrix_array


class TestMatrix:
    pixel_size = 20
    
    def __init__(self):
        self.matrix_settings = Matrix_Settings()
        self.matrix_array = get_matrix_array(self.matrix_settings)
        self.pixels = []
        self.pixels_adresses = []
        
        for pixel_number in range(self.matrix_settings.pixels_total):
            self.pixels.append(color_codes[self.matrix_settings.background_color])
            self.pixels_adresses.append(pixel_number)
        
        for row_number in range(len(self.matrix_array)):
            for column_number in range(len(self.matrix_array[row_number])):
                pixel_number = self.matrix_array[row_number][column_number]
                self.pixels_adresses[pixel_number] = (column_number, row_number)
        
        self.led_init()
    
    def __len__(self):
        return len(self.pixels)
    
    def __next__(self, i = 0):
        if i < len(self)-1:
            i += 1            
            return self[i]
        raise StopIteration();
        
    def __getitem__(self, index):
        return self.pixels[index]
    
    def __setitem__(self, index, color):
            self.pixels[index] = color
            
    def led_init(self):
        pygame.init()
        FPSCLOCK = pygame.time.Clock()
        self.DISPLAYSURF = pygame.display.set_mode((self.pixel_size*self.matrix_settings.width, self.pixel_size*self.matrix_settings.height))
        BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
        BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
        pygame.display.set_caption('Scroller Test')
        BGCOLOR = (0,0,0) # BLACK
        self.DISPLAYSURF.fill(BGCOLOR)
        pygame.display.update()
    
    def show(self):        
        for pixel_number in range(len(self.pixels)):
            pixel_adress = self.pixels_adresses[pixel_number]
            x = pixel_adress[0]
            y = pixel_adress[1]
            color_code = self.pixels[pixel_number]
            self.draw_pixel(x, y, color_code)
        
    def draw_pixel(self, x, y, color_code):        
        pygame.draw.rect(self.DISPLAYSURF, color_code, (x*self.pixel_size+1, y*self.pixel_size+1, self.pixel_size-2, self.pixel_size-2))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        pygame.display.update()