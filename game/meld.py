from typing import List, Dict
from .card import Card, Suit, Rank
from enum import Enum

class MeldType(Enum):
    NINE = "Nine of Trump"
    MARRIAGE = "Marriage"
    TRUMPMARRAGE = "Marrage of Trump"
    POLYGAMY = "Extra King or Queen in Family"
    PINOCHLE = "Pinochle"
    FOURJACKS = "Jack of Each Suit"
    FOURQUEENS = "Queen of each Suit"
    FOURKINGS = "King of each Suit"
    FOURACES = "Ace of each Suit"
    FAMILY = "Family"
    FOURMARRIAGE = "Marriage of each Suit"
    DOUBLEPINOCHLE = "Double Pinochle"
    EIGHTJACKS = "Two Jacks of each Suit"
    EIGHTQUEENS = "Two Queens of each Suit"
    EIGHTKINGS = "Two Kings of each Suit"
    EIGHTACES = "Two Aces of each Suit"
    DOUBLEFAMILY = "Double Family"


    

class MeldDefinition:
    def __init__(self, meld_type: MeldType, combinations: List[List[Card]], points: int):
        self.meld_type = meld_type
        self.combinations = combinations
        self.points = points

    def matches(self, hand: List[Card], trump_suit: Suit = None):
        for combo in self.combinations:
            if self._combo_matches(combo, hand, trump_suit):
                return True
        return False

    def _combo_matches(self, combo: List[Card], hand: List[Card], trump_suit: Suit = None):
        for card in combo:
            # Special logic for trump-based melds
            if self.meld_type in [MeldType.NINE, MeldType.TRUMPMARRAGE]:
                if card.rank == Rank.NINE and trump_suit and card.suit != trump_suit:
                    return False
                if self.meld_type == MeldType.TRUMPMARRAGE and trump_suit and card.suit != trump_suit:
                    return False
            # Check if card exists in hand
            if hand.count(card) < combo.count(card):
                return False
        return True


# Define melds
