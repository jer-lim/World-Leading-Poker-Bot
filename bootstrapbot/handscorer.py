import sys

class HoleCards():
  def __init__(self, rank1, rank2, suited):
    self.rank1 = rank1
    self.rank2 = rank2
    self.suited = suited

  def __str__(self):
    output = ""
    if self.rank1 == 10: output += "T"
    elif self.rank1 == 11: output += "J"
    elif self.rank1 == 12: output += "Q"
    elif self.rank1 == 13: output += "K"
    elif self.rank1 == 14: output += "A"
    else: output += str(self.rank1)

    if self.rank2 == 10: output += "T"
    elif self.rank2 == 11: output += "J"
    elif self.rank2 == 12: output += "Q"
    elif self.rank2 == 13: output += "K"
    elif self.rank2 == 14: output += "A"
    else: output += str(self.rank2)

    if self.suited: output += "s"
    else: output += "o"
    return output

class HandScorer():
  def score_hole_cards(self, hole_cards):
    hand = self.__parse_hole_cards(hole_cards)
    print(hand)
  
  def __parse_hole_cards(self, hole_cards):
    suit1, rank1 = self.__parse_card(hole_cards[0])
    suit2, rank2 = self.__parse_card(hole_cards[1])
    if suit1 == suit2:
      suited = True
    else:
      suited = False

    if rank1 > rank2:
      return HoleCards(rank1, rank2, suited)
    else:
      return HoleCards(rank2, rank1, suited)
      
  def __parse_card(self, card):
    suit = card[0]
    rank = card[1]
    if rank == 'T':
      rank = 10
    elif rank == 'J':
      rank = 11
    elif rank == 'Q':
      rank = 12
    elif rank == 'K':
      rank = 13
    elif rank == 'A':
      rank = 14
    return suit, int(rank)