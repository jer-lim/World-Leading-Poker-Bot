"""
This implementation of advesarial search ignores the size of the pot.
It only models:
1) Given the state of the community cards, current cards on hand
2) three possible transition states of each player
3) Whether the player is expected to win given a set of cards
4) POST FLOP

This simple implementation makes a few assumptions:
1) Currently at the start of the showdown phase.
2) matching previous

Using MiniMax (hence probabilities/heuristic are not involved)
Attempt to maximise utility given current set of hole cards/community cards
Terminates after the last community card is drawn

#TODO:
Work on ChanceNode
It currently returns ONE decision node, using a random card
"""

indent = 0
def indent_print(x):
    print("   " * indent + str(x))
from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate, _pick_unused_card

RAISE_TURN_THRESHOLD = 2

class AdversarialSeach:
    def __init__(self, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.pot = pot

    def decide(self, actions):
        node = DecisionNode(0,self.hole_cards, self.community_cards, self.pot)
        return node.getBestAction(actions)

class DecisionNode:
    def __init__(self, turn, hole_cards, community_cards, pot, raise_turn = 0, called=False):

        self.hole_cards = hole_cards
        self.turn = turn
        self.opponent = 1 - self.turn
        self.community_cards = community_cards
        self.remaining_cards = 5 - len(community_cards)
        self.pot = pot
        self.raise_turn = raise_turn
        self.called = called

    def getBestAction(self, actions):
        action_map = {"raise": self.raise_stakes, "fold":self.fold, "call":self.call}
        action_funcs = [(action,action_map.get(action)) for action in actions]
        results = {}
        for label, func in action_funcs:
            node = func()
            value = node.eval()
            print(label, value)
            if value != None:
                results[label] = value
        indent_print(results)
        return max(results, key=results.get)

    """
    Returns an expected utility value at the current node
    """
    def eval(self):
        global indent
        indent += 1

        indent_print("-MY TURN-"  if not (self.turn) else "-OPP TURN-")
        #Terminal node
        if self.remaining_cards == 0 and not self.called:
            return self.expected_value()

        f = max if self.turn == 0 else min

        actions = [self.raise_stakes, self.fold, self.call]

        results = []
        for action in actions:
            node = action()
            if node != None:
                value = node.eval()
                results.append(value)
                indent_print(value)
        indent_print("VALUE: " + str(f(results)))
        indent -= 1
        return f(results)

    def expected_value(self):
        cards = self.hole_cards if self.turn == 0 else _pick_unused_card(2, self.hole_cards + self.community_cards)
        win_prob = estimate_hole_card_win_rate(
                nb_simulation=10,
                nb_player=2,
                hole_card=cards,
                community_card=self.community_cards
                )
        return win_prob * self.pot + (1-win_prob) * (-1) * self.pot
    """
    Generates next node with raised stakes
    """
    def raise_stakes(self):
        if self.raise_turn >= RAISE_TURN_THRESHOLD:
            return None
        indent_print(str(self.turn) + ": EXPLORE RAISED")
        return DecisionNode(self.opponent, self.hole_cards, self.community_cards, self.pot + 10, self.raise_turn + 1, called=True)
    """
    Generates a next node that describes terminated value
    """
    def fold(self):
        indent_print(str(self.turn) + ": EXPLORE FOLDED")
        return FoldedNode(self.opponent, self.pot)
    """
    Generates the next node, allows it to go to chance phase
    """
    def call(self):
        indent_print(str(self.turn) + ": EXPLORE CALL")
        if self.called:
            if self.remaining_cards == 0:
                return EndingNode(self.expected_value())
            else:
                return ChanceNode(self.hole_cards, self.community_cards, pot)
        return DecisionNode(self.opponent, self.hole_cards, self.community_cards, self.pot, called=True)

class EndingNode:
    def __init__(self, val):
        self.val = val
    def eval(self):
        return self.val

class FoldedNode:
    def __init__(self, winner, pot):
        self.winner = winner
        self.pot = pot
    def eval(self):
        indent_print("Opponent folded. Winner: " + str(self.winner))
        return (-1) *self.pot if self.winner else self.pot

class ChanceNode:
    def __init__(self, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.pot = pot
    def eval(self):
        new_card = _pick_unused_card(1, self.hole_cards + self.community_cards)
        node = DecisionNode(0, self.hole_cards, self.community_cards + new_card, self.pot)
        return node.eval()