from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

hole_card = gen_cards(['HQ', 'D3'])
community_card = gen_cards(['SA', 'D2', 'CQ', 'D5', 'D4'])

# Just count suits.
def haveFlush(hole_card, community_card):
	numSuit = {}
	for suitNum in Card.SUIT_MAP.keys():
		numSuit[suitNum] = 0
	for card in hole_card + community_card:
		numSuit[card.suit] += 1
	
	for suit in numSuit:
		if numSuit[suit] >= 5:
			return True

	return False


def haveStraight(hole_card, community_card):
	haveRank = {}
	for rank in range(1, 14):
		haveRank[rank] = 0
	for card in hole_card + community_card:
		haveRank[card.rank] = 1
		if card.rank == 14:
			haveRank[1] = 1

	# Look for chain of 5
	chain = 0
	for rank in haveRank:
		if haveRank[rank] == 0:
			chain = 0
		else:
			chain += haveRank[rank]
		if chain == 5:
			return True

	return False

def haveStraightFlush(hole_card, community_card):
	return haveFlush(hole_card, community_card) and haveStraight(hole_card, community_card)

print(haveStraight(hole_card, community_card))
print(haveFlush(hole_card, community_card))
print(haveStraightFlush(hole_card, community_card))