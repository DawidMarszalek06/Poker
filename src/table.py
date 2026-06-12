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

        # Dalej rozdanie kart graczom itp.