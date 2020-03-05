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
    WINNING_SCORE = 10

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

