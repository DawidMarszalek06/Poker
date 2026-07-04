import itertools
from collections import Counter

class HandEvaluator:

    HAND_NAMES = {
        10: "Poker Królewski",
        9: "Poker",
        8: "Kareta",
        7: "Full",
        6: "Kolor",
        5: "Strit",
        4: "Trójka",
        3: "Dwie Pary",
        2: "Para",
        1: "Wysoka Karta"
    }

    CARD_SYMBOLS = {
        14: "A",
        13: "K",
        12: "Q", 
        11: "J"
    }

    BONUS_PAYOUTS = {
        10: 100,
        9: 50,
        8: 40,
        7: 30,
        6: 20,
        5: 7,
        4: 7,
        3: 7,
    }

    @staticmethod
    def evaluate_7_cards(cards): #Sprawdzamy wszystkie kombinacje złożone z 7 kart(2 gracza + 5 wspólnych)
        best_score = (-1,0)
        best_hand = None

        for hand in itertools.combinations(cards,5):
            score = HandEvaluator.evaluate_5_cards(hand)

            if score > best_score:
                best_score = score
                best_hand = hand

        return best_score, best_hand

    @staticmethod
    def evaluate_5_cards(hand): #Sprawdzenie każdej z 21 kombinacji

        sorted_cards = sorted(hand, key=lambda c: c.rank.value, reverse=True)

        ranks = [c.rank.value for c in sorted_cards]
        suits = [c.suit.name for c in sorted_cards]

        is_flush = len(set(suits)) == 1 #Sprawdzenie koloru

        is_straight = False
        straight_high = ranks[0]

        if len(set(ranks)) == 5 and (ranks[0] - ranks[4] == 4): #Sprawdzenie strita
            is_straight = True
            straight_high = ranks[0]

        elif ranks == [14,5,4,3,2]: #Wyjątek dla strita As-5
            is_straight = True
            straight_high = 5

        rank_counts = Counter(ranks) #Sprawdzenie par, trójek, karet

        counts = sorted(rank_counts.values(), reverse=True)

        ranks_by_count = [r for r,_ in sorted(rank_counts.items(), key = lambda x:(x[1],x[0]), reverse=True)]

        #Ocena układów:

        if is_flush and is_straight and straight_high == 14: #Poker Królewski
            return (10,[])

        if is_flush and is_straight: #Poker
            return (9, [straight_high])

        if counts == [4,1]: #Kareta
            return(8,ranks_by_count)

        if counts == [3,2]: #Ful
            return (7, ranks_by_count)

        if is_flush: #Kolor
            return (6, ranks)

        if is_straight: #Stirt
            return (5,[straight_high])

        if counts == [3,1,1]: #Trójka
            return (4, ranks_by_count)

        if counts == [2,2,1]: #Dwie pary
            return (3, ranks_by_count)

        if counts == [2,1,1,1]: #Para
            return (2, ranks_by_count)

        return (1, ranks) #High card

    @staticmethod
    def get_hand_string(score): #Pozyskiwanie "ładnej" nazwy układu

        hand_type = score[0]
        kickers = score[1]

        base_name = HandEvaluator.HAND_NAMES.get(hand_type, "Nieznany układ")

        def to_symbol(val):
            return str(HandEvaluator.CARD_SYMBOLS.get(val, val))

        if hand_type == 10:
            return base_name
            
        elif hand_type in (9, 5):
            high_card = kickers[0]
            if high_card == 5:
                return f"{base_name} A-5"
            low_card = high_card - 4
            return f"{base_name} {to_symbol(low_card)}-{to_symbol(high_card)}"
            
        elif hand_type in (8, 7, 4, 2): 
            main_figure = kickers[0]
            return f"{base_name} {to_symbol(main_figure)}"
            
        elif hand_type == 3:  
            para1 = kickers[0]
            para2 = kickers[1]
            return f"{base_name} {to_symbol(para1)} i {to_symbol(para2)}"
            
        else: 
            return f"{base_name} {to_symbol(kickers[0])}"
        
    @staticmethod
    def get_bonus_multiplier(score):
        hand_type = score[0]
        kickers = score[1]

        if hand_type in HandEvaluator.BONUS_PAYOUTS:
            return HandEvaluator.BONUS_PAYOUTS[hand_type]

        if hand_type == 2:
            if kickers[0] == 14:
                return 7
        return 0
   