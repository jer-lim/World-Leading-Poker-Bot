from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

# Factors Actively Selectively Taken
class FASTHeuristic:
        def __init__(self, weights):
                # Array of weights
                # 0 - High Card [highCard]
                # 1 - Pair Strength [singlePairStrength]
                # 2 - Higher Pairs [numberOfHigherFormableSinglePairs]
                # 3 - Outs [numberOfOuts]
                # 4 - 2-Pair Strength [doublePairStrength]
                # 5 - Higher 2-Pairs [numberOfFormableDoublePairs]
                # 6 - Triple Strength [tripleStrength]
                # 7 - Higher Triple [numberOfHigherFormableTriples]
                # 8 - Straight Strength [straightStrength]
                # 9 - Higher Straights [possibleStraights]
                # 10 - Flush Strength [flushStrength]
                # 11 - Higher Flushes [possibleFlushes]
                #    - Full House or Higher [haveFullHouseOrBetter] (Always infinite EV, #yolo)
                self.weights = weights
                # self.max_values = [13, 13, 5, 15, 13, 10, 13, 5, 13, 12, 13, 2]
                self.max_values = [13, 13, 0, 15, 13, 0, 13, 0, 13, 0, 13, 0]
                maximum = 0
                for i in range(0,12):
                        maximum += self.max_values[i]*self.weights[i]
                self.maximum = maximum
                

        def getEV(self, hole_card, community_card):
                factors = [0] * 12

                cards = DecomposedCards(hole_card, community_card)
                # If have FH or better, #yolo
                if cards.haveFullHouseOrBetter() > 0:
                        return 1

                # Calculate flush [10, 11]
                factors[10] = cards.flushStrength()
                factors[11] = -cards.possibleFlushes()
                if factors[10] > 0:
                        return self.__linearCombination(factors)

                # Calculate straights
                factors[8] = cards.straightStrength()
                factors[9] = -cards.possibleStraights()
                if factors[8] > 0:
                        return self.__linearCombination(factors)

                # Calculate triples and outs
                factors[6] = cards.tripleStrength()
                factors[7] = -cards.numberOfHigherFormableTriples()
                factors[3] = cards.numberOfOuts()
                if factors[6] > 0:
                        return self.__linearCombination(factors)

                # Calculate 2 pairs
                factors[4] = cards.doublePairStrength()
                factors[5] = -cards.numberOfHigherFormableDoublePairs()
                if factors[4] > 0:
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
                # print(factors)
                total = 0
                for i in range(0, 12):
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
        
        def numberOfOuts(self):
                outs = 0

                # Calculate straight outs
                pattern = 0
                for rank in self.num_rank:
                        if pattern >= 16:
                                pattern -= 16
                        pattern = pattern << 1
                        if self.num_rank[rank] >= 1:
                                pattern += 1
                        current_out = None
                        # 11110
                        if pattern == 30 and not (self.comm_card_num_rank[rank-1] > 0 and self.comm_card_num_rank[rank-2] > 0 and self.comm_card_num_rank[rank-3] > 0 and self.comm_card_num_rank[rank-4] > 0):
                                current_out = rank
                        # 01111
                        elif pattern == 15 and rank >= 5 and not (self.comm_card_num_rank[rank] > 0 and self.comm_card_num_rank[rank-1] > 0 and self.comm_card_num_rank[rank-2] > 0 and self.comm_card_num_rank[rank-3] > 0):
                                current_out = rank - 4
                        # 10111
                        elif pattern == 23 and not (self.comm_card_num_rank[rank] > 0 and self.comm_card_num_rank[rank-1] > 0 and self.comm_card_num_rank[rank-2] > 0 and self.comm_card_num_rank[rank-4] > 0):
                                current_out = rank - 3
                        # 11011
                        elif pattern == 27 and not (self.comm_card_num_rank[rank] > 0 and self.comm_card_num_rank[rank-1] > 0 and self.comm_card_num_rank[rank-3] > 0 and self.comm_card_num_rank[rank-4] > 0):
                                current_out = rank - 2
                        # 11101
                        elif pattern == 29 and not (self.comm_card_num_rank[rank] > 0 and self.comm_card_num_rank[rank-2] > 0 and self.comm_card_num_rank[rank-3] > 0 and self.comm_card_num_rank[rank-4] > 0):
                                current_out = rank - 1
                        if current_out != None:
                                outs += 4
        
                # Calculate flush outs
                overlap = int(outs / 4)
                for suit in self.num_suits:
                        if self.num_suits[suit] == 4 and self.comm_card_num_suits[suit] != 4:
                                outs += 9 - overlap
                return outs

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

        def numberOfHigherFormableDoublePairs(self):
                if self.doublePairStrength() != 0:
                        highestPair = 0
                        for rank in range(14,0,-1):
                                if self.num_rank[rank] == 2:
                                        highestPair = rank
                                        break
                        numberOfHigherCards = 0
                        for rank in self.comm_card_num_rank:
                                if rank > highestPair and self.comm_card_num_rank[rank] > 0:
                                        numberOfHigherCards += 1
                        return int((numberOfHigherCards / 2) * (9 - numberOfHigherCards))
                return 0
                                        

        def tripleStrength(self):
                triple_strength = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] == 3 and self.comm_card_num_rank[rank] != 3:
                                triple_strength = rank
                return triple_strength

        def numberOfHigherFormableTriples(self):
                myTripleStrength = self.tripleStrength()
                num_higher_formable_triples = 0
                if myTripleStrength > 0:
                        for rank in self.comm_card_num_rank:
                                if rank > myTripleStrength and self.comm_card_num_rank[rank] > 0:
                                        num_higher_formable_triples += 1
                return num_higher_formable_triples

        # Highest rank in a straight
        def straightStrength(self):
                # Look for chain of 5
                highest_rank = 0
                chain = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] == 0:
                                chain = 0
                        else:
                                chain += 1
                        if chain == 5:
                                highest_rank = rank
                return highest_rank

        def possibleStraights(self):
                myStraightStrength = self.straightStrength()
                count = 0
                pattern = 0
                # Bit magic to find pattern in last 5 ranks
                for rank in self.comm_card_num_rank:
                        if pattern >= 16:
                                pattern -= 16
                        pattern = pattern << 1
                        if self.comm_card_num_rank[rank] >= 1:
                                pattern += 1
                        if rank > myStraightStrength:
                                # 11110
                                if pattern == 30:
                                        count += 4 - self.hole_card_num_rank[rank]
                                # 01111
                                elif pattern == 15 and rank >= 5:
                                        count += 4 - self.hole_card_num_rank[rank-4]
                                # 10111
                                elif pattern == 23:
                                        count += 4 - self.hole_card_num_rank[rank-3]
                                # 11011
                                elif pattern == 27:
                                        count += 4 - self.hole_card_num_rank[rank-2]
                                # 11101
                                elif pattern == 29:
                                        count += 4 - self.hole_card_num_rank[rank-1]
                                # No fast way to estimate when 2 cards are needed
                                elif bin(pattern).count('1') == 3:
                                        count += 4 # idk what number to put here but it should definitely be low
                return count

        # Highest rank in a flush
        def flushStrength(self):
                for suit in self.num_suits:
                        if self.num_suits[suit] >= 5:
                                return self.suit_high[suit]
                return 0

        # Quick estimate number of possible flushes
        def possibleFlushes(self):
                count = 0
                for suit in self.comm_card_num_suits:
                        if self.comm_card_num_suits[suit] >= 3:
                                # Estimate number of flushes higher than the one we have, if we have any
                                if self.num_suits[suit] >= 5:
                                        count += 14 - self.suit_high[suit]
                                # If we don't have any, count all possible flushes
                                else:
                                        count += 13 - self.num_suits[suit]
                return count

        def haveStraightFlush(self):
                return int(self.flushStrength() > 0 and self.straightStrength() > 0)

        def haveFourOfAKind(self):
                for rank in self.num_rank:
                        if self.num_rank[rank] == 4:
                                return 1
                return 0

        def haveFullHouse(self):
                highest_trip = 0
                highest_doub = 0
                for rank in self.num_rank:
                        if self.num_rank[rank] >= 3 and rank > highest_trip:
                                if highest_doub < highest_trip:
                                        highest_doub = highest_trip
                                highest_trip = rank
                        if self.num_rank[rank] >= 2 and rank > highest_doub and rank > highest_trip:
                                highest_doub = rank
                return int(highest_trip > 0 and highest_doub > 0)

        def haveFullHouseOrBetter(self):
                return self.haveFullHouse() or self.haveStraightFlush() or self.haveFourOfAKind()
                
                                
########## TEST ##########

# hole_card_list = ['C4', 'DQ']
# community_card_list = ['D4', 'C5', 'CQ', 'CA', 'HK']

# hole_card = gen_cards(hole_card_list)
# community_card = gen_cards(community_card_list)                                                                
# cards = DecomposedCards(hole_card, community_card)

# print("Hole cards: " + str(hole_card_list))
# print("Community cards: " + str(community_card_list))
# print()
# print("0 highCard: " + str(cards.highCard()))
# print("1 singlePairStrength: " + str(cards.singlePairStrength()))
# print("2 numberOfHigherFormableSinglePairs: " + str(cards.numberOfHigherFormableSinglePairs()))
# print("3 numberOfOuts: " + str(cards.numberOfOuts()))
# print("4 doublePairStrength: " + str(cards.doublePairStrength()))
# print("5 numberOfHigherFormableDoublePairs: " + str(cards.numberOfHigherFormableDoublePairs()))
# print("6 tripleStrength: " + str(cards.tripleStrength()))
# print("7 numberOfHigherFormableTriples: " + str(cards.numberOfHigherFormableTriples()))
# print("8 straightStrength: " + str(cards.straightStrength()))
# print("9 possibleStraights: " + str(cards.possibleStraights()))
# print("10 flushStrength: "+ str(cards.flushStrength()))
# print("11 possibleFlushes: "+ str(cards.possibleFlushes()))
# print("haveStraightFlush: " + str(cards.haveStraightFlush()))
# print("haveFullHouse: " + str(cards.haveFullHouse()))
# print("INF haveFullHouseOrBetter: " + str(cards.haveFullHouseOrBetter()))
# print()

# fast = FASTHeuristic([1,1,1,1,1,1,1,1,1,1,1,1])

# print("FAST: " + str(fast.getEV(hole_card, community_card)))

