from typing import List
from game.card import Card, Suit, Rank
from game.hand import Hand
import math

class BidHelper:
    def __init__(self, hand: Hand):
        self.hand = hand

    def remaining_deck(self) -> list:
        """Generate the remaining deck after the player's hand is removed"""
        full_deck = self.create_full_deck()  # Create a full deck of cards
        remaining = [card for card in full_deck if card not in self.hand.cards]
        return remaining

    def create_full_deck(self) -> list:
        """Creates a full deck of 48 cards (2 copies of each card)"""
        suits = [Suit.CLUBS, Suit.DIAMONDS, Suit.HEARTS, Suit.SPADES]
        ranks = [Rank.ACE, Rank.TEN, Rank.KING, Rank.QUEEN, Rank.JACK]
        deck = [Card(suit, rank) for suit in suits for rank in ranks for _ in range(2)]  # 2 of each card
        return deck

    def calculate_hypergeometric_probability(self, needed_cards: list, total_cards_needed: int) -> float:
        """Calculate the probability that the partner has the necessary meld cards"""
        remaining_deck = self.remaining_deck()
        total_remaining = len(remaining_deck)

        # Count how many of the needed cards are in the remaining deck
        remaining_needed = [card for card in needed_cards if card in remaining_deck]

        # If the number of needed cards is more than the remaining, probability is 0
        if len(remaining_needed) < total_cards_needed:
            return 0.0

        # Calculate hypergeometric probability
        # Number of ways to choose the needed cards
        needed_combinations = math.comb(len(remaining_needed), total_cards_needed)
        # Number of ways to choose the remaining cards
        remaining_combinations = math.comb(total_remaining - len(remaining_needed), 12 - total_cards_needed)
        # Total number of ways to choose 12 cards from the remaining deck
        total_combinations = math.comb(total_remaining, 12)

        # Hypergeometric probability
        probability = (needed_combinations * remaining_combinations) / total_combinations
        return probability
    
    def closest_family_suits(self):
        missing_cards_per_suit = []

        for suit in Suit:
            family_cards = [Card(suit, rank) for rank in [Rank.ACE, Rank.TEN, Rank.KING, Rank.QUEEN, Rank.JACK]]
            missing = [card for card in family_cards if card not in self.hand.cards]
            missing_cards_per_suit.append(missing)

        return missing_cards_per_suit

    def create_bid_hand(self, trump: Suit, needed_cards: List[Card]) -> int:
        # Start with an empty hand
        bid_hand = Hand()

        # Add all Aces in hand
        for card in self.hand.cards:
            if card.rank == Rank.ACE:
                bid_hand.add_card(card)
        
        # Add all cards of trump suit
        for card in self.hand.cards:
            if card.suit == trump:
                bid_hand.add_card(card)
        
        # Add the Jack of Diamonds if trump is Spades
        if trump == Suit.SPADES:
            for card in self.hand.cards:
                if card.suit == Suit.DIAMONDS and card.rank == Rank.JACK:
                    bid_hand.add_card(card)
        
        # Add the Queen of Spades if trump is Diamonds
        if trump == Suit.DIAMONDS:
            for card in self.hand.cards:
                if card.suit == Suit.SPADES and card.rank == Rank.QUEEN:
                    bid_hand.add_card(card)
        
        # Add all the needed cards
        for card in needed_cards:
            bid_hand.add_card(card)

        bid_hand.add_meld_def(trump)

        # Calculate the melds for the new hand
        total_points = bid_hand.evaluate_melds()

        return total_points
    

    def estimate_tricks(self, hand_cards: List[Card], trump_suit: Suit) -> int:
        """Estimate the number of tricks the player is likely to win."""
        # Start with a base score of 250
        estimated_tricks = 250
        
        # Group cards by suit
        suit_cards = {suit: [] for suit in Suit}
        
        for card in hand_cards:
            suit_cards[card.suit].append(card)
        
        # Loop over each suit that is not trump
        for suit, cards in suit_cards.items():
            if suit == trump_suit:
                continue  # Skip trump suit
            
            # Identify loose cards (non-trump cards that don't have an Ace to back them up)
            non_ace_cards = [card for card in cards if card.rank != Rank.ACE]
            ace_cards = [card for card in cards if card.rank == Rank.ACE]
            
            # For each non-ace card, check if it has an Ace to back it up
            loosers = 0
            for card in non_ace_cards:
                if not any(ace_card.suit == card.suit for ace_card in ace_cards):
                    loosers += 1
            
            # Subtract 10 for each looser
            estimated_tricks -= 10 * loosers
        
        # Ensure the estimated tricks do not go below zero
        return max(estimated_tricks, 0)
