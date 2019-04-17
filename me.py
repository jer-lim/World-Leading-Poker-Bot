from pypokerengine.players import BasePokerPlayer
import random as rand
from adversarial_search import AdversarialSeach
import math

from pypokerengine.utils.card_utils import gen_cards



class MePlayer(BasePokerPlayer):
    def __init__(self, alpha = 0.000001):
        self.action_weights = [1, 1.1, 0.9]
        self.stack_start_round = 0
        self.last_action = "call"
        self.action_counts = [0,0]
        self.alpha = alpha

    def declare_action(self, valid_actions, hole_card, round_state):
        print(round_state)
        val = "call"
        import pdb;pdb.set_trace()
        return val

    def receive_game_start_message(self, game_info):
        print(game_info)
        return


    def receive_round_start_message(self, round_count, hole_card, seats):
        return

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

def setup_ai():
    return RandomPlayer()
