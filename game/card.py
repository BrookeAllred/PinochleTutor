from enum import Enum
from typing import List, Optional

import random

class Suit(Enum):
    SPADES = "♠️"
    HEARTS = "♥️"
    CLUBS = "♣️"
    DIAMONDS = "♦️"
    

class Rank(Enum):
    NINE = 9
    JACK = 10
    QUEEN = 11
    KING = 12
    TEN = 13
    ACE = 14
    
    def __str__(self) -> str:
        if self == Rank.ACE:
            return "A"
        elif self == Rank.TEN:
            return "10"
        elif self == Rank.KING:
            return "K"
        elif self == Rank.QUEEN:
            return "Q"
        elif self == Rank.JACK:
            return "J"
        else:  # NINE
            return "9"

class Card:
    def __init__(self, suit: Suit, rank: Rank):
        self.suit = suit
        self.rank = rank

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.suit == other.suit and self.rank == other.rank
        return False  # If compared with something that's not a Card, return False

    def __repr__(self):
        """String representation for debugging."""
        return f"{self.suit.value}  {self.rank}"

class Deck:
    def __init__(self):
        self.cards: List[Card] = []
        self._create_deck()
    
    def _create_deck(self) -> None:
        """Create a Pinochle deck (48 cards, two of each card)."""
        self.cards = []
        for suit in Suit:
            for rank in Rank:
                # Add two of each card
                self.cards.append(Card(suit, rank))
                self.cards.append(Card(suit, rank))
    
    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def draw_card(self) -> Optional[Card]:
        """Draw a card from the top of the deck."""
        if not self.cards:
            return None
        return self.cards.pop()
    
    def draw_hand(self, num_cards: int) -> List[Card]:
        """Draw a hand of cards."""
        hand = []
        for _ in range(num_cards):
            card = self.draw_card()
            if card:
                hand.append(card)
        return hand
    
    def remove_card(self, card: Card) -> bool:
        """Remove a specific card from the deck."""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def __len__(self) -> int:
        return len(self.cards) 