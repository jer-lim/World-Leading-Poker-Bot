from pypokerengine.players import BasePokerPlayer
import pprint
import collections
from multiprocessing import Process, Queue
from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator

# Factors have an associated weight and calculate method to calculate
# corresponding value using hole cards and community cards
class Factor:
    def __init__(self, weight):
        self.weight = weight

    # Used to get numerical values for T,J,Q,K,A cards
    def getNumbers(self, cards):
        cardNumbers = []
        for card in cards:
            if card[1:] == 'T':
                cardNumbers += [10]
            elif card[1:] == 'J':
                cardNumbers += [11]
            elif card[1:] == 'Q':
                cardNumbers += [12]
            elif card[1:] == 'K':
                cardNumbers += [13]
            elif card[1:] == 'A':
                cardNumbers += [14]
            else:
                cardNumbers += [card[1:]]
        return cardNumbers

    # Used to get suites of cards
    def getSuites(self, cards):
        cardSuites = []
        for card in cards:
            cardSuites += card[0]
        return cardSuites

    # Returns the number of same value cards formed, as well as the value of the combination, excluding combinations
    # formed only from community cards
    def getCombinations(self, hole_cards, community_cards):
        hole_numbers = getNumbers(hole_cards)
        community_numbers = getNumbers(community_cards)
        if (hole_numbers[0] == hole_numbers[1]):
            
    
    # Used to get number of pairs and the pairs formed, excluding pairs formed
    # from 2 community cards and triples
    def getPairs(self, hole_cards, community_cards):
        hole_numbers = getNumbers(hole_cards)
        community_numbers = getNumbers(community_cards)
        number_of_pairs = 0
        pairs = []

        if (hole_numbers[0] == hole_numbers[1]) and (hole_numbers[0] not in community_numbers):
            number_of_pairs += 1
            pairs += [hole_numbers[0]]
            
        else:
            for number in hole_numbers:
                if community_numbers.count(number) == 1:
                    number_of_pairs += 1
                    pairs += [number]
        
        return [number_of_pairs, pairs]

    # Used to check for straight outs, excluding the event where straight comes
    # from all 5 community cards
    def getStraightOuts(self, hole_cards, community_cards):
        hole_numbers = getNumbers(hole_cards)
        community_numbers = getNumbers(community_cards)
        all_numbers = hole_numbers + community_numbers
        number_of_aces = all_numbers.count(14)
        all_numbers += ([1]*number_of_aces)
        all_numbers.sort()
        current_run = all_numbers[0]
        outs = []
        has_straight_outs = False
        for i in range(len(all_numbers) - 1):
            if all_numbers[i] + 1 == all_numbers[i+1]:
                current_run += all_numbers[i+1]
            else:
                current_run = [all_numbers[i+1]]
        if (len(current_run) == 4) and (set(current_run) != set(community_cards)):
            has_sraight_outs = True
            if current_run[0] != 2:
                for suite in ['C','D','H','S']:
                    outs += [str(current_run[0]-1) + suite]
            elif current_run[0] == 2:
                for suite in ['C','D','H','S']:
                    outs += [str(14) + suite]
            if current_run[-1] != 14:
                for suite in ['C','D','H','S']:
                    outs += [str(current_run[-1]+1) + suite]
            
        return [has_straight_outs, outs]

    # Used to check for flush outs, excluding the event where flush comes from
    # all 5 community cards
    def getFlushOuts(self, hole_cards, community_cards):
        hole_suites = getSuites(hole_cards)
        community_suites = getSuites(community_cards)
        all_suites = hole_suites + community_suites
        all_cards = community_cards + hole_cards
        has_flush_outs = false
        outs = []
        for suite in ['C','D','H','S']:
            if all_suites.count(suite) == 4:
                has_flush_outs = True
                for number in [2,3,4,5,6,7,8,9,'T','J','Q','K']:
                    if number == 'T' and ((str(number)+suite) not in all_cards):
                        outs += [str(number)+suite]
                    elif number == 'J' and ((str(number)+suite) not in all_cards):
                        outs += ['11'+suite]
                    elif number == 'Q' and ((str(number)+suite) not in all_cards):
                        outs += ['12'+suite]
                    elif number == 'K' and ((str(number)+suite) not in all_cards):
                        outs += ['13'+suite]
                    elif number == 'A' and ((str(number)+suite) not in all_cards):
                        outs += ['14'+suite]
                    elif (str(number)+suite) not in all_cards:
                        outs += [str(number)+suite]
                        
                break
        return [has_flush_outs, outs]
        
    # Note: To be overridden by subclasses of Factor
    def calculate(self, hole_cards, community_cards):
        print("calculate not overridden")

# We only consider high cards when we have no combination, excluding combinations
# from only community cards. Return the highest card in hole cards that is also
# higher than all community cards, else return 0
class HighCard(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        pair_part = getPairs(hole_cards, community_cards)
        straight_part = getStraightOuts(hole_cards, community_cards)
        flush_part = getFlushPart(hole_cards, community_cards)
        max_hole_card = max(getNumbers(hole_cards))
        if (pair_part[0] == 0) and (not straight_part[0]) and (not flush_part[0]) and (max_hole_card > max(getNumbers(community_cards))):
            return max_hole_card
        else:
            return 0
            
        
# We only consider single pairs and exclude other combinations like triples
# or double pairs that would also contain pairs. We also exclude pairs formed
# by 2 community cards

class StrengthOfSinglePair(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        pairs = getPairs(hole_cards, community_cards)
        if pairs[0] == 1:
            return pairs[1][0]
        else:
            return 0

# We only consider single pairs still formable from community cards against
# our single pair. If we do not have a single pair or there is already a pair
# among the community cards, we exclude this factor (return 0).
class NumberOfHigherFormableSinglePairs(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        pairs = getPairs(hole_cards, community_cards)
        community_numbers = getNumbers(community_cards)
        numberOfHigherFormableSinglePairs = 0
        if (pairs[0] == 1) and (len(community_numbers) == len(set(community_numbers))):
            for number in community_numbers:
                if number > pairs[1][0]:
                    numberOfHigherFormableSinglePairs += 1
        return numberOfHigherFormableSinglePairs
        
# Returns number of single cards that will form either a straight or flush
class Outs(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        straight_part = getStraightOuts(hole_cards, community_cards)
        flush_part = getFlushOuts(hole_cards, community_cards)
        outs = []
        if straight_part[0] and flush_part[0]:
            return len(list(set(straight_part[1] + flush_part[1])))
        else:
            return 0

# Returns the strength of a double pair as the sum of the 2 pairs, or 0
# if no double pair is formed
class StrengthOfTwoPairs(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        pairs = getPairs(hole_cards, community_cards)
        if pairs[0] == 2:
            return pairs[1][0] + pairs[1][1]
        else:
            return 0

# Returns the strength of a triple or a 0 if no triple is formed
class StrengthOfTriple(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        hole_numbers = getNumbers(hole_cards)
        community_numbers = getNumbers(community_cards)
        if (hole_numbers[0] == hole_numbers[1]) and (community_numbers.count(hole_numbers) == 1):
            return hole_numbers[0]
        else:
            for number in hole_numbers:
                if community_numbers.count(number) == 2:
                    return number
        return 0

# Returns the number of higher triples that could possibly be formed compared
# to our triple, returns 0 if we do not have a triple.
class NumberOfHigherFormableTriples(Factor):
    def __init__(self, weight):
        super(Factor, self).__init__(weight)

    def calculate(self, hole_cards, community_cards):
        if 
