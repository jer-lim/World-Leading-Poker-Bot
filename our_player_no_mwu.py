from pypokerengine.players import BasePokerPlayer
import random as rand
from adversarial_search import AdversarialSearch
import collections
import math

from pypokerengine.utils.card_utils import gen_cards

PreflopOdds = collections.namedtuple('PreflopOdds', 'ev win tie occur cumulative')

def MWU(action_weights, factor_to_punish, punish_constant,
        loss):  #factor_to_punish should be the previous move made
    punish_rate = math.exp(-punish_constant * loss)
    if factor_to_punish == "call":
        action_weights = [
            action_weights[0] * punish_rate, action_weights[1],
            action_weights[2]
        ]
    elif factor_to_punish == "raise":
        action_weights = [
            action_weights[0], action_weights[1] * punish_rate,
            action_weights[2]
        ]
    elif factor_to_punish == "fold":
        action_weights = [
            action_weights[0], action_weights[1],
            action_weights[2] * punish_rate
        ]
    else:
        pass
    return action_weights


class OurPlayerNoMwu(BasePokerPlayer):
    def __init__(self, weights = [0.8425,2.3519,0.19,1.6801,0.7491,0.3869,0.855,0.7166,-0.24,0.085,-0.21,0.035,0.52], preflop_weights = [-0.23, 0, 0, 0, 0, 0]):
        self.hand_scorer = HandScorer()
        self.action_weights = [1, 1, 1]
        self.heuristic_weights = weights  # For heuristic function
        self.preflop_weights = preflop_weights
        self.stack_start_round = 0
        self.last_action = "call"

    def declare_action(self, valid_actions, hole_card, round_state):
        self.is_big_blind = self.__is_big_blind(round_state)
        if round_state["street"] == "preflop":
            #PREFLOP
            bb_score = 1
            score = self.hand_scorer.score_hole_cards(hole_card)
            # Fold Below
            if score < self.preflop_weights[0] + self.preflop_weights[4] * bb_score:
                return "fold"
            # Raise Above
            elif score < self.preflop_weights[1] + self.preflop_weights[5] * bb_score:
                # Bluff Raise
                if rand.random() < self.preflop_weights[2]:
                    if {"action": "raise"} in valid_actions:
                        return "raise"
                    else:
                        return "call"
                return "call"
            else:
                # Bluff Call
                if rand.random() < self.preflop_weights[3]:
                    return "call"
                if {"action": "raise"} in valid_actions:
                    return "raise"
                else:
                    return "call"

        hole_cards = gen_cards(hole_card)
        community_cards = gen_cards(round_state["community_card"])
        pot = round_state["pot"]["main"]["amount"]
        self.last_action = AdversarialSearch(self,
            hole_cards, community_cards,
            pot, self.heuristic_weights).decide([action.get("action") for action in valid_actions],
                        self.action_weights)
        return self.last_action

    def __is_big_blind(self, round_state):
        if (round_state["big_blind_pos"] == self.seatNum):
            return True
        else:
            return False

    def __find_position(self, game_info):
        seatNum = 0
        for seat in game_info['seats']:
            if seat['uuid'] != self.uuid:
                seatNum += 1
            else:
                break
        return seatNum

    def receive_game_start_message(self, game_info):
        self.seatNum = self.__find_position(game_info)

    def receive_round_start_message(self, round_count, hole_card, seats):

        self.stack_start_round = list(
            filter(lambda x: x["uuid"] == self.uuid, seats))[0]["stack"]

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    # Sets the new weights of the Player's actions
    def set_heuristic_weights(self, index, value):
        self.heuristic_weights[index] = value

# Assign a score to a hand
class HandScorer(object):

  def score_hole_cards(self, hole_cards):
    # Generate easily readable hand
    hand = HoleCards.from_array(hole_cards)

    # --- SCORING LOGIC HERE ---
    score = hand.get_ev()

    # return
    return score

# Help manage our cards better
class HoleCards(object):
  __slots__ = ('rank1', 'rank2', 'suited')
  def __init__(self, rank1, rank2, suited):
    self.rank1 = rank1
    self.rank2 = rank2
    self.suited = suited

  def get_ev(self):
    return preflop_odds[self].ev

  @staticmethod
  def from_array(hole_cards):
    suit1, rank1 = HoleCards.__parse_card(hole_cards[0])
    suit2, rank2 = HoleCards.__parse_card(hole_cards[1])
    if suit1 == suit2:
      suited = True
    else:
      suited = False

    if rank1 > rank2:
      return HoleCards(rank1, rank2, suited)
    else:
      return HoleCards(rank2, rank1, suited)

  @staticmethod
  def from_str(hole_cards):
    suit1, rank1 = HoleCards.__parse_card("x" + hole_cards[0]);
    suit2, rank2 = HoleCards.__parse_card("x" + hole_cards[1])
    if (hole_cards[2] == "s"):
      suited = True
    else:
      suited = False

    if rank1 > rank2:
      return HoleCards(rank1, rank2, suited)
    else:
      return HoleCards(rank2, rank1, suited)
  
  @staticmethod  
  def __parse_card(card):
    suit = card[0]
    rank = card[1]
    if rank == 'T':
      rank = 10
    elif rank == 'J':
      rank = 11
    elif rank == 'Q':
      rank = 12
    elif rank == 'K':
      rank = 13
    elif rank == 'A':
      rank = 14
    return suit, int(rank)

  def __str__(self):
    output = ""
    if self.rank1 == 10: output += "T"
    elif self.rank1 == 11: output += "J"
    elif self.rank1 == 12: output += "Q"
    elif self.rank1 == 13: output += "K"
    elif self.rank1 == 14: output += "A"
    else: output += str(self.rank1)

    if self.rank2 == 10: output += "T"
    elif self.rank2 == 11: output += "J"
    elif self.rank2 == 12: output += "Q"
    elif self.rank2 == 13: output += "K"
    elif self.rank2 == 14: output += "A"
    else: output += str(self.rank2)

    if self.suited: output += "s"
    else: output += "o"
    return output

  def __hash__(self):
    return hash((self.rank1, self.rank2, self.suited))

  def __eq__(self, other):
    return self.rank1 == other.rank1 and self.rank2 == other.rank2 and self.suited == other.suited

# From https://caniwin.com/texasholdem/preflop/heads-up.php
preflop_odds = {
HoleCards.from_str('AAo') : PreflopOdds(0.70, 84.93, 0.54, 0.45, 0.45),
HoleCards.from_str('KKo') : PreflopOdds(0.64, 82.11, 0.55, 0.45, 0.90),
HoleCards.from_str('QQo') : PreflopOdds(0.59, 79.63, 0.58, 0.45, 1.35),
HoleCards.from_str('JJo') : PreflopOdds(0.54, 77.15, 0.63, 0.45, 1.80),
HoleCards.from_str('TTo') : PreflopOdds(0.50, 74.66, 0.70, 0.45, 2.26),
HoleCards.from_str('99o') : PreflopOdds(0.44, 71.66, 0.78, 0.45, 2.71),
HoleCards.from_str('88o') : PreflopOdds(0.38, 68.71, 0.89, 0.45, 3.16),
HoleCards.from_str('AKs') : PreflopOdds(0.34, 66.21, 1.65, 0.30, 3.46),
HoleCards.from_str('77o') : PreflopOdds(0.32, 65.72, 1.02, 0.45, 3.92),
HoleCards.from_str('AQs') : PreflopOdds(0.32, 65.31, 1.79, 0.30, 4.22),
HoleCards.from_str('AJs') : PreflopOdds(0.30, 64.39, 1.99, 0.30, 4.52),
HoleCards.from_str('AKo') : PreflopOdds(0.30, 64.46, 1.70, 0.90, 5.42),
HoleCards.from_str('ATs') : PreflopOdds(0.29, 63.48, 2.22, 0.30, 5.73),
HoleCards.from_str('AQo') : PreflopOdds(0.28, 63.50, 1.84, 0.90, 6.63),
HoleCards.from_str('AJo') : PreflopOdds(0.27, 62.53, 2.05, 0.90, 7.54),
HoleCards.from_str('KQs') : PreflopOdds(0.26, 62.40, 1.98, 0.30, 7.84),
HoleCards.from_str('66o') : PreflopOdds(0.26, 62.70, 1.16, 0.45, 8.29),
HoleCards.from_str('A9s') : PreflopOdds(0.25, 61.50, 2.54, 0.30, 8.59),
HoleCards.from_str('ATo') : PreflopOdds(0.25, 61.56, 2.30, 0.90, 9.50),
HoleCards.from_str('KJs') : PreflopOdds(0.25, 61.47, 2.18, 0.30, 9.80),
HoleCards.from_str('A8s') : PreflopOdds(0.23, 60.50, 2.87, 0.30, 10.10),
HoleCards.from_str('KTs') : PreflopOdds(0.23, 60.58, 2.40, 0.30, 10.40),
HoleCards.from_str('KQo') : PreflopOdds(0.22, 60.43, 2.04, 0.90, 11.31),
HoleCards.from_str('A7s') : PreflopOdds(0.21, 59.38, 3.19, 0.30, 11.61),
HoleCards.from_str('A9o') : PreflopOdds(0.21, 59.44, 2.64, 0.90, 12.51),
HoleCards.from_str('KJo') : PreflopOdds(0.21, 59.44, 2.25, 0.90, 13.42),
HoleCards.from_str('55o') : PreflopOdds(0.20, 59.64, 1.36, 0.45, 13.87),
HoleCards.from_str('QJs') : PreflopOdds(0.20, 59.07, 2.37, 0.30, 14.17),
HoleCards.from_str('K9s') : PreflopOdds(0.19, 58.63, 2.70, 0.30, 14.47),
HoleCards.from_str('A5s') : PreflopOdds(0.19, 58.06, 3.71, 0.30, 14.78),
HoleCards.from_str('A6s') : PreflopOdds(0.19, 58.17, 3.45, 0.30, 15.08),
HoleCards.from_str('A8o') : PreflopOdds(0.19, 58.37, 2.99, 0.90, 15.98),
HoleCards.from_str('KTo') : PreflopOdds(0.19, 58.49, 2.48, 0.90, 16.89),
HoleCards.from_str('QTs') : PreflopOdds(0.18, 58.17, 2.59, 0.30, 17.19),
HoleCards.from_str('A4s') : PreflopOdds(0.18, 57.13, 3.79, 0.30, 17.49),
HoleCards.from_str('A7o') : PreflopOdds(0.17, 57.16, 3.34, 0.90, 18.40),
HoleCards.from_str('K8s') : PreflopOdds(0.16, 56.79, 3.04, 0.30, 18.70),
HoleCards.from_str('A3s') : PreflopOdds(0.16, 56.33, 3.77, 0.30, 19.00),
HoleCards.from_str('QJo') : PreflopOdds(0.16, 56.90, 2.45, 0.90, 19.90),
HoleCards.from_str('K9o') : PreflopOdds(0.15, 56.40, 2.80, 0.90, 20.81),
HoleCards.from_str('A5o') : PreflopOdds(0.15, 55.74, 3.90, 0.90, 21.71),
HoleCards.from_str('A6o') : PreflopOdds(0.15, 55.87, 3.62, 0.90, 22.62),
HoleCards.from_str('Q9s') : PreflopOdds(0.15, 56.22, 2.88, 0.30, 22.92),
HoleCards.from_str('K7s') : PreflopOdds(0.15, 55.84, 3.38, 0.30, 23.22),
HoleCards.from_str('JTs') : PreflopOdds(0.15, 56.15, 2.74, 0.30, 23.52),
HoleCards.from_str('A2s') : PreflopOdds(0.14, 55.50, 3.74, 0.30, 23.83),
HoleCards.from_str('QTo') : PreflopOdds(0.14, 55.94, 2.68, 0.90, 24.73),
HoleCards.from_str('44o') : PreflopOdds(0.14, 56.25, 1.53, 0.45, 25.18),
HoleCards.from_str('A4o') : PreflopOdds(0.13, 54.73, 3.99, 0.90, 26.09),
HoleCards.from_str('K6s') : PreflopOdds(0.13, 54.80, 3.67, 0.30, 26.39),
HoleCards.from_str('K8o') : PreflopOdds(0.12, 54.43, 3.17, 0.90, 27.30),
HoleCards.from_str('Q8s') : PreflopOdds(0.12, 54.41, 3.20, 0.30, 27.60),
HoleCards.from_str('A3o') : PreflopOdds(0.11, 53.85, 3.97, 0.90, 28.50),
HoleCards.from_str('K5s') : PreflopOdds(0.11, 53.83, 3.91, 0.30, 28.80),
HoleCards.from_str('J9s') : PreflopOdds(0.11, 54.11, 3.10, 0.30, 29.11),
HoleCards.from_str('Q9o') : PreflopOdds(0.10, 53.86, 2.99, 0.90, 30.01),
HoleCards.from_str('JTo') : PreflopOdds(0.10, 53.82, 2.84, 0.90, 30.92),
HoleCards.from_str('K7o') : PreflopOdds(0.10, 53.41, 3.54, 0.90, 31.82),
HoleCards.from_str('A2o') : PreflopOdds(0.09, 52.94, 3.96, 0.90, 32.73),
HoleCards.from_str('K4s') : PreflopOdds(0.09, 52.88, 3.99, 0.30, 33.03),
HoleCards.from_str('Q7s') : PreflopOdds(0.08, 52.52, 3.55, 0.30, 33.33),
HoleCards.from_str('K6o') : PreflopOdds(0.08, 52.29, 3.85, 0.90, 34.23),
HoleCards.from_str('K3s') : PreflopOdds(0.08, 52.07, 3.96, 0.30, 34.53),
HoleCards.from_str('T9s') : PreflopOdds(0.08, 52.37, 3.30, 0.30, 34.84),
HoleCards.from_str('J8s') : PreflopOdds(0.08, 52.31, 3.40, 0.30, 35.14),
HoleCards.from_str('33o') : PreflopOdds(0.07, 52.83, 1.70, 0.45, 35.59),
HoleCards.from_str('Q6s') : PreflopOdds(0.07, 51.67, 3.86, 0.30, 35.89),
HoleCards.from_str('Q8o') : PreflopOdds(0.07, 51.93, 3.33, 0.90, 36.80),
HoleCards.from_str('K5o') : PreflopOdds(0.06, 51.25, 4.12, 0.90, 37.70),
HoleCards.from_str('J9o') : PreflopOdds(0.06, 51.63, 3.22, 0.90, 38.61),
HoleCards.from_str('K2s') : PreflopOdds(0.06, 51.23, 3.94, 0.30, 38.91),
HoleCards.from_str('Q5s') : PreflopOdds(0.05, 50.71, 4.11, 0.30, 39.21),
HoleCards.from_str('T8s') : PreflopOdds(0.04, 50.50, 3.65, 0.30, 39.51),
HoleCards.from_str('K4o') : PreflopOdds(0.04, 50.22, 4.20, 0.90, 40.42),
HoleCards.from_str('J7s') : PreflopOdds(0.04, 50.45, 3.74, 0.30, 40.72),
HoleCards.from_str('Q4s') : PreflopOdds(0.03, 49.76, 4.18, 0.30, 41.02),
HoleCards.from_str('Q7o') : PreflopOdds(0.03, 49.90, 3.72, 0.90, 41.93),
HoleCards.from_str('T9o') : PreflopOdds(0.03, 49.81, 3.43, 0.90, 42.83),
HoleCards.from_str('J8o') : PreflopOdds(0.02, 49.71, 3.55, 0.90, 43.74),
HoleCards.from_str('K3o') : PreflopOdds(0.02, 49.33, 4.18, 0.90, 44.64),
HoleCards.from_str('Q6o') : PreflopOdds(0.02, 48.99, 4.05, 0.90, 45.55),
HoleCards.from_str('Q3s') : PreflopOdds(0.02, 48.93, 4.16, 0.30, 45.85),
HoleCards.from_str('98s') : PreflopOdds(0.01, 48.85, 3.88, 0.30, 46.15),
HoleCards.from_str('T7s') : PreflopOdds(0.01, 48.65, 3.97, 0.30, 46.45),
HoleCards.from_str('J6s') : PreflopOdds(0.01, 48.57, 4.06, 0.30, 46.75),
HoleCards.from_str('K2o') : PreflopOdds(0.01, 48.42, 4.17, 0.90, 47.66),
HoleCards.from_str('22o') : PreflopOdds(0.00, 49.38, 1.89, 0.45, 48.11),
HoleCards.from_str('Q2s') : PreflopOdds(0.00, 48.10, 4.13, 0.30, 48.41),
HoleCards.from_str('Q5o') : PreflopOdds(0.00, 47.95, 4.32, 0.90, 49.32),
HoleCards.from_str('J5s') : PreflopOdds(0.00, 47.82, 4.33, 0.30, 49.62),
HoleCards.from_str('T8o') : PreflopOdds(0.00, 47.81, 3.80, 0.90, 50.52),
HoleCards.from_str('J7o') : PreflopOdds(0.00, 47.72, 3.91, 0.90, 51.43),
HoleCards.from_str('Q4o') : PreflopOdds(-0.01, 46.92, 4.40, 0.90, 52.33),
HoleCards.from_str('97s') : PreflopOdds(-0.01, 46.99, 4.25, 0.30, 52.63),
HoleCards.from_str('J4s') : PreflopOdds(-0.01, 46.86, 4.40, 0.30, 52.94),
HoleCards.from_str('T6s') : PreflopOdds(-0.02, 46.80, 4.28, 0.30, 53.24),
HoleCards.from_str('J3s') : PreflopOdds(-0.03, 46.04, 4.37, 0.30, 53.54),
HoleCards.from_str('Q3o') : PreflopOdds(-0.03, 46.02, 4.38, 0.90, 54.44),
HoleCards.from_str('98o') : PreflopOdds(-0.03, 46.06, 4.05, 0.90, 55.35),
HoleCards.from_str('87s') : PreflopOdds(-0.04, 45.68, 4.50, 0.30, 55.65),
HoleCards.from_str('T7o') : PreflopOdds(-0.04, 45.82, 4.15, 0.90, 56.56),
HoleCards.from_str('J6o') : PreflopOdds(-0.04, 45.71, 4.26, 0.90, 57.46),
HoleCards.from_str('96s') : PreflopOdds(-0.05, 45.15, 4.55, 0.30, 57.76),
HoleCards.from_str('J2s') : PreflopOdds(-0.05, 45.20, 4.35, 0.30, 58.06),
HoleCards.from_str('Q2o') : PreflopOdds(-0.05, 45.10, 4.37, 0.90, 58.97),
HoleCards.from_str('T5s') : PreflopOdds(-0.05, 44.93, 4.55, 0.30, 59.27),
HoleCards.from_str('J5o') : PreflopOdds(-0.05, 44.90, 4.55, 0.90, 60.18),
HoleCards.from_str('T4s') : PreflopOdds(-0.06, 44.20, 4.65, 0.30, 60.48),
HoleCards.from_str('97o') : PreflopOdds(-0.07, 44.07, 4.45, 0.90, 61.38),
HoleCards.from_str('86s') : PreflopOdds(-0.07, 43.81, 4.84, 0.30, 61.68),
HoleCards.from_str('J4o') : PreflopOdds(-0.07, 43.86, 4.63, 0.90, 62.59),
HoleCards.from_str('T6o') : PreflopOdds(-0.07, 43.84, 4.48, 0.90, 63.49),
HoleCards.from_str('95s') : PreflopOdds(-0.08, 43.31, 4.81, 0.30, 63.80),
HoleCards.from_str('T3s') : PreflopOdds(-0.08, 43.37, 4.62, 0.30, 64.10),
HoleCards.from_str('76s') : PreflopOdds(-0.09, 42.82, 5.08, 0.30, 64.40),
HoleCards.from_str('J3o') : PreflopOdds(-0.09, 42.96, 4.61, 0.90, 65.30),
HoleCards.from_str('87o') : PreflopOdds(-0.09, 42.69, 4.71, 0.90, 66.21),
HoleCards.from_str('T2s') : PreflopOdds(-0.10, 42.54, 4.59, 0.30, 66.51),
HoleCards.from_str('85s') : PreflopOdds(-0.10, 41.99, 5.10, 0.30, 66.81),
HoleCards.from_str('96o') : PreflopOdds(-0.11, 42.10, 4.77, 0.90, 67.72),
HoleCards.from_str('J2o') : PreflopOdds(-0.11, 42.04, 4.59, 0.90, 68.62),
HoleCards.from_str('T5o') : PreflopOdds(-0.11, 41.85, 4.78, 0.90, 69.53),
HoleCards.from_str('94s') : PreflopOdds(-0.12, 41.40, 4.90, 0.30, 69.83),
HoleCards.from_str('75s') : PreflopOdds(-0.12, 40.97, 5.39, 0.30, 70.13),
HoleCards.from_str('T4o') : PreflopOdds(-0.12, 41.05, 4.89, 0.90, 71.04),
HoleCards.from_str('93s') : PreflopOdds(-0.13, 40.80, 4.91, 0.30, 71.34),
HoleCards.from_str('86o') : PreflopOdds(-0.13, 40.69, 5.08, 0.90, 72.24),
HoleCards.from_str('65s') : PreflopOdds(-0.13, 40.34, 5.57, 0.30, 72.54),
HoleCards.from_str('84s') : PreflopOdds(-0.14, 40.10, 5.19, 0.30, 72.85),
HoleCards.from_str('95o') : PreflopOdds(-0.14, 40.13, 5.06, 0.90, 73.75),
HoleCards.from_str('T3o') : PreflopOdds(-0.14, 40.15, 4.87, 0.90, 74.66),
HoleCards.from_str('92s') : PreflopOdds(-0.15, 39.97, 4.88, 0.30, 74.96),
HoleCards.from_str('76o') : PreflopOdds(-0.15, 39.65, 5.33, 0.90, 75.86),
HoleCards.from_str('74s') : PreflopOdds(-0.16, 39.10, 5.48, 0.30, 76.16),
HoleCards.from_str('T2o') : PreflopOdds(-0.16, 39.23, 4.85, 0.90, 77.07),
HoleCards.from_str('54s') : PreflopOdds(-0.17, 38.53, 5.84, 0.30, 77.37),
HoleCards.from_str('85o') : PreflopOdds(-0.17, 38.74, 5.37, 0.90, 78.28),
HoleCards.from_str('64s') : PreflopOdds(-0.17, 38.48, 5.70, 0.30, 78.58),
HoleCards.from_str('83s') : PreflopOdds(-0.18, 38.28, 5.18, 0.30, 78.88),
HoleCards.from_str('94o') : PreflopOdds(-0.18, 38.08, 5.17, 0.90, 79.78),
HoleCards.from_str('75o') : PreflopOdds(-0.18, 37.67, 5.67, 0.90, 80.69),
HoleCards.from_str('82s') : PreflopOdds(-0.19, 37.67, 5.18, 0.30, 80.99),
HoleCards.from_str('73s') : PreflopOdds(-0.19, 37.30, 5.46, 0.30, 81.29),
HoleCards.from_str('93o') : PreflopOdds(-0.19, 37.42, 5.18, 0.90, 82.20),
HoleCards.from_str('65o') : PreflopOdds(-0.20, 37.01, 5.86, 0.90, 83.10),
HoleCards.from_str('53s') : PreflopOdds(-0.20, 36.75, 5.86, 0.30, 83.40),
HoleCards.from_str('63s') : PreflopOdds(-0.20, 36.68, 5.69, 0.30, 83.71),
HoleCards.from_str('84o') : PreflopOdds(-0.21, 36.70, 5.47, 0.90, 84.61),
HoleCards.from_str('92o') : PreflopOdds(-0.21, 36.51, 5.16, 0.90, 85.52),
HoleCards.from_str('43s') : PreflopOdds(-0.22, 35.72, 5.82, 0.30, 85.82),
HoleCards.from_str('74o') : PreflopOdds(-0.22, 35.66, 5.77, 0.90, 86.72),
HoleCards.from_str('72s') : PreflopOdds(-0.23, 35.43, 5.43, 0.30, 87.02),
HoleCards.from_str('54o') : PreflopOdds(-0.23, 35.07, 6.16, 0.90, 87.93),
HoleCards.from_str('64o') : PreflopOdds(-0.23, 35.00, 6.01, 0.90, 88.83),
HoleCards.from_str('52s') : PreflopOdds(-0.24, 34.92, 5.83, 0.30, 89.14),
HoleCards.from_str('62s') : PreflopOdds(-0.24, 34.83, 5.66, 0.30, 89.44),
HoleCards.from_str('83o') : PreflopOdds(-0.25, 34.74, 5.46, 0.90, 90.34),
HoleCards.from_str('42s') : PreflopOdds(-0.26, 33.91, 5.82, 0.30, 90.64),
HoleCards.from_str('82o') : PreflopOdds(-0.26, 34.08, 5.48, 0.90, 91.55),
HoleCards.from_str('73o') : PreflopOdds(-0.26, 33.71, 5.76, 0.90, 92.45),
HoleCards.from_str('53o') : PreflopOdds(-0.27, 33.16, 6.19, 0.90, 93.36),
HoleCards.from_str('63o') : PreflopOdds(-0.27, 33.06, 6.01, 0.90, 94.26),
HoleCards.from_str('32s') : PreflopOdds(-0.28, 33.09, 5.78, 0.30, 94.57),
HoleCards.from_str('43o') : PreflopOdds(-0.29, 32.06, 6.15, 0.90, 95.47),
HoleCards.from_str('72o') : PreflopOdds(-0.30, 31.71, 5.74, 0.90, 96.38),
HoleCards.from_str('52o') : PreflopOdds(-0.31, 31.19, 6.18, 0.90, 97.28),
HoleCards.from_str('62o') : PreflopOdds(-0.31, 31.07, 5.99, 0.90, 98.19),
HoleCards.from_str('42o') : PreflopOdds(-0.33, 30.11, 6.16, 0.90, 99.09),
HoleCards.from_str('32o') : PreflopOdds(-0.35, 29.23, 6.12, 0.90, 100.00)
}

def setup_ai():
    return OurPlayerNoMwu()
