from collections import defaultdict
import HandEvaluator
"""
Deprecated:
Problem: Difficult to distinguish between a pair in the community and a pair
among all the hole cards
"""
class SimplifiedCardUtils:
    @classmethod
    def generatePermutationsOfCards(self, hole_cards, community_cards):
        hole_cards = hole_cards
        community_cards = community_cards


        lower_bound = 0
        if HandEvaluator.__is_straightflash(cards):
            lower_bound = 8
        elif HandEvaluator.__is_fourcard(cards):
            lower_bound = 7
        elif HandEvaluator.__is_fullhouse(cards):
            lower_bound = 6
        elif HandEvaluator.__is_flash(cards):
            lower_bound = 5
        elif HandEvaluator.__is_straight(cards):
            lower_bound = 4
        elif HandEvaluator.__is_threecard(cards):
            lower_bound = 3
        elif HandEvaluator.__is_twopair(cards):
            lower_bound = 2
        elif HandEvaluator.__is_onepair(cards):
            lower_bound = 1


        count = defaultdict(int)
        for card in hole_cards:
            count[card.rank] += 1
        cards = hole_cards + community_cards

    def generate_extra_card_onepair(self, cards, card_count):
        """Precondition: all values are distinct"""
        cards =
