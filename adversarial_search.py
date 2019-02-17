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
Work on chanceNode
"""


from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate


class AdversarialSeach:
    def __init__(self, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.community_cards = community_cards

    def decide(self):
        node = DecisionNode(self.hole_cards, self.community_cards)
        return node.getBestAction()

class DecisionNode:
    def __init__(self, turn, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.turn = turn
        self.opponent = 1 - self.turn
        self.community_cards = community_cards
        self.remainding_cards = 5 - len(community_cards)
        self.pot = pot

    def getBestAction(self):
        import pdb;pdb.set_trace()
        actions = [self.raise_stakes, self.fold, self.see]
        results = {}
        for action in actions:
            node = action()
            value = node.eval()
            results[action] = value
        return max(results.items(), results.get)

    """
    Returns an expected utility value at the current node
    """
    def eval(self):
        #Terminal node
        if self.remainding_cards == 0:

            return self.expected_value()

        f = max if self.turn else min
        import pdb;pdb.set_trace()

        actions = [self.raise_stakes, self.fold, self.see]

        results = []
        for action in actions:
            node = action()
            value = node.eval()
            results.append(value)
        return f(results)

    def expected_value(self):
        win_prob = estimate_hole_card_win_rate(
                nb_simulation=10,
                nb_player=2,
                hole_card=self.hole_cards,
                community_card=self.community_cards
                )
        return win_prob * self.pot + (1-win_prob) * (-1) * self.pot

    def raise_stakes(self):
        return DecisionNode(self.opponent, self.hole_cards, self.community_cards, self.pot + 10)
    """
    Generates a next node that describes terminated value
    """
    def fold(self):
        return TerminalNode(self.opponent, self.pot)
    """
    Generates the next node, allows it to go to chance phase
    """
    def see(self):
        return ChanceNode(self.hole_cards, self.community_cards, self.pot)

