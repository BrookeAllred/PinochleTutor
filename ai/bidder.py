from typing import List, Tuple
from game.card import Card, Suit
from game.hand import Hand
import random

class Bidder:
    def __init__(self, maxBid, best_suit=None):
        self.minimum_bid = 250
        self.bid_increment = 10
        self.max_bid = maxBid
        self.best_suit = best_suit
    
    def get_next_bid(self, current_bid: int) -> str:
        """
        Determine if the bidder should bid or pass based on current bid and max bid.
        Returns either a string of the next bid amount or 'pass'.
        """
        # If current bid is already at or above max bid, always pass
        if current_bid >= self.max_bid:
            return "pass"
            
        # Calculate how close we are to max bid (0.0 to 1.0)
        bid_progress = (current_bid - self.minimum_bid) / (self.max_bid - self.minimum_bid)
        
        # Base probability of bidding (starts at 75% and decreases as we get closer to max bid)
        base_prob = 0.75 * (1 - bid_progress)
        
        # Add some randomness to make it less predictable
        random_factor = random.uniform(0.8, 1.2)
        final_prob = min(0.95, max(0.05, base_prob * random_factor))
        
        # Roll the dice
        if random.random() < final_prob:
            return str(current_bid + self.bid_increment)
        else:
            return "pass"