import pygame
from fonts import SMALL


class Button(object):

    def __init__(self, text, rect, color, text_color, callback, screen, event_manager):
        self.rect = rect
        self.image = pygame.Surface((rect.width, rect.height))
        self.callback = callback
        self.screen = screen

        self.image.fill(color)

        text = SMALL.render(text, True, text_color)
        text_rect = text.get_rect()
        text_rect.center = self.image.get_rect().center
        self.image.blit(text, text_rect)

        self.event_manager = event_manager

    def display(self):
        self.screen.blit(self.image, self.rect)
        pygame.display.update(self.rect)
        self.event_manager.add_click_listener(self.callback, self.rect)

    def clean(self):
        self.event_manager.remove_click_listener(self.callback)
