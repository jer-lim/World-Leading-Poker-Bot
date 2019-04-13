from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from time import sleep
import pprint

'''
This player is the best player to ever existed in the poker world.
'''

ACTION_RAISE = "raise"
ACTION_CALL = "call"
ACTION_FOLD = "fold"

STREET_PREFLOP = "preflop"
STREET_FLOP = "flop"
STREET_TURN = "turn"
STREET_RIVER = "river"

class HandStrengthPlayer(BasePokerPlayer):

    global lost
    global win
    global incorrectLost
    lost = 0
    win = 0
    incorrectLost = 0

    def __init__(self):   
        self.UUID_SELF = ""
        self.UUID_ENEMY = ""
        self.last_action_self = None
        self.last_action_enemy = None

    def declare_action(self, valid_actions, hole_card, round_state):
        # valid_actions: list of actions player can perform
        # hole_card: the card this player have
        # round_state: The current state of this round. Contains the following,
          # dealer_btn: What is this?
          # big_blind_pos: Literal position of big blind
          # round_count: The current round count.
          # small_blind_pos: Literal position of small blind
          # next_player: Should be next player to play
          # small_blind_amount: small blind amount/cost
          # action_histories: Histories of action. Contains a dict with turn, preflop, flop, with a list of actions.
          # street: current moment of game I presume. (seems to be same as the other method param)
          # seats: Who is in which seat, laso contains the $$ they possess
          # community card: The card in river.
          # pot: money in pot
        if(self.estimatedStrength > 0.7):
            action = "raise"
        elif self.estimatedStrength > 0.3 or self.last_action_enemy == ACTION_CALL:
            action = "call"
        else:
            action = "fold"

        for i in valid_actions:
            if i["action"] == action:
                action = i["action"]
                return action  # action returned here is sent to the poker engine
        action = valid_actions[1]["action"]
        return action  # action returned here is sent to the poker engine

    def receive_game_start_message(self, game_info):
        # game_info returns a dict with the following
        # player_num, rule (rule of this particular game), seats(who is in each seats).
        # Set player UUIDs
        self.UUID_SELF = self.uuid
        for seat in game_info["seats"]: # Get the enemy uuid
            if seat["uuid"] != self.UUID_SELF:
                self.UUID_ENEMY = seat["uuid"]
                break
        assert self.UUID_ENEMY

    def receive_round_start_message(self, round_count, hole_card, seats):
        # hole_card: the card this player have
        self.hole_card = hole_card

        self.last_action_self = None
        self.last_action_enemy = None
        pass

    def receive_street_start_message(self, street, round_state):
        # street: current moment of the game.
        #  preflop  : Before opening card
        #  flop     : After opening first 3 card
        #  turn     : After opening 4th card
        #  river    : After opening 5th card
        # round_state: The current state of this round. Contains the following,
            # dealer_btn: What is this?
            # big_blind_pos: Literal position of big blind
            # round_count: The current round count.
            # small_blind_pos: Literal position of small blind
            # next_player: Should be next player to play
            # small_blind_amount: small blind amount/cost
            # action_histories: Histories of action. Contains a dict with turn, preflop, flop, with a list of actions.
            # street: current moment of game I presume. (seems to be same as the other method param)
            # seats: Who is in which seat, laso contains the $$ they possess
            # community card: The card in river.
            # pot: money in pot
        # pypokerutils.estimate_hand_strength(100, 2, round_state)
        holeCard = gen_cards(self.hole_card)
        communityCard = gen_cards(round_state["community_card"])
        self.estimatedStrength = estimate_hole_card_win_rate(
            nb_simulation=50, nb_player=2, hole_card=holeCard, community_card=communityCard)
        pass

    def receive_game_update_message(self, action, round_state):
        # Update self and enemy's last action
        if action["action"] == ACTION_CALL or action["action"] == ACTION_RAISE:
            if action["player_uuid"] == self.UUID_SELF:
                self.last_action_self = action
            else:
                self.last_action_enemy = action

    def receive_round_result_message(self, winners, hand_info, round_state):
        # winners: This round's winner
        # hand_info: Show info of all player's hand (Only have info when reached show down apparently)
        # print(winners, round_state["pot"])
        global lost
        global incorrectLost
        global win
        if winners[0]["name"] == "My agent":
            win += 1
        else:
            lost += 1
            if self.estimatedStrength > 0.5:
                incorrectLost += 1

        # print("{0} : {1}".format(win, lost))
        pass


def setup_ai():
    return HandStrengthPlayer()
