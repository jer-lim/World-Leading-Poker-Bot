from pypokerengine.players import BasePokerPlayer
from time import sleep
import pprint

class RaisedPlayer(BasePokerPlayer):

  def declare_action(self, valid_actions, hole_card, round_state):
    for i in valid_actions:
      if i["action"] == "raise" and i["amount"]["min"] > -1:
        action, amount = i["action"], i["amount"]["min"]
        return action, amount  # action returned here is sent to the poker engine
    action, amount = valid_actions[1]["action"], valid_actions[1]["amount"]
    return action, amount # action returned here is sent to the poker engine

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

def setup_ai():
  return RandomPlayer()
