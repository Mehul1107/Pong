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
