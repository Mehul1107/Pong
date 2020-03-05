import sys
import heapq

import pygame
from properties import FPS


class EventManager(object):
    """An event manager that dispatches event listeners."""

    def __init__(self):
        self.key_listeners = {}
        self.exit_listeners = set()
        self.game_end_listeners = set()
        self.timed = []
        self.ticker = 0
        self.input_listeners = set()
        self.click_listeners = {}
        self.tick_listeners = set()
        self.num_timers = 0

    def add_exit_listener(self, listener):
        self.exit_listeners.add(listener)

    def add_key_listener(self, key, listener):
        try:
            self.key_listeners[key].add(listener)
        except KeyError:
            self.key_listeners[key] = set()
            self.add_key_listener(key, listener)

    def remove_key_listener(self, key, listener):
        self.key_listeners[key].remove(listener)

    def notify_game_end(self, winner):
        for listener in self.game_end_listeners:
            listener(winner)

    def add_game_end_listener(self, listener):
        self.game_end_listeners.add(listener)

    def add_timer(self, seconds, listener):
        heapq.heappush(self.timed, (self.ticker +
                                    int(seconds * FPS), self.num_timers, listener))
        self.num_timers += 1

    def add_input_listener(self, listener):
        self.input_listeners.add(listener)

    def remove_input_listener(self, listener):
        self.input_listeners.remove(listener)

    def add_click_listener(self, listener, rect):
        self.click_listeners[listener] = rect

    def remove_click_listener(self, listener):
        del self.click_listeners[listener]

    def add_tick_listener(self, listener):
        self.tick_listeners.add(listener)

    def remove_tick_listener(self, listener):
        self.tick_listeners.remove(listener)

    def run(self):
        pressed = pygame.key.get_pressed()
        for listener in self.tick_listeners:
            listener()

        for key in self.key_listeners:
            if pressed[key]:
                for listener in self.key_listeners[key]:
                    listener()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.key_listeners = None
                self.game_end_listeners = None

                for listener in self.exit_listeners:
                    listener()
                self.exit_listeners = None
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                try:
                    if event.key == pygame.K_BACKSPACE:
                        for listener in self.input_listeners:
                            listener(-1)
                    elif 'a' <= chr(event.key) <= 'z' or '0' <= chr(event.key) <= '9' or event.key == pygame.K_SPACE:
                        if pressed[pygame.K_RSHIFT] or pressed[pygame.K_LSHIFT]:
                            char = chr(event.key).upper()
                        else:
                            char = chr(event.key)
                        for listener in self.input_listeners:
                            listener(char)
                except ValueError:
                    pass
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                for listener, rect in self.click_listeners.items():
                    if rect.left <= event.pos[0] <= rect.right and rect.top <= event.pos[1] <= rect.bottom:
                        listener()

        while self.timed and self.ticker >= self.timed[0][0]:
            self.timed[0][2]()
            heapq.heappop(self.timed)

        self.ticker += 1
