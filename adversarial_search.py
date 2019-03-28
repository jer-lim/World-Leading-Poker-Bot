"""
This implementation of advesarial search only models:
1) The state of the community cards, current hole_cards of myself
2) three possible transition states of each player (fold, call, raise)
3) POST FLOP onwards
Decision Node: Represents decision node of myself or of opponent
Ending Node: Represents the ending (i.e. when all possible cards are drawn)
Folded Node: Represents the outcome from myself or opponent folding
Chance Node: Represents the new card drawn
Heuristic adopted:
Look at expected value of decision node:
win_prob * self.pot + (1-win_prob) * (-1) * self.pot
"""
import abc
from pypokerengine.engine.hand_evaluator import HandEvaluator
from collections import defaultdict
indent = 0


def indent_print(x):
    print("   " * indent + str(x))


from pypokerengine.utils.card_utils import gen_cards, estimate_hole_card_win_rate, _pick_unused_card, gen_deck

RAISE_TURN_THRESHOLD = 2


class AdversarialSeach:
    def __init__(self, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.pot = pot

    def decide(self, actions):
        node = DecisionNode(0, self.hole_cards, self.community_cards, self.pot)
        return node.getBestAction(actions)

class TerminalNode:
    __metaclass__ = abc.ABCMeta

    def max_value(self, alpha, beta):
        return self.eval()
    def min_value(self, alpha, beta):
        return self.eval()
    @abc.abstractmethod
    def eval(self):
        pass


class DecisionNode:
    def __init__(self,
                 turn,
                 hole_cards,
                 community_cards,
                 pot,
                 raise_turn=0,
                 opponent_called=False,
                 opponent_raised=False):
        """
        Params
        ------
        turn: 0 for my turn, 1 for opponent's turn
        hole_cards: my hole cards (random cards generated for opponent)
        raise_turn: current times in street that raise has been called
        opponent_called: True if opponent called right before
        opponent_raised: True if opponent raised right before
        """

        self.hole_cards = hole_cards
        self.turn = turn
        self.opponent = 1 - self.turn
        self.community_cards = community_cards
        self.remaining_cards = 5 - len(community_cards)
        self.pot = pot
        self.raise_turn = raise_turn
        self.opponent_called = opponent_called
        self.opponent_raised = opponent_raised
        self.win_prob = estimate_hole_card_win_rate(
            nb_simulation=10,
            nb_player=2,
            hole_card=self.hole_cards,
            community_card=self.community_cards)

    def getBestAction(self, actions):
        action_map = {
            "raise": self.raise_stakes,
            "fold": self.fold,
            "call": self.call
        }
        action_funcs = [(action, action_map.get(action)) for action in actions]
        results = {}
        for label, func in action_funcs:
            node = func()
            print("TESTING ACTION: " + str(label))
            value = node.eval()
            print("DONE TESTING ACTION: " + str(label) + " VAL:" + str(value))
            print("----------------------------------")

            if value != None:
                results[label] = value
        indent_print(results)
        return max(results, key=results.get)

    def eval(self, alpha=-float("inf"), beta=float("inf")):
        """
        Returns an expected utility value at the current node
        """

        global indent
        indent += 1

        indent_print("-MY TURN-" if not (self.turn) else "-OPP TURN-")
        #Terminal node #TODO: Think about whether this is needed
        if self.remaining_cards == 0 and not self.called_or_raised:
            indent -= 1
            return self.expected_value()

        if self.turn == 0:
            return self.max_value(alpha, beta)
        else:
            return self.min_value(alpha, beta)

    def max_value(self, alpha, beta):
        actions = self.get_available_actions()

        v = -float("inf")
        for action in actions:
            v = max(v, action().min_value(alpha,beta))
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    def min_value(self, alpha, beta):
        actions = self.get_available_actions()

        v = float("inf")
        for action in actions:
            v = min(v, action().max_value(alpha, beta))
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

    def expected_value(self):
        return self.win_prob * self.pot + (1 - self.win_prob) * (-1) * self.pot

    def get_available_actions(self):
        actions = [self.fold, self.call]
        if self.raise_turn < RAISE_TURN_THRESHOLD:
            actions.append(self.raise_stakes)
        return actions

    def raise_stakes(self):
        """
        Generates next node with raised stakes
        """
        if self.raise_turn >= RAISE_TURN_THRESHOLD:
            return None
        indent_print(str(self.turn) + ": EXPLORE RAISED")
        if self.opponent_raised:
            #Counter raise
            increment_val = 20
        else:
            increment_val = 10
        return DecisionNode(
            self.opponent,
            self.hole_cards,
            self.community_cards,
            self.pot + increment_val,
            raise_turn = self.raise_turn + 1,
            opponent_raised=True)

    def fold(self):
        """
        Generates a next node that describes terminated value
        """
        indent_print(str(self.turn) + ": EXPLORE FOLDED")
        return FoldedNode(self.opponent, self.pot)

    def call(self):
        """
        Generates the next node, allows it to go to chance phase
        """
        indent_print(str(self.turn) + ": EXPLORE CALL")
        if self.opponent_called or self.opponent_raised:
            if self.opponent_raised:
                self.pot += 10
            if self.remaining_cards == 0:
                return EndingNode(self.expected_value())
            else:
                return ChanceNode(self.hole_cards, self.community_cards,
                                  self.pot)
        return DecisionNode(
            self.opponent,
            self.hole_cards,
            self.community_cards,
            self.pot,
            opponent_called=True)


class EndingNode(TerminalNode):
    def __init__(self, val):
        self.val = val

    def eval(self):
        return self.val


class FoldedNode(TerminalNode):
    def __init__(self, winner, pot):
        self.winner = winner
        self.pot = pot

    def eval(self):
        indent_print("A player folded. Winner: " + str(self.winner))
        return (-1) * self.pot if self.winner else self.pot


class ChanceNode(TerminalNode):
    def __init__(self, hole_cards, community_cards, pot):
        self.hole_cards = hole_cards
        self.community_cards = community_cards
        self.pot = pot

    def eval(self):
        """
        Generates and checks only 1 card per meaningful outcome. Returns expected utility.
        i.e. Given a set of cards, get all the cards that have not been drawn.
        Check the outcome of the hand given the additional card. Outcomes can be
        ONEPAIR, FLUSH, etc. Only 1 permutation that gives that outcome is checked.
        """
        # TODO: Optimise gen_hand_rank_info as there are currently alot of useless steps
        remaining_cards = gen_deck(
            exclude_cards=self.hole_cards + self.community_cards)
        n = remaining_cards.size()
        #Store the utility value given for that outcome
        memo = {}
        #Number of counts that generates the OUTCOME
        count = defaultdict(int)
        while remaining_cards.size() > 0:
            new_card = remaining_cards.draw_card()
            strength = HandEvaluator.gen_hand_rank_info(
                self.hole_cards,
                self.community_cards + [new_card])["hand"]["strength"]
            if strength not in memo:
                memo[strength] = DecisionNode(
                    0, self.hole_cards, self.community_cards + [new_card],
                    self.pot).eval()
            count[strength] += 1

        #Return expected value
        return sum(
            [count[strength] * memo[strength] for strength in memo.keys()]) / n
