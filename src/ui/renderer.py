import pygame

# Proste funkcje rysujace stol, karty i przyciski (Pygame UI)

from src.cards import Card, Rank, Suit
from src.settings import CARD_HEIGHT, CARD_WIDTH
from src.ui.card_assets import CardSprites

TABLE_GREEN = (0, 90, 0)
TABLE_DARK = (0, 60, 0)
WHITE = (255, 255, 255)
BLACK = (20, 20, 20)
GRAY = (160, 160, 160)
RED = (200, 40, 40)
GOLD = (220, 180, 60)
CARD_BACK = (30, 60, 140)

RANK_LABELS = {
    Rank.TWO: "2",
    Rank.THREE: "3",
    Rank.FOUR: "4",
    Rank.FIVE: "5",
    Rank.SIX: "6",
    Rank.SEVEN: "7",
    Rank.EIGHT: "8",
    Rank.NINE: "9",
    Rank.TEN: "10",
    Rank.JACK: "J",
    Rank.QUEEN: "Q",
    Rank.KING: "K",
    Rank.ACE: "A",
}

SUIT_SYMBOLS = {
    Suit.HEARTS: "♥",
    Suit.DIAMONDS: "♦",
    Suit.CLUBS: "♣",
    Suit.SPADES: "♠",
}


def suit_color(suit: Suit):
    if suit in (Suit.HEARTS, Suit.DIAMONDS):
        return RED
    return BLACK


def card_label(card: Card) -> str:
    """Krotka nazwa karty do tekstu, np. A♠"""
    return f"{RANK_LABELS[card.rank]}{SUIT_SYMBOLS[card.suit]}"


def draw_table(surface: pygame.Surface, width: int, height: int):
    # zielone tlo + elipsa stolu (prototyp, pozniej mozna podmienic grafika)
    surface.fill(TABLE_GREEN)
    # Rysowanie samej elipsy
    table_rect = pygame.Rect(width // 2 - 420, height // 2 - 180, 840, 360)
    pygame.draw.ellipse(surface, TABLE_DARK, table_rect)
    pygame.draw.ellipse(surface, GOLD, table_rect, 4)

BLUE = (40, 80, 200)

# Zmień całą funkcję draw_chips na tę wersję:
def draw_chips(surface, x, y, chip_colors):
    if not chip_colors:
        return
        
    for i, color in enumerate(chip_colors):
            # Dzielenie całkowite (//) dzieki temu wiemy ktory stos modyfikuejmy
            nr_stosu = i // 10 
            
            
            pozycja_w_stosie = i % 10 
            
            
            cx = x + (nr_stosu * 40)
            cy = y - (pozycja_w_stosie * 4)
            
            # Rysujemy żeton we właściwym miejscu
            pygame.draw.circle(surface, color, (cx, cy), 18)
            pygame.draw.circle(surface, WHITE, (cx, cy), 18, 2)
            pygame.draw.circle(surface, (20, 20, 20), (cx, cy), 10, 1)
def draw_card(
    surface: pygame.Surface,
    card: Card | None,
    x: int,
    y: int,
    face_up: bool = True,
    font=None,
    card_sprites: CardSprites | None = None,
):
    rect = pygame.Rect(x, y, CARD_WIDTH, CARD_HEIGHT)

    # grafiki z assets (jesli zaladowane)
    if card_sprites is not None:
        if not face_up or card is None:
            surface.blit(card_sprites.get_back(), rect.topleft)
        else:
            surface.blit(card_sprites.get(card), rect.topleft)
        return rect

    # fallback - proste prostokaty gdyby nie bylo grafik
    if not face_up or card is None:
        pygame.draw.rect(surface, CARD_BACK, rect, border_radius=6)
        pygame.draw.rect(surface, WHITE, rect, 2, border_radius=6)
        if font:
            mark = font.render("?", True, WHITE)
            surface.blit(mark, mark.get_rect(center=rect.center))
        return rect

    pygame.draw.rect(surface, WHITE, rect, border_radius=6)
    pygame.draw.rect(surface, BLACK, rect, 2, border_radius=6)

    if font:
        rank_text = font.render(RANK_LABELS[card.rank], True, suit_color(card.suit))
        suit_text = font.render(SUIT_SYMBOLS[card.suit], True, suit_color(card.suit))
        surface.blit(rank_text, (x + 8, y + 8))
        surface.blit(suit_text, (x + 8, y + CARD_HEIGHT - 28))
    return rect


def draw_card_row(
    surface: pygame.Surface,
    cards: list[Card],
    center_x: int,
    y: int,
    face_up: bool = True,
    font=None,
    gap: int = 12,
    card_sprites: CardSprites | None = None,
):
    """Rysuje rzad kart wycentrowany w poziomie."""
    if not cards:
        return
    total_width = len(cards) * CARD_WIDTH + (len(cards) - 1) * gap
    start_x = center_x - total_width // 2
    rects = []
    for index, card in enumerate(cards):
        x = start_x + index * (CARD_WIDTH + gap)
        rects.append(
            draw_card(surface, card, x, y, face_up=face_up, font=font, card_sprites=card_sprites)
        )
    return rects


def draw_deck(surface: pygame.Surface, x: int, y: int, card_sprites: CardSprites):
    # talia kart na stole
    surface.blit(card_sprites.get_deck(), (x, y))


def draw_text(surface, text, x, y, font, color=WHITE, center=False):
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(rendered, rect)
    return rect


def draw_button(surface, rect: pygame.Rect, text: str, font, enabled=True):
    color = (80, 80, 80) if enabled else (50, 50, 50)
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, WHITE if enabled else GRAY, rect, 2, border_radius=8)
    label = font.render(text, True, WHITE if enabled else GRAY)
    surface.blit(label, label.get_rect(center=rect.center))
    return rect
