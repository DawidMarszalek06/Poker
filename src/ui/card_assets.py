import pygame

from src.cards import Card, Rank, Suit
from src.settings import ASSETS_DIR, CARD_HEIGHT, CARD_WIDTH

SPRITE_W = 88
SPRITE_H = 124
COLS = 5

SUIT_FILES = {
    Suit.HEARTS: "Hearts-88x124.png",
    Suit.DIAMONDS: "Diamonds-88x124.png",
    Suit.CLUBS: "Clubs-88x124.png",
    Suit.SPADES: "Spades-88x124.png",
}


def rank_to_index(rank: Rank) -> int:
    if rank == Rank.ACE:
        return 0
    return rank.value - 1


def _is_background(r: int, g: int, b: int, key: tuple[int, int, int], tolerance: int) -> bool:
    if max(abs(r - key[0]), abs(g - key[1]), abs(b - key[2])) <= tolerance:
        return True
    # zaokraglone rogi maja piksele pomiedzy teal a bialym
    return g > 70 and b > 70 and g - r > 15 and b - r > 15


def _remove_background(sprite: pygame.Surface, tolerance: int = 45) -> pygame.Surface:
    key = sprite.get_at((0, 0))[:3]
    w, h = sprite.get_size()
    clean = pygame.Surface((w, h), pygame.SRCALPHA)

    for y in range(h):
        for x in range(w):
            r, g, b = sprite.get_at((x, y))[:3]
            if _is_background(r, g, b, key, tolerance):
                clean.set_at((x, y), (0, 0, 0, 0))
            else:
                clean.set_at((x, y), (r, g, b, 255))

    return clean


def _load_sheet(path: str) -> pygame.Surface:
    return pygame.image.load(path).convert()


def _cut_sprite(sheet: pygame.Surface, rect: pygame.Rect, width: int, height: int) -> pygame.Surface:
    sprite = sheet.subsurface(rect).copy()
    sprite = _remove_background(sprite)
    return pygame.transform.smoothscale(sprite, (width, height))


class CardSprites:
    DECK_W = 55
    DECK_H = 88

    def __init__(self):
        self.sprites: dict[tuple[Suit, Rank], pygame.Surface] = {}
        cards_dir = ASSETS_DIR / "Cards"

        for suit, filename in SUIT_FILES.items():
            sheet = _load_sheet(str(cards_dir / filename))
            for rank in Rank:
                index = rank_to_index(rank)
                col = index % COLS
                row = index // COLS
                rect = pygame.Rect(col * SPRITE_W, row * SPRITE_H, SPRITE_W, SPRITE_H)
                self.sprites[(suit, rank)] = _cut_sprite(sheet, rect, CARD_WIDTH, CARD_HEIGHT)

        back_sheet = _load_sheet(str(cards_dir / "Card_Back-88x124.png"))
        back_rect = pygame.Rect(0, 0, SPRITE_W, SPRITE_H)
        self.card_back = _cut_sprite(back_sheet, back_rect, CARD_WIDTH, CARD_HEIGHT)

        deck_sheet = _load_sheet(str(cards_dir / "Card_DeckA-88x140.png"))
        deck_rect = pygame.Rect(88, 0, 88, 140)  # czerwony jak rewers kart krupiera
        self.deck = _cut_sprite(deck_sheet, deck_rect, self.DECK_W, self.DECK_H)

    def get(self, card: Card) -> pygame.Surface:
        return self.sprites[(card.suit, card.rank)]

    def get_back(self) -> pygame.Surface:
        return self.card_back

    def get_deck(self) -> pygame.Surface:
        return self.deck
