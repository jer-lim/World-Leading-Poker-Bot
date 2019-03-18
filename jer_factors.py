from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

hole_card = gen_cards(['HQ', 'D3'])
community_card = gen_cards(['DA', 'D2', 'CQ', 'D5', 'D4'])

class DecomposedCards:
	def __init__(self, hole_card, community_card):
		self.hole_card = hole_card
		self.community_card = community_card

		# Count suits
		self.numSuit = {}
		self.suitHigh = {}
		for suitNum in Card.SUIT_MAP.keys():
			self.numSuit[suitNum] = 0
			self.suitHigh[suitNum] = 0
		for card in hole_card + community_card:
			self.numSuit[card.suit] += 1
			if card.rank > self.suitHigh[suitNum]:
				self.suitHigh[suitNum] = card.rank

		# Count ranks
		self.numRank = {}
		for rank in range(1, 15):
			self.numRank[rank] = 0
		for card in hole_card + community_card:
			self.numRank[card.rank] += 1
			if card.rank == 14:
				self.numRank[1] += 1

	def flushStrength(self):
		for suit in self.numSuit:
			if self.numSuit[suit] >= 5:
				return self.suitHigh[suit]
		return 0

	def straightStrength(self):
		# Look for chain of 5
		chain = 0
		for rank in self.numRank:
			if self.numRank[rank] == 0:
				chain = 0
			else:
				chain += self.numRank[rank]
			if chain == 5:
				return rank
		return 0

	def haveStraightFlush(self):
		return int(self.flushStrength() > 0 and self.straightStrength() > 0)

cards = DecomposedCards(hole_card, community_card)

print(cards.straightStrength())
print(cards.flushStrength())
print(cards.haveStraightFlush())