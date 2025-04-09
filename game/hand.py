from typing import List, Dict
from .card import Card, Suit, Rank
from enum import Enum
from .meld import MeldDefinition, MeldType

    # self.points: Dict[str, int] = {
    #         "Nine of Trump" : 10,
    #         "Nontrump Marrage" : 20,
    #         "Trump Marrage" : 40,
    #         "Polygamy" : 40,
    #         "Pinochle" : 40,
    #         "Jack of Each Suit" : 40,
    #         "Queen of Each Suit" : 60,
    #         "King of Each Suit" : 80,
    #         "Ace of Each Suit" : 100,
    #         "Family" : 150,
    #         "Marrage of Each Suit": 240,
    #         "Double Pinochle" : 300,
    #         "2 Jacks of Each Suit" : 400,
    #         "2 Queens of Each Suit" : 600,
    #         "2 Kings of Each Suit" : 800,
    #         "2 Aces of Each Suit" : 1000,
    #         "Double Family" : 1500
    #     }
    
    
class Hand:
    def __init__(self):
        self.cards: List[Card] = []
        self.meld_definitions = [
        ]
        
        self.melds = []
            
        self.meldPoints = 0
    
    def add_card(self, card: Card) -> None:
        """Add a card to the hand."""
        self.cards.append(card)
        self._sort_cards()
    
    def remove_card(self, card: Card) -> bool:
        """Remove a card from the hand."""
        if card in self.cards:
            self.cards.remove(card)
            return True
        return False
    
    def add_meld_def(self, trump: Suit):
        
        self.meld_definitions = [
            MeldDefinition(
                MeldType.NINE,
                combinations=[[Card(trump, Rank.NINE)]],
                points=10
            ),
            
            MeldDefinition(
                MeldType.MARRIAGE,
                combinations=[[Card(suit, Rank.KING), Card(suit, Rank.QUEEN)] for suit in Suit if suit != trump],
                points=20
            ),

            MeldDefinition(
                MeldType.TRUMPMARRAGE,
                combinations = [[Card(trump, Rank.KING), Card(trump, Rank.QUEEN)]],
                points=40
            ),

            MeldDefinition(
                MeldType.PINOCHLE,
                combinations=[[Card(Suit.SPADES, Rank.QUEEN), Card(Suit.DIAMONDS, Rank.JACK)]],
                points=40
            ),

            MeldDefinition(
                MeldType.POLYGAMY,
                combinations=[[Card(trump, Rank.KING), Card(trump, Rank.KING)], [Card(trump, Rank.QUEEN), Card(trump, Rank.QUEEN)]],
                points=40
            ),

            MeldDefinition(
                MeldType.FOURJACKS,
                combinations=[[Card(s, Rank.JACK) for s in Suit]],
                points=40
            ),

            MeldDefinition(
                MeldType.FOURQUEENS,
                combinations=[[Card(s, Rank.QUEEN) for s in Suit]],
                points=60
            ),

            MeldDefinition(
                MeldType.FOURKINGS,
                combinations=[[Card(s, Rank.KING) for s in Suit]],
                points=80
            ),
            
            MeldDefinition(
                MeldType.FOURACES,
                combinations=[[Card(s, Rank.ACE) for s in Suit]],
                points=100
            ),
            
            MeldDefinition(
                MeldType.FAMILY,
                combinations=[[Card(trump, Rank.ACE), Card(trump, Rank.TEN), Card(trump, Rank.KING),
                            Card(trump, Rank.QUEEN), Card(trump, Rank.JACK)]],
                points=150
            ),
            
            MeldDefinition(
                MeldType.FOURMARRIAGE,
                combinations=[
                    [Card(Suit.SPADES, Rank.KING), Card(Suit.SPADES, Rank.QUEEN),
                    Card(Suit.HEARTS, Rank.KING), Card(Suit.HEARTS, Rank.QUEEN),
                    Card(Suit.CLUBS, Rank.KING), Card(Suit.CLUBS, Rank.QUEEN),
                    Card(Suit.DIAMONDS, Rank.KING), Card(Suit.DIAMONDS, Rank.QUEEN)]
                ],
                points=240
            ),

            MeldDefinition(
                MeldType.DOUBLEPINOCHLE,
                combinations=[[Card(Suit.SPADES, Rank.QUEEN), Card(Suit.DIAMONDS, Rank.JACK),
                            Card(Suit.SPADES, Rank.QUEEN), Card(Suit.DIAMONDS, Rank.JACK)]],
                points=300
            ),
            
            MeldDefinition(
                MeldType.EIGHTJACKS,
                combinations=[[Card(s, Rank.JACK) for _ in range(2) for s in Suit]],
                points=400
            ),
            
            MeldDefinition(
                MeldType.EIGHTQUEENS,
                combinations=[[Card(s, Rank.QUEEN) for _ in range(2) for s in Suit]],
                points=600
            ),
            
            MeldDefinition(
                MeldType.EIGHTKINGS,
                combinations=[[Card(s, Rank.KING) for _ in range(2) for s in Suit]],
                points=800
            ),
            
            MeldDefinition(
                MeldType.EIGHTACES,
                combinations=[[Card(s, Rank.ACE) for _ in range(2) for s in Suit]],
                points=1000
            ),
            
            MeldDefinition(
                MeldType.DOUBLEFAMILY,
                combinations=[[Card(trump, Rank.ACE), Card(trump, Rank.ACE), 
                            Card(trump, Rank.TEN), Card(trump, Rank.TEN),
                            Card(trump, Rank.KING), Card(trump, Rank.KING),
                            Card(trump, Rank.QUEEN), Card(trump, Rank.QUEEN),
                            Card(trump, Rank.JACK), Card(trump, Rank.JACK)]],
                points=1500
            ),]
    
    def _sort_cards(self) -> None:
        """Sort cards by suit and rank."""
        # Define suit order (Spades, Hearts, Clubs, Diamonds)
        suit_order = {Suit.SPADES: 0, Suit.HEARTS: 1, Suit.CLUBS: 2, Suit.DIAMONDS: 3}
        
        # Define rank order (Ace, Ten, King, Queen, Jack, Nine)
        rank_order = {Rank.ACE: 0, Rank.TEN: 1, Rank.KING: 2, 
                     Rank.QUEEN: 3, Rank.JACK: 4, Rank.NINE: 5}
        
        # Sort cards first by suit, then by rank
        self.cards.sort(key=lambda card: (suit_order[card.suit], rank_order[card.rank]))

    def evaluate_melds(self):
        melds_found = []
        total_points = 0

        # Track suit-wise cards
        suit_map = {suit: [] for suit in Suit}
        for card in self.cards:
            suit_map[card.suit].append(card)

        # Track what melds are already added
        meld_types_found = set()

        for definition in self.meld_definitions:
            if definition.meld_type in [MeldType.POLYGAMY, MeldType.TRUMPMARRAGE, MeldType.FAMILY, MeldType.DOUBLEFAMILY, MeldType.PINOCHLE, MeldType.DOUBLEPINOCHLE]:
                continue  # We'll handle these special cases after the loop

            for combo in definition.combinations:
                if all(self.cards.count(card) >= combo.count(card) for card in combo):
                    melds_found.append([definition.meld_type, definition.points, combo])
                    meld_types_found.add(definition.meld_type)
                    total_points += definition.points
                    break  # Only one instance per meld type (for now)

        # --- Handle special conditional melds ---

        # Check if DOUBLEPINOCHLE exists
        double_pinochle_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.DOUBLEPINOCHLE), None)
        if double_pinochle_def and all(self.cards.count(card) >= double_pinochle_def.combinations[0].count(card) for card in double_pinochle_def.combinations[0]):
            melds_found.append([MeldType.DOUBLEPINOCHLE, double_pinochle_def.points, double_pinochle_def.combinations[0]])
            meld_types_found.add(MeldType.DOUBLEPINOCHLE)
            total_points += double_pinochle_def.points
        else:
            # Check for PINOCHLE only if no DOUBLEPINOCHLE
            pinochle_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.PINOCHLE), None)
            if pinochle_def and all(self.cards.count(card) >= pinochle_def.combinations[0].count(card) for card in pinochle_def.combinations[0]):
                melds_found.append([MeldType.PINOCHLE, pinochle_def.points, pinochle_def.combinations[0]])
                meld_types_found.add(MeldType.PINOCHLE)
                total_points += pinochle_def.points

        # Check if DOUBLEFAMILY exists
        double_family_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.DOUBLEFAMILY), None)
        if double_family_def and all(self.cards.count(card) >= double_family_def.combinations[0].count(card) for card in double_family_def.combinations[0]):
            melds_found.append([MeldType.DOUBLEFAMILY, double_family_def.points, double_family_def.combinations[0]])
            meld_types_found.add(MeldType.DOUBLEFAMILY)
            total_points += double_family_def.points
        else:
            # Check for FAMILY only if no DOUBLEFAMILY
            family_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.FAMILY), None)
            if family_def and all(self.cards.count(card) >= family_def.combinations[0].count(card) for card in family_def.combinations[0]):
                melds_found.append([MeldType.FAMILY, family_def.points, family_def.combinations[0]])
                meld_types_found.add(MeldType.FAMILY)
                total_points += family_def.points

        # Add TRUMPMARRAGE only if neither FAMILY nor DOUBLEFAMILY were added
        if MeldType.FAMILY not in meld_types_found and MeldType.DOUBLEFAMILY not in meld_types_found:
            trump_marriage_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.TRUMPMARRAGE), None)
            if trump_marriage_def:
                for combo in trump_marriage_def.combinations:
                    if all(self.cards.count(card) >= combo.count(card) for card in combo):
                        melds_found.append([MeldType.TRUMPMARRAGE, trump_marriage_def.points, combo])
                        meld_types_found.add(MeldType.TRUMPMARRAGE)
                        total_points += trump_marriage_def.points
                        break

        # Add POLYGAMY only if FAMILY or DOUBLEFAMILY exists
        if MeldType.FAMILY in meld_types_found or MeldType.DOUBLEFAMILY in meld_types_found:
            polygamy_def = next((m for m in self.meld_definitions if m.meld_type == MeldType.POLYGAMY), None)
            if polygamy_def:
                for combo in polygamy_def.combinations:
                    if all(self.cards.count(card) >= combo.count(card) for card in combo):
                        melds_found.append([MeldType.POLYGAMY, polygamy_def.points, combo])
                        meld_types_found.add(MeldType.POLYGAMY)
                        total_points += polygamy_def.points
                        break

        self.melds = melds_found
        self.meldPoints = total_points
        return total_points

    
    def closest_family_suits(self):
        missing_cards_per_suit = []

        for suit in Suit:
            family_cards = [Card(suit, rank) for rank in [Rank.ACE, Rank.TEN, Rank.KING, Rank.QUEEN, Rank.JACK]]
            missing = [card for card in family_cards if card not in self.cards]
            missing_cards_per_suit.append(missing)

        return missing_cards_per_suit
    
    def edit_hand(self, action: str, card: Card) -> bool:
        """Edit the player's hand by adding or removing a card.
        
        action: "add" to add the card to the hand, "remove" to remove the card.
        card: the Card object to add or remove.
        Returns True if the action is successful, False otherwise.
        """
        if action == "add":
            if card not in self.cards:
                self.cards.append(card)
                self.cards.sort(key=lambda c: (Suit.ORDER[c.suit], Rank.ORDER[c.rank]))  # Keep cards sorted
                return True
            return False  # Card is already in the hand, so no action

        elif action == "remove":
            if card in self.cards:
                self.cards.remove(card)
                return True
            return False  # Card isn't in the hand to remove

        return False  # Invalid action




    def __str__(self) -> str:
        """Return a string representation of the hand with cards sorted and indexed."""
        return "\n".join(f"{i:2d}:\t{card.suit.value}  {card.rank}" for i, card in enumerate(self.cards)) 