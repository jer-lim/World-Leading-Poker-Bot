from pypokerengine.players import BasePokerPlayer
import random as rand
from adversarial_search import AdversarialSearch
import math

from pypokerengine.utils.card_utils import gen_cards

LEARNING_RATE = 0.000001


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


class OurPlayer(BasePokerPlayer):
    def __init__(self):
        self.action_weights = [1, 1, 1]
        self.heuristic_weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                                  1]  # For heuristic function
        self.stack_start_round = 0
        self.last_action = "call"
        self.action_counts = [0, 0]

    def declare_action(self, valid_actions, hole_card, round_state):
        if round_state["street"] == "preflop":
            #PREFLOP
            return "call"
        hole_cards = gen_cards(hole_card)
        community_cards = gen_cards(round_state["community_card"])
        pot = round_state["pot"]["main"]["amount"]
        self.last_action = AdversarialSearch(
            hole_cards, community_cards, pot, self.heuristic_weights).decide(
                [action.get("action") for action in valid_actions],
                self.action_weights)
        if self.last_action == "call":
            self.action_counts[0] += 1
        else:
            self.action_counts[1] += 1
        return self.last_action

    def receive_game_start_message(self, game_info):
        self.action_weights = [1, 1, 1]
        return

    def receive_round_start_message(self, round_count, hole_card, seats):
        self.action_counts = [0, 0]

        self.stack_start_round = list(
            filter(lambda x: x["uuid"] == self.uuid, seats))[0]["stack"]

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        if len(winners) == 0:  #Safety check
            return
        new_stack = list(
            filter(lambda x: x["uuid"] == self.uuid,
                   round_state["seats"]))[0]["stack"]
        to_penalize = self.last_action
        if to_penalize == "fold":
            self.action_weights = MWU(self.action_weights, self.last_action,
                                      LEARNING_RATE,
                                      self.stack_start_round - new_stack)
        else:
            if self.action_counts[0] > self.action_counts[1]:
                self.action_weights = MWU(self.action_weights, "call",
                                          LEARNING_RATE,
                                          self.stack_start_round - new_stack)
                self.action_weights = MWU(self.action_weights, "raise",
                                          LEARNING_RATE,
                                          self.stack_start_round - new_stack)
            else:
                self.action_weights = MWU(self.action_weights, "raise",
                                          LEARNING_RATE,
                                          self.stack_start_round - new_stack)

        # print("Loss: {}, Last action: {}, call - raise: {}".format(
        # (self.stack_start_round - new_stack), self.last_action, self.action_counts[0]-self.action_counts[1]))
        # print(self.action_weights)

    # Sets the new weights of the Player's actions
    def set_heuristic_weights(self, index, value):
        self.heuristic_weights[index] = value


def setup_ai():
    return OurPlayer()
