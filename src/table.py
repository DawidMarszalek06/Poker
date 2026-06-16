from src.players import Player, Dealer
from src.cards import Deck

class Table:
    def __init__(self, players: list[Player]):
        dealer = None
        for player in players:
            if isinstance(player, Dealer):
                dealer = player
                players.remove(dealer)
                break
        self.dealer = dealer
        self.players = players
        self.game_round = 0

    def prepare_new_deal(self):
        self.game_round += 1
        self.pot = 0
        self.cards_on_the_table = []
        self.deck = Deck()

        if self.dealer:
            self.dealer.hand.clear()

        for player in self.players:
            player.hand.clear()
    def deal_initial_cards(self):
        #tu rozdajemy po dwie karty graczom
        for _ in range(2):
            #rozdajemy kazdemu graczowi
            for player in self.players:
                player.receive_card(self.deck.get_card())
            
            # Rozdajemy krupierowi 
            if self.dealer:
                self.dealer.receive_card(self.deck.get_card())
                
        #rozdanie flopa (3kart)
        for _ in range(3):
            self.cards_on_the_table.append(self.deck.get_card())
        