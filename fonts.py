from sys import platform

import pygame
pygame.init()

if platform.startswith("linux") or platform == "darwin":
    FONT_NAME = "FreeMono"
else:
    FONT_NAME = "Lucida Console"

SMALL = pygame.font.SysFont(FONT_NAME, 20)
NORMAL = pygame.font.SysFont(FONT_NAME, 40)
MEDLARGE = pygame.font.SysFont(FONT_NAME, 80)
LARGE = pygame.font.SysFont(FONT_NAME, 100)
XLARGE = pygame.font.SysFont(FONT_NAME, 280)
