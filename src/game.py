import pygame

from src.players import Player, Dealer
from src.settings import (SCREEN_HEIGHT, SCREEN_WIDTH)
from src.cards import (Card, Rank, Suit)
from src.table import Table
from src.hand_evaluator import HandEvaluator

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
        self.table = table

    def run(self):
        print("--- ROZPOCZYNAMY CASINO HOLD'EM (Wersja Terminal) ---")
        me = self.table.players[0]
         
       
        while True:
            #  Reset stołu i tasowanie 
            self.table.prepare_new_deal()
            #  Rozdanie kart 
            self.table.deal_initial_cards()
            dealer = self.table.dealer # Pobieramy krupiera
            # Pobranie obiektu gracza 
            
            #pobeiranie salda gracza i pobranie zakładu początkowego (Ante)
            while True:
                ante_str = input(f"\nTwój balans to {me.balance}. Podaj stawkę (Ante): ")
                try:
                    ante = float(ante_str)
                    if ante <= 0:
                        print("Stawka musi być większa od zera!")
                    elif ante * 3 > me.balance:
                        # Tłumaczymy graczowi, dlaczego nie może postawić wszystkiego na start
                        max_ante = me.balance / 3
                        print(f"Za mało środków! Pamiętaj, że wpisowe 'Graj' kosztuje 2x Ante.")
                        print(f"Maksymalne możliwe Ante dla Twojego salda to: {max_ante:.2f}")
                    else:
                        break
                except ValueError:
                    print("Podaj poprawną liczbę!")
                    
            me.balance -= ante
            # Wyświetlenie informacji w konsoli
            print(f"\nGracz: {me.nickname} | Saldo: {me.balance}")
            print(f"Twoje karty: {me.hand}")
            
            print("\nKarty wspólne na stole (Flop):")
            print(f"{self.table.cards_on_the_table}")

            while True:
                decyzja = input("\nCo robisz? [F]old czy [G]raj? ").upper().strip()
                if decyzja in ['F', 'G']:
                        break
                print("Niepoprawny wybór! Wpisz 'F' lub 'G'.")
                
                # Logika po decyzji
            if decyzja == 'F':
                print(f"\nSpasowałeś. Przegrywasz zakład Ante ({ante}).")
                print(f"oto karty krupiera: {dealer.hand}")
                for _ in range(2):
                    self.table.cards_on_the_table.append(self.table.deck.get_card())
                print(f"oto karty wspólne po shuwdownie: {self.table.cards_on_the_table}")

                
                    
            elif decyzja == 'G':
                koszt_graj = ante * 2
                me.balance -= koszt_graj
                print(f"\nGramy dalej! Pobrano stawkę x2: {koszt_graj}. Pozostałe saldo: {me.balance}")
                    
                # Krupier dokłada 2 brakujące karty wspólne na stół (Turn i River)
                for _ in range(2):
                    self.table.cards_on_the_table.append(self.table.deck.get_card())
                print(f"\n--- SHOWDOWN ---")
                print(f"Ostateczne karty na stole: {self.table.cards_on_the_table}")
                print(f"Twoje karty: {me.hand}")
                print(f"Karty krupiera: {dealer.hand}")
                    
                # Łączymy 7 kart gracza i krupiera z kartami wspólnymi
                my_7_cards = me.hand + self.table.cards_on_the_table
                dealer_7_cards = dealer.hand + self.table.cards_on_the_table
                    
                # uzywamy fynkcji z hand_evaluator do oceny układów
                my_score, _ = HandEvaluator.evaluate_7_cards(my_7_cards)
                dealer_score, _ = HandEvaluator.evaluate_7_cards(dealer_7_cards)
                    
                # Zamieniamy punkty na ładny tekst
                my_hand_name = HandEvaluator.get_hand_string(my_score)
                dealer_hand_name = HandEvaluator.get_hand_string(dealer_score)
                    
                print(f"\nTwój najlepszy układ: {my_hand_name}")
                print(f"Układ krupiera: {dealer_hand_name}")
                    
                # Zwykłe porównanie kto wygral
                if my_score > dealer_score:
                    wygrana = (ante + koszt_graj) * 2
                    me.balance += wygrana
                    print(f"\n WYGRYWASZ! Zgarniasz {wygrana}! ")
                elif my_score < dealer_score:
                    print("\n Krupier ma lepszy układ. Przegrywasz. ")
                else:
                    zwrot = ante + koszt_graj
                    me.balance += zwrot
                    print("\n Remis Stawki wracają na Twoje konto. ")
            if me.balance <= 0:
                print("\n Twój balans jest pusty. Gra zakończona. ")
                return  
            else:
                kontynuuj = input("\nChcesz zagrać kolejne rozdanie? [T/N] ").upper().strip()
                if kontynuuj != 'T':
                    print("\nkoniec gry.")
                    return