from pypokerengine.players import BasePokerPlayer
import random as rand
import pprint
from handscorer import HandScorer

class BootStrapBot(BasePokerPlayer):

  def __init__(self):
    self.hand_scorer = HandScorer()

  def declare_action(self, valid_actions, hole_card, round_state):
    pp = pprint.PrettyPrinter(indent=2)
    score = self.hand_scorer.score_hole_cards(hole_card)

    if (score >= 0):
      return self.__raise_or_call(valid_actions)
    else:
      return "fold"
    

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

  def __raise_or_call(self, valid_actions):
    if {"action": "raise"} in valid_actions:
      return "raise"
    else:
      return "call"

def setup_ai():
  return BootStrapBot()
