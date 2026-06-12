import pygame

from src.players import Player, Dealer
from src.settings import (SCREEN_HEIGHT, SCREEN_WIDTH)
from src.cards import (Card, Rank, Suit)
from src.table import Table

class Game:
    def __init__(self):
        pygame.init()
        #self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #pygame.display.set_caption("Poker")
        self.clock = pygame.time.Clock()

        player = Player("igor", 100)
        dealer = Dealer()

        table = Table([player, dealer])
        table.prepare_new_deal()


    def run(self):
        ...