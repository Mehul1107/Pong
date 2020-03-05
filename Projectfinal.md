##`properties.py`
```python
"""Contains changeable properties relevant to different aspects of the game."""

FPS = 80

SCREEN_WIDTH = 1200
BOARD_HEIGHT = 600
HALF_WIDTH = SCREEN_WIDTH / 2
HALF_HEIGHT = BOARD_HEIGHT / 2
CONTROLS_HEIGHT = 100
SCREEN_HEIGHT = BOARD_HEIGHT + CONTROLS_HEIGHT
SCREEN_CENTER = (HALF_WIDTH, SCREEN_HEIGHT / 2)

BORDER_THICKNESS = 20
HALF_BORDER = BORDER_THICKNESS / 2
```

##`basicpages.py`
```python
from colors import ORANGE, CORNSILK, WHITE, BLACK
from fonts import SMALL, XLARGE, LARGE, MEDLARGE
from properties import SCREEN_CENTER, HALF_WIDTH
from button import Button
from eventmanager import EventManager
import pygame
from properties import *
from leaderboard import LeaderBoard

class Page(object):
    def __init__(self, screen, color, event_manager):
        self.color = color
        self.screen = screen
        self.buttons = []
        self.texts = []
        self.textboxes = []
        self.caption = "PONG!!!"
        self.event_manager = event_manager

    def display(self):
        pygame.display.set_caption(self.caption)
        self.screen.fill(self.color)
        for text, text_rect in self.texts:
            self.screen.blit(text, text_rect)
        for button in self.buttons:
            button.display()
        pygame.display.flip()

    def clean(self):
        for button in self.buttons:
            button.clean()

class SplashScreen(Page):
    def __init__(self, screen, event_manager):
        super(SplashScreen, self).__init__(screen, ORANGE, event_manager)

        splash = XLARGE.render("PONG!!!", True, WHITE)
        splash_rect = splash.get_rect()
        splash_rect.center = SCREEN_CENTER

        self.texts.append((splash, splash_rect))

class TextInput(Page):
    def __init__(self, screen, event_manager, prompt, callback):
        super(TextInput, self).__init__(screen, CORNSILK, event_manager)

        prompt = MEDLARGE.render(prompt, True, ORANGE)
        prompt_rect = prompt.get_rect()
        prompt_rect.topleft = (20, HALF_HEIGHT - 100)

        self.texts.append((prompt, prompt_rect))

        self.value = ""
        self.value_rect = pygame.Rect(0, HALF_HEIGHT, SCREEN_WIDTH, 140)
        self.value_surface = pygame.Surface((SCREEN_WIDTH, 140))

        def cb():
            callback(self.value)

        submit_rect = pygame.Rect(0, 0, 100, 60)
        submit_rect.bottomright = (SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20)
        submit = Button("Submit", submit_rect, ORANGE, WHITE, cb, screen, event_manager)

        self.buttons.append(submit)
       
    def display(self):
        super(TextInput, self).display()
        self.event_manager.add_input_listener(self.add_text)
        self.show_value()
    
    def show_value(self):
        value_img = MEDLARGE.render(self.value, True, BLACK)
        self.value_surface.fill(WHITE)
        self.value_surface.blit(value_img, (20, 20))
        self.screen.blit(self.value_surface, (0, HALF_HEIGHT))
        pygame.display.update(self.value_rect)
    
    def add_text(self, letter):
        if letter == -1:
            self.value = self.value[:-1]
        else:
            self.value += letter
        
        self.show_value()
    
    def clean(self):
        super(TextInput, self).clean()
        self.event_manager.remove_input_listener(self.add_text)

class LeaderBoardPage(Page):
    def __init__(self, screen, event_manager):
        super(LeaderBoardPage, self).__init__(screen, CORNSILK, event_manager)

        header = LARGE.render("Leaderboard", True, ORANGE)
        header_rect = header.get_rect()
        header_rect.midtop = (HALF_WIDTH, 20)
        
        heading = SMALL.render("Rank |         Name         | Matches Played | Wins | Losses | Point Difference | Win Percentage", True, ORANGE)
        heading_rect = heading.get_rect()
        heading_rect.midtop = (HALF_WIDTH, 150)

        self.texts.extend([(header, header_rect), (heading, heading_rect)])

        self.leaderboard = LeaderBoard()
    
    def display(self):
        del self.texts[2:]
        TOP = self.texts[1][1].top + 35
        
        format_string = "{rank:>4d} | {name:20s} | {matches_played:>14d} | {wins:>4d} | {losses:>6d} | {point_diff:>16d} | {win_per:>14.2f}"
        for index, leader in enumerate(self.leaderboard.get_top_number(10)):
            res = SMALL.render(format_string.format(**dict(zip(("rank", "name", "matches_played", "wins", "losses", "point_diff", 
            "win_per"), leader))), True, BLACK)
            res_rect = res.get_rect()
            res_rect.top = TOP + 35 * index
            res_rect.centerx = HALF_WIDTH
            self.texts.append((res, res_rect))
        
        super(LeaderBoardPage, self).display()

if __name__ == '__main__':
    from properties import SCREEN_HEIGHT, SCREEN_WIDTH
    from eventmanager import EventManager
    c = pygame.time.Clock()
    s = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    e = EventManager()
    l = LeaderBoardPage(s, e)
    l.display()
    while True:
        e.run()
        c.tick(30)
```

##`boardpage.py`
```python
import pygame
from properties import SCREEN_WIDTH, BOARD_HEIGHT, CONTROLS_HEIGHT, HALF_HEIGHT, HALF_WIDTH, BORDER_THICKNESS, HALF_BORDER
from gameobjects import Paddle, Ball
from colors import CORNSILK, ORANGE, RED, WHITE, BLACK
from fonts import NORMAL, MEDLARGE
from basicpages import Page
from leaderboard import LeaderBoard

LINE_THICKNESS = 2

ARENA = pygame.Surface((SCREEN_WIDTH, BOARD_HEIGHT))
ARENA.fill(CORNSILK)

pygame.draw.line(ARENA, ORANGE, (HALF_WIDTH, 0),
                 (HALF_WIDTH, BOARD_HEIGHT), LINE_THICKNESS)
pygame.draw.rect(
    ARENA, ORANGE, ((0, 0), (SCREEN_WIDTH, BOARD_HEIGHT)), BORDER_THICKNESS)
pygame.draw.circle(ARENA, ORANGE, (HALF_BORDER, HALF_HEIGHT), 2 * BOARD_HEIGHT / 5, LINE_THICKNESS)
pygame.draw.circle(ARENA, ORANGE, (SCREEN_WIDTH - HALF_BORDER, HALF_HEIGHT), 2 * BOARD_HEIGHT / 5, LINE_THICKNESS)


class BoardPage(Page):
    LINE_THICKNESS = 2
    ARENA = ARENA
    WINNING_SCORE = 3

    def __init__(self, screen, event_manager, names, finish_cb):
        super(BoardPage, self).__init__(screen, CORNSILK, event_manager)

        def game_end_listener(winner):
            self.suspended = True
            self.score_board.update(winner)
            if not any(score == BoardPage.WINNING_SCORE for score in self.score_board.scores):
                event_manager.add_timer(1, self.reset)
            else:
                self.declare_winner()
                event_manager.add_timer(3, finish_cb)

        event_manager.add_game_end_listener(game_end_listener)
        event_manager.add_tick_listener(self.run)
        self.event_manager = event_manager

        self.paddle_1 = Paddle(30, RED, pygame.K_w, pygame.K_s, event_manager)
        self.paddle_2 = Paddle(1160, RED, pygame.K_UP,
                               pygame.K_DOWN, event_manager)
        self.paddles = pygame.sprite.RenderUpdates()
        self.paddles.add(self.paddle_1, self.paddle_2)

        self.ball = Ball(RED, (self.paddle_1, self.paddle_2), event_manager)
        self.ball_group = pygame.sprite.RenderUpdates()
        self.ball_group.add(self.ball)

        self.suspended = True
        self.score_board = ScoreBoard(names, screen, event_manager)
    
    def declare_winner(self):
        self.score_board.store_result()
        winner = 0 if self.score_board.scores[0] == BoardPage.WINNING_SCORE else 1
        name = MEDLARGE.render(self.score_board.names[winner], True, BLACK)
        name_rect = name.get_rect()
        name_rect.center = (HALF_WIDTH, HALF_HEIGHT - 80)

        wins = MEDLARGE.render("Wins!!!", True, BLACK)
        wins_rect = wins.get_rect()
        wins_rect.center = (HALF_WIDTH, HALF_HEIGHT + 10)

        self.screen.blit(name, name_rect)
        self.screen.blit(wins, wins_rect)
        pygame.display.update((name_rect, wins_rect))
    
    def display(self):
        super(BoardPage, self).display()
        self.score_board.render()
        self.reset(2)
    
    def start(self):
        self.suspended = False

    def reset(self, delay=0):
        self.screen.blit(ARENA, (0, 0))

        self.paddle_1.reset()
        self.paddle_2.reset()
        self.ball.reset()

        self.paddles.clear(self.screen, ARENA)
        self.ball_group.clear(self.screen, ARENA)

        self.paddles.draw(self.screen)
        self.ball_group.draw(self.screen)

        pygame.display.flip()
        self.event_manager.add_timer(delay, self.start)
    
    def clean(self):
        super(BoardPage, self).clean()
        self.event_manager.remove_tick_listener(self.run)
        self.paddle_1.clean()
        self.paddle_2.clean()

    def run(self):
        if not self.suspended:
            self.paddles.clear(self.screen, ARENA)
            self.ball_group.clear(self.screen, ARENA)

            self.ball_group.update()

            pygame.display.update(self.paddles.draw(self.screen))
            pygame.display.update(self.ball_group.draw(self.screen))


class ScoreBoard(object):
    def __init__(self, names, screen, event_manager):
        self.names = names
        self.screen = screen
        self.background = pygame.Surface((SCREEN_WIDTH, CONTROLS_HEIGHT))
        self.rect = self.background.get_rect()
        self.rect.topleft = (0, BOARD_HEIGHT)
        self.leaderboard = LeaderBoard()

        self.scores = [0, 0]

    def update(self, winner):
        self.scores[winner] += 1
        self.render()

    def render(self):
        self.background.fill(ORANGE)
        for number in xrange(2):
            self.background.blit(
                NORMAL.render(str(self.scores[number]), True, WHITE),
                (HALF_WIDTH * (number + 1) - HALF_BORDER - 40, HALF_BORDER))
            self.background.blit(
                NORMAL.render(self.names[number], True, WHITE),
                (HALF_WIDTH * number + HALF_BORDER, HALF_BORDER))
        self.screen.blit(self.background, self.rect)
        pygame.display.update(self.rect)
    
    def store_result(self):
        for index in range(2):
            self.leaderboard.store_match_result(self.names[index], self.scores[index] - self.scores[index ^ 1])
```

## `button.py`
```python
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
```

## `colors.py`
```python
"""Named colors for reusability."""

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
ORANGE = (255, 165, 0)
WHITE = (255, 255, 255)
CORNSILK = (255, 230, 220)
```

## `eventmanager.py`
```python
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
```

##`fonts.py`
```python
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
```

##`gameobjects.py`
```python
import random

import pygame

from properties import BOARD_HEIGHT, SCREEN_WIDTH, HALF_HEIGHT, HALF_WIDTH, HALF_BORDER


class Paddle(pygame.sprite.DirtySprite):
    PADDLE_HEIGHT = 100
    PADDLE_WIDTH = 15
    MOVE_DISTANCE = 5
    TOP = HALF_BORDER
    BOTTOM = BOARD_HEIGHT - HALF_BORDER

    def __init__(self, x_coordinate, color, up_key, down_key, event_manager):
        super(Paddle, self).__init__()

        self.image = pygame.Surface(
            (Paddle.PADDLE_WIDTH, Paddle.PADDLE_HEIGHT))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.x_coordinate = x_coordinate

        self.reset()

        def up_mover():
            if self.rect.top >= Paddle.TOP + Paddle.MOVE_DISTANCE:
                self.move(-Paddle.MOVE_DISTANCE)

        def down_mover():
            if self.rect.bottom <= Paddle.BOTTOM - Paddle.MOVE_DISTANCE:
                self.move(Paddle.MOVE_DISTANCE)

        event_manager.add_key_listener(up_key, up_mover)
        event_manager.add_key_listener(down_key, down_mover)

        self.up_mover = up_mover
        self.down_mover = down_mover
        self.up_key = up_key
        self.down_key = down_key
        self.event_manager = event_manager

    def reset(self):
        self.rect.center = (
            self.x_coordinate + Paddle.PADDLE_WIDTH / 2, HALF_HEIGHT)
    
    def clean(self):
        self.event_manager.remove_key_listener(self.up_key, self.up_mover)
        self.event_manager.remove_key_listener(self.down_key, self.down_mover)

    def move(self, distance):
        """Moves the Paddle rect

        -ve: Move up
        +ve: Move down
        """
        self.dirty = 1
        self.rect.move_ip(0, distance)


class Ball(pygame.sprite.DirtySprite):
    BALL_DIMENSIONS = 12
    MOVE_DISTANCE = 8
    TOP = HALF_BORDER
    BOTTOM = BOARD_HEIGHT - HALF_BORDER
    LEFT = HALF_BORDER
    RIGHT = SCREEN_WIDTH - HALF_BORDER
    DIRECTIONS = (-1, 1)

    def __init__(self, color, paddles, event_manager):
        super(Ball, self).__init__()

        self.dirty = 2
        self.image = pygame.Surface(
            (Ball.BALL_DIMENSIONS, Ball.BALL_DIMENSIONS))
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.center = (HALF_WIDTH, HALF_HEIGHT)

        self.x_velocity = random.choice(Ball.DIRECTIONS) * Ball.MOVE_DISTANCE
        self.y_velocity = random.choice(Ball.DIRECTIONS) * Ball.MOVE_DISTANCE

        self.left_paddle, self.right_paddle = paddles
        self.left_limit = self.left_paddle.rect.right
        self.right_limit = self.right_paddle.rect.left

        self.not_crossed = True
        self.event_manager = event_manager

    def reflect_coordinate(self, reference, coordinate, velocity):
        return 2 * reference - coordinate - velocity

    def move_y(self):
        if Ball.TOP > self.rect.top + self.y_velocity:
            self.rect.top = self.reflect_coordinate(
                Ball.TOP, self.rect.top, self.y_velocity)
        elif Ball.BOTTOM < self.rect.bottom + self.y_velocity:
            self.rect.bottom = self.reflect_coordinate(
                Ball.BOTTOM, self.rect.bottom, self.y_velocity)
        else:
            self.rect.move_ip(0, self.y_velocity)
            return
        self.y_velocity *= -1

    def in_limits(self, paddle):
        return paddle.rect.bottom >= self.rect.centery >= paddle.rect.top

    def move_x(self):
        if self.in_limits(self.left_paddle) and 0 >= self.left_limit - self.rect.left > self.x_velocity:
            self.rect.left = self.reflect_coordinate(
                self.left_limit, self.rect.left, self.x_velocity)
        elif self.in_limits(self.right_paddle) and 0 <= self.right_limit - self.rect.right < self.x_velocity:
            self.rect.right = self.reflect_coordinate(
                self.right_limit, self.rect.right, self.x_velocity)
        else:
            self.rect.move_ip(self.x_velocity, 0)
            return
        self.x_velocity *= -1

    def update(self):
        self.move_x()
        self.move_y()
        if self.rect.left <= Ball.LEFT or self.rect.right >= Ball.RIGHT:
            winner = 1 if self.rect.left <= Ball.LEFT else 0
            self.not_crossed = False
            if self.rect.left <= Ball.LEFT:
                xloc = Ball.LEFT
            else:
                xloc = Ball.RIGHT - Ball.BALL_DIMENSIONS
            self.rect.move_ip(0, abs(xloc - self.rect.left) * (self.y_velocity / abs(self.y_velocity)))
            self.rect.left = xloc
            self.event_manager.notify_game_end(winner)

    def reset(self):
        self.rect.center = (HALF_WIDTH, HALF_HEIGHT)
```

##`leaderboard.py`
```python
import pickle as p

NAME = 0
POINT_DIFFS = 1
WINS = 2
MATCHES = 3

class LeaderBoard(object):
    def __init__(self):
        self.file = "leaderlist.dat"
        with open(self.file, "ab") as _:
            pass



    @staticmethod
    def win_percentage(person):
        return float(person[WINS] * 100) / person[MATCHES]


    @staticmethod
    def compare_leaders(person_1, person_2):
        return cmp((LeaderBoard.win_percentage(person_1), person_1[POINT_DIFFS], person_1[WINS]),
                    (LeaderBoard.win_percentage(person_2), person_2[POINT_DIFFS], person_2[WINS]))

    @staticmethod
    def sort(array):
        return sorted(array, cmp=LeaderBoard.compare_leaders, reverse=True)

    def get_top_number(self, number):
        with open(self.file, "rb") as f:
            raw_leaders = LeaderBoard.sort(p.load(f))[:number]

        new_leaders = []
        prev_leader = ["Batman", 0, 2, 1]
        rank = 0
        count = 1
        for leader in raw_leaders:
            if LeaderBoard.compare_leaders(leader, prev_leader) == -1:
                rank += count
                count = 1
            else:
                count += 1

            new_leaders.append(
                [rank, leader[NAME], leader[MATCHES], leader[WINS], leader[MATCHES] - leader[WINS], leader[POINT_DIFFS], LeaderBoard.win_percentage(leader)]
            )

            prev_leader = leader

        return new_leaders

    def store_match_result(self, name, point_diff):
        with open(self.file, "rb") as f:
            try:
                people = p.load(f)
            except:
                people = []

        for person in people:
            if person[NAME].lower() == name.lower():
                person[MATCHES] += 1
                person[POINT_DIFFS] += point_diff
                if point_diff > 0:
                    person[WINS] += 1
                break
        else:
            people.append([name, point_diff, 1 if point_diff > 0 else 0, 1])

        with open(self.file, "wb") as f:
            p.dump(people, f)
```

##`main.py`
```python
import pygame
from eventmanager import EventManager
from basicpages import Page, SplashScreen, TextInput, LeaderBoardPage
from boardpage import BoardPage
from colors import BLACK
from properties import SCREEN_WIDTH, SCREEN_HEIGHT, FPS

class Browser(object):
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.event_manager = EventManager()
        self.current_page = Page(pygame.Surface((0, 0)), BLACK, self.event_manager)

        self.name_1 = "Batman"
        self.name_2 = "Superman"
    
    def get_shower(self, klass, *args):
        def shower():
            self.current_page.clean()
            self.current_page = klass(self.screen, self.event_manager, *args)
            self.current_page.display()
        return shower
    
    def run(self):
        self.get_shower(SplashScreen)()

        def cb1(value):
            self.name_1 = value
            self.get_shower(TextInput, "Enter Player 2's name", cb2)()
            
        def finish_cb():
            self.get_shower(LeaderBoardPage)()
        
        def cb2(value):
            self.name_2 = value
            self.get_shower(BoardPage, (self.name_1, self.name_2), finish_cb)()
        
        self.event_manager.add_timer(2, self.get_shower(TextInput, "Enter Player 1's name", cb1))

        while True:
            self.event_manager.run()
            self.clock.tick(FPS)
if __name__ == '__main__':
    BROWSER = Browser()
    BROWSER.run()
```



