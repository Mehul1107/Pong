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
