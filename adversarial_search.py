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

class AdversarialSeach:
    def __init__(self):
