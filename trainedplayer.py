from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint

"""
In order to make a player trainable, it must contain:

Attributes: The individual values are irrelevant at this point, as the trainer will reset these values.
    call_weight
    raise_weight
    
Method: Trainer uses this method to modify the weights on the bots.
    def set_weights(self, call_weight, raise_weight):
        self.call_weight = call_weight
        self.raise_weight = raise_weight
"""

# Modified the RandomPlayer() Class

class TrainedPlayer(BasePokerPlayer):

    def __init__(self):
        self.call_weight = 0.5
        self.raise_weight = 0.2

        """""
        Probability Distribution: 
        #########################################################################################
        |       raise     |                    call                    |         fold           |
        #########################################################################################
        ^                 ^                                            ^                        ^
        0        (call_weight * raise_weight)                       (call_weight)               1
        
        """""

    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions format => [raise_action_pp = pprint.PrettyPrinter(indent=2)
        #pp = pprint.PrettyPrinter(indent=2)
        #print("------------ROUND_STATE(RANDOM)--------")
        #pp.pprint(round_state)
        #print("------------HOLE_CARD----------")
        #pp.pprint(hole_card)
        #print("------------VALID_ACTIONS----------")
        #pp.pprint(valid_actions)
        #print("-------------------------------")
        r = rand.random()
        if r <= self.call_weight * self.raise_weight and len(valid_actions) == 3:
            call_action_info = valid_actions[2]  # raise if applicable
        elif r <= self.call_weight:
            call_action_info = valid_actions[1]  # call
        else:
            call_action_info = valid_actions[0]  # fold
        action = call_action_info["action"]
        return action  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        pass

    def receive_round_start_message(self, round_count, hole_card, seats):
        pass

    def receive_street_start_message(self, street, round_state):
        pass

    def receive_game_update_message(self, action, round_state):
        pass

    def receive_round_result_message(self, winners, hand_info, round_state):
        pass

    # Sets the new weights of the Player
    # fold_weight is 1 - call_weight by default
    def set_weights(self, call_weight, raise_weight):
        self.call_weight = call_weight
        self.raise_weight = raise_weight

    def setup_ai():
        return TrainedPlayer()
