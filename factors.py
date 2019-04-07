from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

# Factors Actively Selectively Taken
class FASTHeuristic:
        def __init__(self, weights):
                # Array of weights
                # 0 - High Card [highCard]
                # 1 - Pair Strength [singlePairStrength]
                # 2 - Higher Pairs [numberOfHigherFormableSinglePairs]
                # 3 - 2-Pair Strength [doublePairStrength]
                #   - Triple or Higher [haveTripleOrBetter] (Always infinite EV, #yolo)
                self.weights = weights
                self.max_values = [13, 13, 0, 15]
                maximum = 0
                for i in range(0,4):
                        maximum += self.max_values[i]*self.weights[i]
                self.maximum = maximum
                

        def getEV(self, hole_card, community_card):
                factors = [0] * 4

                cards = DecomposedCards(hole_card, community_card)
                # If have FH or better, #yolo
                if cards.haveTripleOrBetter() > 0:
                        return 1

                # Preset strengths to make strong hands stronger than weaker hands
                factors[3] = self.max_values[3]
                factors[1] = self.max_values[1]
                factors[0] = self.max_values[0]

                # Calculate 2 pairs
                factors[3] = cards.doublePairStrength()
                if factors[3] > 0:
                        return self.__linearCombination(factors)

                # Calculate pairs
                factors[1] = cards.singlePairStrength()
                factors[2] = -cards.numberOfHigherFormableSinglePairs()
                if factors[1] > 0:
                        return self.__linearCombination(factors)

                # High card
                factors[0] = cards.highCard()
                return self.__linearCombination(factors)

        def __linearCombination(self, factors):
                total = 0
                for i in range(0, 4):
                        total += self.weights[i] * factors[i]
                return max(0, total/self.maximum)


class DecomposedCards:
        def __init__(self, hole_card, community_card):
                self.hole_card = hole_card
                self.community_card = community_card

                # Count suits
                self.num_suits = {}
                self.suit_high = {}
                self.hole_card_num_suits = {}
                self.hole_card_suit_high = {}
                self.comm_card_num_suits = {}
                self.comm_card_suit_high = {}
                for suit_num in Card.SUIT_MAP.keys():
                        self.num_suits[suit_num] = 0
                        self.suit_high[suit_num] = 0
                        self.hole_card_num_suits[suit_num] = 0
                        self.hole_card_suit_high[suit_num] = 0
                        self.comm_card_num_suits[suit_num] = 0
                        self.comm_card_suit_high[suit_num] = 0

                for card in hole_card:
                        self.num_suits[card.suit] += 1
                        self.hole_card_num_suits[card.suit] += 1
                        if card.rank > self.suit_high[card.suit]:
                                self.suit_high[card.suit] = card.rank
                        if card.rank > self.hole_card_suit_high[card.suit]:
                                self.hole_card_suit_high[card.suit] = card.rank

                for card in community_card:
                        self.num_suits[card.suit] += 1
                        self.comm_card_num_suits[card.suit] += 1
                        if card.rank > self.suit_high[card.suit]:
                                self.suit_high[card.suit] = card.rank
                        if card.rank > self.comm_card_suit_high[card.suit]:
                                self.comm_card_suit_high[card.suit] = card.rank

                # Count ranks
                self.num_rank = {}
                self.hole_card_num_rank = {}
                self.comm_card_num_rank = {}
                self.hole_card_highest_rank = 0
                self.comm_card_highest_rank = 0
                for rank in range(1, 15):
                        self.num_rank[rank] = 0
                        self.hole_card_num_rank[rank] = 0
                        self.comm_card_num_rank[rank] = 0

                for card in hole_card:
                        self.num_rank[card.rank] += 1
                        self.hole_card_num_rank[card.rank] += 1
                        if card.rank == 14:
                                self.num_rank[1] += 1
                                self.hole_card_num_rank[1] += 1
                        if card.rank > self.hole_card_highest_rank:
                                self.hole_card_highest_rank = card.rank

                for card in community_card:
                        self.num_rank[card.rank] += 1
                        self.comm_card_num_rank[card.rank] += 1
                        if card.rank == 14:
                                self.num_rank[1] += 1
                                self.comm_card_num_rank[1] += 1
                        if card.rank > self.comm_card_highest_rank:
                                self.comm_card_highest_rank = card.rank

        def highCard(self):
                if self.hole_card_highest_rank > self.comm_card_highest_rank:
                        return self.hole_card_highest_rank
                return 0

        def singlePairStrength(self):
                num_pairs = 0
                pair_strength = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] == 2:
                                num_pairs += 1
                                pair_strength = rank
                comm_card_has_pair = False
                for rank in self.comm_card_num_rank:
                        if self.comm_card_num_rank[rank] == 2:
                                comm_card_has_pair = True
                if num_pairs == 1 and not comm_card_has_pair:
                        return pair_strength
                return 0

        def numberOfHigherFormableSinglePairs(self):
                mySinglePairStrength = self.singlePairStrength()
                num_higher_formable_pairs = 0
                if mySinglePairStrength > 0:
                        for rank in self.comm_card_num_rank:
                                if rank > mySinglePairStrength and self.comm_card_num_rank[rank] > 0:
                                        num_higher_formable_pairs += 1
                return num_higher_formable_pairs
        
        def doublePairStrength(self):
                num_pairs = 0
                pair_strength = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] == 2:
                                num_pairs += 1
                                pair_strength = rank
                comm_card_has_pair = False
                for rank in self.comm_card_num_rank:
                        if self.comm_card_num_rank[rank] == 2:
                                comm_card_has_pair = True
                if num_pairs == 2 and not comm_card_has_pair:
                        return pair_strength
                return 0                

        # Checks if we have a triple, excluding the case where all 3 cards come
        # from the community cards. This includes Triples, Four-Of-A-Kinds, and
        # Full houses
        def hasATriple(self):
                for rank in self.num_rank:
                        if self.num_rank[rank] >= 3 and not self.comm_card_num_rank[rank] >= 3:
                                return True
                return False

        # Checks if we have a straight inclusive of the case where all 5 cards
        # come from the community cards because of the negligible chance
        def hasStraight(self):
                # Look for chain of 5
                chain = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] == 0:
                                chain = 0
                        else:
                                chain += 1
                        if chain == 5:
                                return True
                return False
        
        # Checks if we have a flush, inclusive of the case where all 5 cards
        # come from the community cards because of the negligible chance
        def hasFlush(self):
                for suit in self.num_suits:
                        if self.num_suits[suit] >= 5:
                                return True
                return 0

        def haveTripleOrBetter(self):
                return self.hasATriple() or self.hasStraight() or self.hasFlush()
                
                                
########## TEST ##########
##
##hole_card_list = ['C2', 'D4']
##community_card_list = ['D4', 'C5', 'CQ', 'CA', 'HK']
##hole_card = gen_cards(hole_card_list)
##community_card = gen_cards(community_card_list)                                                                
##cards = DecomposedCards(hole_card, community_card)
##print("Hole cards: " + str(hole_card_list))
##print("Community cards: " + str(community_card_list))
##print()
##print("0 highCard: " + str(cards.highCard()))
##print("1 singlePairStrength: " + str(cards.singlePairStrength()))
##print("2 numberOfHigherFormableSinglePairs: " + str(cards.numberOfHigherFormableSinglePairs()))
##print("3 doublePairStrength: " + str(cards.doublePairStrength()))
##print("haveTripleOfBetter: " + str(cards.haveTripleOrBetter()))
##print()
##fast = FASTHeuristic([1,1,1,1])
##print("FAST: " + str(fast.getEV(hole_card, community_card)))
##
##
