from pypokerengine.utils.card_utils import gen_cards
from pypokerengine.engine.card import Card

hole_card = gen_cards(['HQ', 'D3'])
community_card = gen_cards(['DA', 'D2', 'CQ', 'D5', 'D4'])

class DecomposedCards:
	def __init__(self, hole_card, community_card):
		self.hole_card = hole_card
		self.community_card = community_card

		# Count suits
		self.num_suits = {}
		self.suit_high = {}
		self.hole_card_num_suits = {}
		self.hole_card_suit_high = {}
		self.comm_card_num_suits = {}
		self.comm_card_suit_high = {}
		for suit_num in Card.SUIT_MAP.keys():
			self.num_suits[suit_num] = 0
			self.suit_high[suit_num] = 0
			self.hole_card_num_suits[suit_num] = 0
			self.hole_card_suit_high[suit_num] = 0
			self.comm_card_num_suits[suit_num] = 0
			self.comm_card_suit_high[suit_num] = 0

		for card in hole_card:
			self.num_suits[card.suit] += 1
			self.hole_card_num_suits[card.suit] += 1
			if card.rank > self.suit_high[suit_num]:
				self.suit_high[suit_num] = card.rank
			if card.rank > self.hole_card_suit_high[suit_num]:
				self.hole_card_suit_high[suit_num] = card.rank

		for card in community_card:
			self.num_suits[card.suit] += 1
			self.comm_card_num_suits[card.suit] += 1
			if card.rank > self.suit_high[suit_num]:
				self.suit_high[suit_num] = card.rank
			if card.rank > self.comm_card_suit_high[suit_num]:
				self.comm_card_suit_high[suit_num] = card.rank

		# Count ranks
		self.num_rank = {}
		for rank in range(1, 15):
			self.num_rank[rank] = 0
		for card in hole_card + community_card:
			self.num_rank[card.rank] += 1
			if card.rank == 14:
				self.num_rank[1] += 1

	# Highest rank in a flush
	def flushStrength(self):
		for suit in self.num_suits:
			if self.num_suits[suit] >= 5:
				return self.suit_high[suit]
		return 0

	# Quick estimate number of possible flushes
	def possibleFlushes(self):
		count = 0
		for suit in self.comm_card_num_suits:
			if self.comm_card_num_suits[suit] >= 3:
				# Estimate number of flushes higher than the one we have, if we have any
				if self.num_suits[suit] >= 5:
					count += 13 - self.suit_high[suit]
				# If we don't have any, count all possible flushes
				else:
					count += 13 - self.num_suits[suit]
		return count

	# Highest rank in a straight
	def straightStrength(self):
		# Look for chain of 5
		chain = 0
		for rank in self.num_rank:
			if self.num_rank[rank] == 0:
				chain = 0
			else:
				chain += self.num_rank[rank]
			if chain == 5:
				return rank
		return 0

	def haveStraightFlush(self):
		return int(self.flushStrength() > 0 and self.straightStrength() > 0)

cards = DecomposedCards(hole_card, community_card)

print(cards.straightStrength())
print(cards.flushStrength())
print(cards.haveStraightFlush())