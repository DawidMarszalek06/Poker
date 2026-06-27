import pygame

from src.hand_evaluator import HandEvaluator
from src.players import Dealer, Player
from src.settings import DEFAULT_PLAYER_BALANCE, MIN_ANTE, SCREEN_HEIGHT, SCREEN_WIDTH
from src.table import Table
from src.ui.card_assets import CardSprites
from src.ui.renderer import (
    GRAY,
    GOLD,
    RED,
    WHITE,
    card_label,
    draw_button,
    draw_card_row,
    draw_deck,
    draw_table,
    draw_text,
)


class Game:
    def __init__(self):
        pygame.init()
        self.display = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Poker - Casino Hold'em")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 32)
        self.font_card = pygame.font.SysFont(None, 36)
        self.card_sprites = CardSprites()

        self.table = None
        self.phase = "ante"
        self.ante = 0.0
        self.ante_input = ""
        self.message = ""
        self.reveal_dealer = False
        self.result_lines = []

        self.btn_post_ante = pygame.Rect(SCREEN_WIDTH // 2 - 100, 750, 200, 45)
        self.btn_fold = pygame.Rect(SCREEN_WIDTH // 2 - 220, 750, 200, 45)
        self.btn_play = pygame.Rect(SCREEN_WIDTH // 2 + 20, 750, 200, 45)
        self.btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 100, 750, 200, 45)

    def run_nickname_screen(self):
        nickname = ""

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and nickname.strip():
                        return nickname.strip()
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key == pygame.K_BACKSPACE:
                        nickname = nickname[:-1]
                    elif event.unicode.isprintable() and len(nickname) < 20:
                        nickname += event.unicode

            draw_table(self.display, SCREEN_WIDTH, SCREEN_HEIGHT)
            draw_text(self.display, "Casino Hold'em", SCREEN_WIDTH // 2, 280, self.font, center=True)
            draw_text(self.display, "Wpisz nick i nacisnij Enter", SCREEN_WIDTH // 2, 360, self.font_small, center=True)
            draw_text(self.display, nickname + "|", SCREEN_WIDTH // 2, 420, self.font, center=True)
            draw_text(self.display, "Esc = wyjscie", SCREEN_WIDTH // 2, 500, self.font_small, GRAY, center=True)
            pygame.display.flip()
            self.clock.tick(60)

    def start_new_hand(self):
        self.table.prepare_new_deal()
        self.table.deal_initial_cards()
        self.phase = "ante"
        self.ante = 0.0
        self.ante_input = ""
        self.message = ""
        self.reveal_dealer = False
        self.result_lines = []

    def try_post_ante(self):
        player = self.table.players[0]
        try:
            value = round(float(self.ante_input.replace(",", ".")), 2)
        except ValueError:
            self.message = "Podaj poprawna liczbe!"
            return

        if value < MIN_ANTE:
            self.message = f"Minimalne Ante to {MIN_ANTE:.2f}!"
            return
        if value * 3 > player.balance:
            self.message = f"Za malo srodkow! Max Ante: {player.balance / 3:.2f}"
            return

        self.ante = value
        player.balance = round(player.balance - value, 2)
        self.phase = "decision"
        self.message = ""

    def do_fold(self):
        dealer = self.table.dealer

        self.message = f"Spasowales. Tracisz Ante ({self.ante:.2f})."
        self.reveal_dealer = True
        for _ in range(2):
            self.table.cards_on_the_table.append(self.table.deck.get_card())
        self.result_lines = [
            "Fold - przegrana",
            "Karty krupiera: " + ", ".join(card_label(c) for c in dealer.hand),
        ]
        self.phase = "result"

    def do_play(self):
        player = self.table.players[0]
        dealer = self.table.dealer
        call_cost = self.ante * 2
        player.balance = round(player.balance - call_cost, 2)

        for _ in range(2):
            self.table.cards_on_the_table.append(self.table.deck.get_card())

        self.reveal_dealer = True
        my_score, _ = HandEvaluator.evaluate_7_cards(player.hand + self.table.cards_on_the_table)
        dealer_score, _ = HandEvaluator.evaluate_7_cards(dealer.hand + self.table.cards_on_the_table)
        my_hand = HandEvaluator.get_hand_string(my_score)
        dealer_hand = HandEvaluator.get_hand_string(dealer_score)

        if my_score > dealer_score:
            win = round((self.ante + call_cost) * 2, 2)
            player.balance = round(player.balance + win, 2)
            self.message = f"WYGRANA! +{win:.2f}"
        elif my_score < dealer_score:
            self.message = "Przegrana - lepszy uklad krupiera"
        else:
            refund = round(self.ante + call_cost, 2)
            player.balance = round(player.balance + refund, 2)
            self.message = f"Remis - zwrot {refund:.2f}"

        self.result_lines = [f"Twoj uklad: {my_hand}", f"Uklad krupiera: {dealer_hand}"]
        self.phase = "result"

    def render_game(self):
        player = self.table.players[0]
        dealer = self.table.dealer

        draw_table(self.display, SCREEN_WIDTH, SCREEN_HEIGHT)

        draw_text(self.display, "Krupier", SCREEN_WIDTH // 2, 50, self.font_small, center=True)
        draw_card_row(
            self.display, dealer.hand, SCREEN_WIDTH // 2, 90,
            face_up=self.reveal_dealer, card_sprites=self.card_sprites,
        )

        draw_text(self.display, "Karty wspolne", SCREEN_WIDTH // 2, 300, self.font_small, GRAY, center=True)
        draw_card_row(
            self.display, self.table.cards_on_the_table, SCREEN_WIDTH // 2, 330,
            face_up=True, card_sprites=self.card_sprites,
        )

        deck_x = SCREEN_WIDTH // 2 + 360
        deck_y = SCREEN_HEIGHT // 2 - CardSprites.DECK_H // 2
        draw_deck(self.display, deck_x, deck_y, self.card_sprites)

        draw_text(self.display, f"{player.nickname}  |  Saldo: {player.balance:.2f}", SCREEN_WIDTH // 2, 520, self.font_small, center=True)
        draw_card_row(
            self.display, player.hand, SCREEN_WIDTH // 2, 560,
            face_up=True, card_sprites=self.card_sprites,
        )

        if self.message and self.phase in ("ante", "game_over"):
            color = GOLD if "WYGRANA" in self.message else WHITE
            if "Przegrana" in self.message or "Spasowales" in self.message or "Minimalne" in self.message:
                color = RED
            draw_text(self.display, self.message, SCREEN_WIDTH // 2, 665, self.font_small, color, center=True)

        if self.phase == "decision":
            draw_text(
                self.display,
                f"Ante: {self.ante:.2f}  |  Call: {self.ante * 2:.2f}",
                SCREEN_WIDTH // 2,
                690,
                self.font_small,
                center=True,
            )

        if self.phase == "result":
            y = 678
            if self.message:
                color = GOLD if "WYGRANA" in self.message else WHITE
                if "Przegrana" in self.message or "Spasowales" in self.message:
                    color = RED
                draw_text(self.display, self.message, SCREEN_WIDTH // 2, y, self.font_small, color, center=True)
                y += 30
            for line in self.result_lines:
                draw_text(self.display, line, SCREEN_WIDTH // 2, y, self.font_small, GRAY, center=True)
                y += 26

        if self.phase == "ante":
            draw_text(
                self.display,
                f"Ante min {MIN_ANTE:.0f}, max {player.balance / 3:.2f}: {self.ante_input}|",
                SCREEN_WIDTH // 2,
                690,
                self.font_small,
                center=True,
            )
            draw_button(self.display, self.btn_post_ante, "Postaw Ante", self.font_small)
        elif self.phase == "decision":
            draw_button(self.display, self.btn_fold, "Fold", self.font_small)
            draw_button(self.display, self.btn_play, f"Graj ({self.ante * 2:.2f})", self.font_small)
        elif self.phase == "result":
            label = "Koniec" if player.balance <= 0 else "Kolejne rozdanie"
            draw_button(self.display, self.btn_next, label, self.font_small)
        elif self.phase == "game_over":
            draw_text(self.display, "Koniec gry - zamknij okno", SCREEN_WIDTH // 2, 750, self.font_small, center=True)

    def run(self):
        nickname = self.run_nickname_screen()
        if not nickname:
            pygame.quit()
            return

        player = Player(nickname, DEFAULT_PLAYER_BALANCE)
        dealer = Dealer()
        self.table = Table([player, dealer])
        self.start_new_hand()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN and self.phase == "ante":
                    if event.key == pygame.K_RETURN:
                        self.try_post_ante()
                    elif event.key == pygame.K_BACKSPACE:
                        self.ante_input = self.ante_input[:-1]
                    elif event.unicode.isprintable() and len(self.ante_input) < 8:
                        if event.unicode.isdigit():
                            text = self.ante_input.replace(",", ".")
                            if "." in text and len(text.split(".")[1]) >= 2:
                                continue
                            self.ante_input += event.unicode
                        elif event.unicode in ".," and self.ante_input and "." not in self.ante_input and "," not in self.ante_input:
                            self.ante_input += "."

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.phase == "ante" and self.btn_post_ante.collidepoint(event.pos):
                        self.try_post_ante()
                    elif self.phase == "decision" and self.btn_fold.collidepoint(event.pos):
                        self.do_fold()
                    elif self.phase == "decision" and self.btn_play.collidepoint(event.pos):
                        self.do_play()
                    elif self.phase == "result" and self.btn_next.collidepoint(event.pos):
                        if player.balance <= 0:
                            self.phase = "game_over"
                            self.message = "Brak srodkow. Koniec gry."
                        else:
                            self.start_new_hand()

            self.render_game()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
