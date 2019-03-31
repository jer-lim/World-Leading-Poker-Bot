from pypokerengine.players import BasePokerPlayer
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate
from pypokerengine.engine.hand_evaluator import HandEvaluator
hole_card = gen_cards(['H7', 'D3'])
community_card = gen_cards(['D2', 'HQ', 'C7'])
import timeit
"""
func = lambda : estimate_hole_card_win_rate(
        nb_simulation=100,
        nb_player=2,
        hole_card=gen_cards(hole_card),
        community_card=gen_cards(community_card)
        )
time = timeit.timeit(func,number = 100)/100
print("time: " + str(time))
print(func())

"""
from adversarial_search import AdversarialSeach
tries = 1

print(timeit.timeit(lambda:AdversarialSeach(hole_card, community_card, 40).decide(["raise", "fold", "call"], [1,1,1]), number=tries)/tries)
