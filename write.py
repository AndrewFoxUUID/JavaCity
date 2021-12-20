import pygame
from characters import *

def write(surface, string, coord, color=(0, 0, 0), size=1):
    x_indent = 0
    y_indent = 0
    for letter in string:
        if letter == '\n':
            y_indent += 14*size
            x_indent = 0
        else:
            for r, row in enumerate(characters[letter]):
                for c, item in enumerate(row):
                    if item == 1:
                        pygame.draw.rect(surface, color, (coord[0] + x_indent + size*c, coord[1] + y_indent + size*r, size, size))
            x_indent += 6*size

def writtenlen(string):
    return max([len(line) for line in string.split('\n')])*6 - 1