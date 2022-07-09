import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, 1)
pixels[0] = (10, 0, 0)