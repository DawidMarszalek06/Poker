import random

import pygame
import os
from src.settings import ASSETS_DIR
from src.hand_evaluator import HandEvaluator
from src.players import Dealer, Player
from src.settings import DEFAULT_PLAYER_BALANCE, MIN_ANTE, SCREEN_HEIGHT, SCREEN_WIDTH, ASSETS_DIR
from src.table import Table
from src.ui.card_assets import CardSprites
from src.ui.renderer import (
    GRAY,
    GOLD,
    RED,
    BLUE,
    WHITE,
    card_label,
    draw_button,
    draw_card_row,
    draw_deck,
    draw_table,
    draw_text,
    draw_chips,
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
        self.bonus_bet = 0.0
        self.current_bet = 0.0
        self.message = ""
        self.reveal_dealer = False
        self.result_lines = []

        self.btn_post_ante = pygame.Rect(SCREEN_WIDTH // 2 - 100, 750, 200, 45)
        self.btn_fold = pygame.Rect(SCREEN_WIDTH // 2 - 220, 750, 200, 45)
        self.btn_play = pygame.Rect(SCREEN_WIDTH // 2 + 20, 750, 200, 45)
        self.btn_next = pygame.Rect(SCREEN_WIDTH // 2 - 100, 750, 200, 45)
       
        self.chips_base_x = SCREEN_WIDTH // 2 - 250
        self.chips_base_y = 580
        
        # Aktualna pozycja żetonów (na starcie taka sama jak bazowa)
        self.chips_x = self.chips_base_x
        self.chips_y = self.chips_base_y
        
        #zxmienne do rozciagania
        self.dragging_chips = False
        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.btn_chip_1 = pygame.Rect(SCREEN_WIDTH // 2 - 200, 690, 70, 45)
        self.btn_chip_5 = pygame.Rect(SCREEN_WIDTH // 2 - 120, 690, 70, 45)
        self.btn_chip_25 = pygame.Rect(SCREEN_WIDTH // 2 - 40, 690, 70, 45)
        self.btn_chip_100 = pygame.Rect(SCREEN_WIDTH // 2 + 40, 690, 70, 45)
        self.btn_clear_bet = pygame.Rect(SCREEN_WIDTH // 2 + 120, 690, 80, 45)
        
        self.bonus_bet = 0.0
        self.current_bet = 0.0

        pygame.mixer.init()
        self.volume = 0.2
        self.btn_vol_down = pygame.Rect(SCREEN_WIDTH - 140, 15, 35, 35)
        self.btn_vol_up = pygame.Rect(SCREEN_WIDTH - 35, 15, 35, 35)

        self.deal_sound = None
        sound_path = ASSETS_DIR / "deal.wav"
        if sound_path.exists():
            self.deal_sound = pygame.mixer.Sound(str(sound_path))
            self.deal_sound.set_volume(self.volume)

        self.chip_sound = None
        sound_path = ASSETS_DIR /"chip.wav"
        if sound_path.exists():
            self.chip_sound = pygame.mixer.Sound(str(sound_path))
            self.chip_sound.set_volume(self.volume)

        music_path = ASSETS_DIR / "music.mp3"
        if music_path.exists():
            pygame.mixer.music.load(str(music_path))
            pygame.mixer.music.set_volume(self.volume)
            pygame.mixer.music.play(-1) 

    def change_volume(self, amount):
        self.volume += amount
        self.volume = max(0.0, min(1.0, self.volume)) 
        
        pygame.mixer.music.set_volume(self.volume)
        if self.deal_sound:
            self.deal_sound.set_volume(self.volume)
        if self.chip_sound:
            self.chip_sound.set_volume(self.volume)

    def play_deal_sound(self):
        if self.deal_sound:
            self.deal_sound.play()

    def play_chip_sound(self):
        if self.chip_sound:
            self.chip_sound.play()

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
        #self.table.deal_initial_cards()
        self.phase = "ante"
        self.ante = 0.0
        self.bonus_bet = 0.0
        self.message = ""
        self.reveal_dealer = False
        self.result_lines = []

    def get_chips(self, amount):
        liczba_zetonow = int(amount // 10)
        return [BLUE] * liczba_zetonow
    
    def try_post_ante(self):
        player = self.table.players[0]

        if self.current_bet < MIN_ANTE:
            self.message = f"Minimalne Ante to {MIN_ANTE:.2f}!"
            return
        if self.current_bet * 3 > player.balance:
            self.message = f"Za malo srodkow! Max Ante: {player.balance / 3:.2f}"
            return
        
        self.ante = self.current_bet
        player.balance = round(player.balance -self.ante, 2)
                               
        self.current_bet = 0.0
        self.phase = "bonus"
        self.message = ""

    def try_post_bonus(self):
        player = self.table.players[0]
        max_bonus = round(player.balance - (self.ante * 2), 2)

        if self.current_bet > max_bonus:
            self.message = f"Za malo srodkow! Max Bonus: {max_bonus:.2f}"
            return

        self.bonus_bet = self.current_bet
        player.balance = round(player.balance - self.bonus_bet, 2)
        
        self.current_bet = 0.0

        self.table.deal_initial_cards()
        self.play_deal_sound()

        self.phase = "decision"
        self.message = ""

    def do_fold(self):
        player = self.table.players[0]
        dealer = self.table.dealer
        #Sprawdzenie bonusu
        bonus_score = HandEvaluator.evaluate_5_cards(player.hand + self.table.cards_on_the_table)
        bonus_multiplier = HandEvaluator.get_bonus_multiplier(bonus_score)
        bonus_msg = ""

        if self.bonus_bet > 0:
            if bonus_multiplier > 0:
                bonus_win = round(self.bonus_bet * (bonus_multiplier + 1), 2)
                player.balance = round(player.balance + bonus_win, 2)
                bonus_msg = f" (Bonus wygrany! +{bonus_win:.2f})"
            else:
                bonus_msg = f" (Bonus przegrany: -{self.bonus_bet:.2f})"

        self.message = f"Spasowales. Tracisz Ante ({self.ante:.2f})." + bonus_msg
        self.reveal_dealer = True
        self.reveal_dealer = True
        for _ in range(2):
            self.table.cards_on_the_table.append(self.table.deck.get_card())
        self.play_deal_sound()

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

        bonus_score = HandEvaluator.evaluate_5_cards(player.hand + self.table.cards_on_the_table)
        bonus_multiplier = HandEvaluator.get_bonus_multiplier(bonus_score)
        bonus_msg = ""

        if self.bonus_bet > 0:
            if bonus_multiplier > 0:
                bonus_win = round(self.bonus_bet * (bonus_multiplier + 1), 2)
                player.balance = round(player.balance + bonus_win, 2)
                bonus_msg = f", Bonus: +{bonus_win:.2f}"
            else:
                bonus_msg = f", Bonus: -{self.bonus_bet:.2f}"

        for _ in range(2):
            self.table.cards_on_the_table.append(self.table.deck.get_card())
        self.play_deal_sound()
        self.reveal_dealer = True
                                         
        my_score, _ = HandEvaluator.evaluate_7_cards(player.hand + self.table.cards_on_the_table)
        dealer_score, _ = HandEvaluator.evaluate_7_cards(dealer.hand + self.table.cards_on_the_table)
        my_hand = HandEvaluator.get_hand_string(my_score)
        dealer_hand = HandEvaluator.get_hand_string(dealer_score)

        if my_score > dealer_score:
            win = round((self.ante + call_cost) * 2, 2)
            player.balance = round(player.balance + win, 2)
            self.message = f"WYGRANA! +{win:.2f}{bonus_msg}"
        elif my_score < dealer_score:
            self.message = f"Przegrana - lepszy uklad krupiera{bonus_msg}"
        else:
            refund = round(self.ante + call_cost, 2)
            player.balance = round(player.balance + refund, 2)
            self.message = f"Remis - zwrot {refund:.2f}{bonus_msg}"

        self.result_lines = [f"Twoj uklad: {my_hand}", f"Uklad krupiera: {dealer_hand}"]

        if self.bonus_bet > 0 and bonus_multiplier > 0:
            bonus_hand_name = HandEvaluator.get_hand_string(bonus_score)
            self.result_lines.append(f"Trafiony Bonus: {bonus_hand_name} ({bonus_multiplier}:1)")

        self.phase = "result"

    def render_game(self):
        player = self.table.players[0]
        dealer = self.table.dealer

        draw_table(self.display, SCREEN_WIDTH, SCREEN_HEIGHT,)

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
        
            
        player_chips = self.get_chips(player.balance)
        draw_chips(self.display, self.chips_x, self.chips_y, player_chips)
        if self.ante > 0:
            pot_chips = self.get_chips(self.ante)
            draw_chips(self.display, SCREEN_WIDTH // 2 - 20, 480, pot_chips)
        # Tekst z saldem gracza
        draw_text(self.display, f"{player.nickname}  |  Saldo: {player.balance:.2f}", SCREEN_WIDTH // 2, 520, self.font_small, center=True)
        draw_text(self.display, f"{player.nickname}  |  Saldo: {player.balance:.2f}", SCREEN_WIDTH // 2, 520, self.font_small, center=True)
        draw_card_row(
            self.display, player.hand, SCREEN_WIDTH // 2, 560,
            face_up=True, card_sprites=self.card_sprites,

        )
        draw_text(self.display, "-", self.btn_vol_down.centerx, self.btn_vol_down.centery, self.font, GOLD, center=True)
        draw_text(self.display, f"{int(self.volume * 100)}%", SCREEN_WIDTH - 80, self.btn_vol_down.centery, self.font_small, WHITE, center=True)
        draw_text(self.display, "+", self.btn_vol_up.centerx, self.btn_vol_up.centery, self.font, GOLD, center=True)
        

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

        if self.phase in ("ante", "bonus"):
    
            draw_button(self.display, self.btn_chip_1, "+1", self.font_small)
            draw_button(self.display, self.btn_chip_5, "+5", self.font_small)
            draw_button(self.display, self.btn_chip_25, "+25", self.font_small)
            draw_button(self.display, self.btn_chip_100, "+100", self.font_small)
            draw_button(self.display, self.btn_clear_bet, "Cofnij", self.font_small)

            if self.phase == "ante":
                draw_text(
                    self.display,
                    f"Wybrane Ante (min {MIN_ANTE:.0f}, max {player.balance / 3:.2f}): {self.current_bet:.2f}",
                    SCREEN_WIDTH // 2,
                    650,
                    self.font_small,
                    center=True,
                )
                draw_button(self.display, self.btn_post_ante, "Zatwierdz Ante", self.font_small)
            
            elif self.phase == "bonus":
                max_bonus = round(player.balance - (self.ante * 2), 2)
                draw_text(
                    self.display,
                    f"Wybrany Bonus AA (max {max_bonus:.2f}): {self.current_bet:.2f}",
                    SCREEN_WIDTH // 2,
                    650,
                    self.font_small,
                    center=True,
                )
                draw_button(self.display, self.btn_post_ante, "Zatwierdz Bonus", self.font_small)

        elif self.phase == "decision":
            draw_button(self.display, self.btn_fold, "Fold", self.font_small)
            draw_button(self.display, self.btn_play, f"Graj ({self.ante * 2:.2f})", self.font_small)
            
        elif self.phase == "result":
            label = "Koniec" if player.balance <= 0 else "Kolejne rozdanie (G)"
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

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    if self.btn_vol_down.collidepoint(event.pos):
                        self.change_volume(-0.1)
                    elif self.btn_vol_up.collidepoint(event.pos):
                        self.change_volume(0.1)
                    
                    elif self.phase in ("ante", "bonus"):
                        if self.btn_chip_1.collidepoint(event.pos):
                            self.current_bet += 1.0
                            self.play_chip_sound()
                        elif self.btn_chip_5.collidepoint(event.pos):
                            self.current_bet += 5.0
                            self.play_chip_sound()
                        elif self.btn_chip_25.collidepoint(event.pos):
                            self.current_bet += 25.0
                            self.play_chip_sound()
                        elif self.btn_chip_100.collidepoint(event.pos):
                            self.current_bet += 100.0
                            self.play_chip_sound()
                        elif self.btn_clear_bet.collidepoint(event.pos):
                            self.current_bet = 0.0
                            self.play_chip_sound()
                            
                        elif self.btn_post_ante.collidepoint(event.pos):
                            if self.phase == "ante":
                                self.try_post_ante()
                            elif self.phase == "bonus":
                                self.try_post_bonus()

                    elif self.phase == "decision":
                        if self.btn_fold.collidepoint(event.pos):
                            self.do_fold()
                        elif self.btn_play.collidepoint(event.pos):
                            self.do_play()
                            
                    elif self.phase == "result":
                        if self.btn_next.collidepoint(event.pos):
                            if player.balance <= 0:
                                self.phase = "game_over"
                                self.message = "Brak srodkow. Koniec gry."
                            else:
                                self.start_new_hand()
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
                    chips_hitbox = pygame.Rect(self.chips_x - 30, self.chips_y - 80, 100, 100)
                    if chips_hitbox.collidepoint(event.pos):
                        self.dragging_chips = True
                        self.drag_offset_x = self.chips_x - event.pos[0]
                        self.drag_offset_y = self.chips_y - event.pos[1]

                # Puszczanie żetonów
                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.dragging_chips = False

                # Przeciąganie żetonów po ekranie z limitem odległości
                elif event.type == pygame.MOUSEMOTION:
                    if getattr(self, 'dragging_chips', False):
                        target_x = event.pos[0] + self.drag_offset_x
                        target_y = event.pos[1] + self.drag_offset_y
                        
                        limit = 60
                        self.chips_x = max(self.chips_base_x - limit, min(self.chips_base_x + limit, target_x))
                        self.chips_y = max(self.chips_base_y - limit, min(self.chips_base_y + limit, target_y))

            self.render_game()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()
