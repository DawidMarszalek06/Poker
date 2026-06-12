import random
from enum import Enum

class Suit(Enum):
    HEARTS = "Hearts"
    DIAMONDS = "Diamonds"
    CLUBS = "Clubs"
    SPADES = "Spades"

class Rank(Enum):
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    SIX = 6
    SEVEN = 7
    EIGHT = 8
    NINE = 9
    TEN = 10
    JACK = 11
    QUEEN = 12
    KING = 13
    ACE = 14

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        if not isinstance(suit, Suit):
            raise TypeError(
                f"Nieprawidłowy kolor! Musisz użyć klasy Suit, a podano: {type(suit)}"  #
            )
        if not isinstance(rank, Rank):
            raise TypeError(
                f"Nieprawidłowa ranga! Musisz użyć klasy Rank, a podano: {type(rank)}"
            )
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return f'{self.rank.name} {self.suit.name}'

    def __str__(self):
        return f'{self.rank.name} {self.suit.name}'

# Tworzy nową potasowaną talie
class Deck:
    def __init__(self):
        self.cards = [Card(suit, rank) for rank in Rank for suit in Suit]
        random.shuffle(self.cards)

    def get_card(self):
        return self.cards.pop()

    def size(self):
        return len(self.cards)

    def __repr__(self):
        return [card.__repr__() for card in self.cards].__str__()

    def __str__(self):
        return [card.__str__() for card in self.cards].__str__()

