import board
import neopixel

pixels = neopixel.NeoPixel(board.D18, 17)
pixels[0] = (10, 0, 0)
pixels[7] = (0, 10, 0)
pixels[16] = (0, 0, 10)