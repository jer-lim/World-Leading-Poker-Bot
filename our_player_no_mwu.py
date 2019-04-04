from pypokerengine.players import BasePokerPlayer
import random as rand
from adversarial_search import AdversarialSearch
import math

from pypokerengine.utils.card_utils import gen_cards


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
    def __init__(self):
        self.action_weights = [1, 1, 1]
        self.heuristic_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]  # For heuristic function
        self.stack_start_round = 0
        self.last_action = "call"

    def declare_action(self, valid_actions, hole_card, round_state):
        if round_state["street"] == "preflop":
            #PREFLOP
            return "call"
        hole_cards = gen_cards(hole_card)
        community_cards = gen_cards(round_state["community_card"])
        pot = round_state["pot"]["main"]["amount"]
        self.last_action = AdversarialSearch(
            hole_cards, community_cards,
            pot, self.heuristic_weights).decide([action.get("action") for action in valid_actions],
                        self.action_weights)
        return self.last_action

    def receive_game_start_message(self, game_info):

        pass

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


def setup_ai():
    return OurPlayerNoMwu()
