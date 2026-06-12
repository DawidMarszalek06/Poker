from src.cards import (Card, Suit, Rank)
from src.settings import (DEFAULT_CASINO_BALANCE)

class Player:
    def __init__(self, nickname: str, balance: float):
        self.balance = balance
        self.nickname = nickname
        self.hand: list[Card] = []

    def receive_card(self, card: Card):
        self.hand.append(card)

    def __repr__(self):
        return f'(\'{self.nickname}\' | balance: {self.balance})'

class Dealer(Player):
    def __init__(self, casino_balance: float = DEFAULT_CASINO_BALANCE):
        super().__init__(nickname="Dealer", balance=casino_balance)
