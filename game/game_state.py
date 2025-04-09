from typing import List, Dict, Optional
from .card import Card, Suit
from .hand import Hand

class GameState:
    def __init__(self):
        self.trump_suit: Optional[Suit] = None
        self.current_bid: int = 0
        self.winning_bidder: Optional[int] = None  # Player index
        self.current_trick: List[Card] = []
        self.tricks_won: Dict[int, int] = {0: 0, 1: 0}  # Player index -> tricks won
        self.played_cards: List[Card] = []
        self.player_hands: List[Hand] = []
        self.current_player: int = 0
        self.phase: str = "bidding"  # bidding, melding, playing, scoring
    
    def set_trump(self, suit: Suit) -> None:
        """Set the trump suit for the current hand."""
        self.trump_suit = suit
    
    def place_bid(self, player: int, bid: int) -> bool:
        """Place a bid for the current hand."""
        if bid <= self.current_bid:
            return False
        self.current_bid = bid
        self.winning_bidder = player
        return True
    
    def play_card(self, card: Card) -> None:
        """Play a card in the current trick."""
        self.current_trick.append(card)
        self.played_cards.append(card)
    
    def complete_trick(self, winning_player: int) -> None:
        """Complete the current trick and award it to the winning player."""
        for trick in self.current_trick:
            if trick.rank.value == 14 or trick.rank.value == 13 or trick.rank.value == 12:
                self.tricks_won[winning_player % 2] += 1
        self.current_trick = []
        self.current_player = winning_player
    
    def get_played_cards_in_suit(self, suit: Suit) -> List[Card]:
        """Get all cards played in a specific suit."""
        return [card for card in self.played_cards if card.suit == suit]
    
    def get_remaining_cards_in_suit(self, suit: Suit) -> List[Card]:
        """Get all cards that haven't been played in a specific suit."""
        played_suits = [card.suit for card in self.played_cards]
        return [card for card in self.player_hands[self.current_player].cards 
                if card.suit == suit]
    
    def is_valid_play(self, card: Card) -> bool:
        """Check if a card is a valid play in the current trick."""
        if not self.current_trick:
            return True
        
        # Must follow suit if possible
        led_suit = self.current_trick[0].suit
        if card.suit != led_suit:
            # Check if player has any cards of the led suit
            has_led_suit = any(c.suit == led_suit for c in self.player_hands[self.current_player].cards)
            if has_led_suit:
                return False
            
            # If no led suit, check if player has trump
            has_trump = any(c.suit == self.trump_suit for c in self.player_hands[self.current_player].cards)
            if has_trump:
                # If they have trump, must play trump
                return card.suit == self.trump_suit
            
            # If no led suit and no trump, can play any card
            return True
        
        return True
    

    def get_trick_winner(self, trick_starter: int) -> Optional[int]:
        if not self.current_trick:
            return None

        # Determine trump cards
        trump_cards = [(i, card) for i, card in enumerate(self.current_trick) if card.suit == self.trump_suit]
        if trump_cards:
            # Find the trump card with the highest rank
            best_index, _ = max(trump_cards, key=lambda x: x[1].rank.value)
        else:
            # Use the first suit played
            first_suit = self.current_trick[0].suit
            suit_cards = [(i, card) for i, card in enumerate(self.current_trick) if card.suit == first_suit]
            best_index, _ = max(suit_cards, key=lambda x: x[1].rank.value)

        # Convert the index in the trick to the actual player number
        return (trick_starter + best_index) % 4
