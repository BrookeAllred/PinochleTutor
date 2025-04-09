from typing import List
from collections import defaultdict
from game.card import Card, Suit, Rank
from game.hand import Hand
import random

from collections import defaultdict
from typing import List
from game.card import Card, Suit, Rank


def prompt_user_to_pass_cards(hand, recommended_cards):
    print("\nYour hand:")
    for i, card in enumerate(hand.cards):
        print(f"{i}: {card}")
    
    print("\nWe recommend passing these cards:")
    for card in recommended_cards:
        print(f"  - {card}")
    
    print("\nEnter the indices of 4 cards to pass (separated by spaces):")
    while True:
        try:
            indices = list(map(int, input("> ").strip().split()))
            if len(indices) != 4:
                print("Please enter exactly 4 indices.")
                continue
            selected = [hand.cards[i] for i in indices]
            return selected
        except (ValueError, IndexError):
            print("Invalid input. Make sure you enter 4 valid indices from your hand.")


def choose_cards_to_pass(hand: List[Card], trump_suit: Suit) -> List[Card]:
    to_pass = []
    hand_copy = hand.cards[:]  # Shallow copy of the list of cards

    def try_add(condition):
        nonlocal to_pass
        for card in list(hand_copy):  # Make a copy for safe removal
            if condition(card):
                to_pass.append(card)
                hand_copy.remove(card)
                if len(to_pass) == 4:
                    return True
        return False

    # 1. Pass trump Ace if available
    if try_add(lambda c: c.rank == Rank.ACE and c.suit == trump_suit): return to_pass

    # 2. Pass other high-ranked trump cards (Ace is already handled)
    for rank in [Rank.TEN, Rank.KING, Rank.QUEEN, Rank.JACK]:
        if try_add(lambda c, r=rank: c.rank == r and c.suit == trump_suit): return to_pass


    # 3. Pass other Aces from non-trump suits
    ace_suits = [suit for suit in Suit if suit != trump_suit]
    for suit in ace_suits:
        if try_add(lambda c, s=suit: c.rank == Rank.ACE and c.suit == s): 
            return to_pass

    # 4. Any other Aces not yet passed
    if try_add(lambda c: c.rank == Rank.ACE and c.suit != trump_suit): return to_pass

    # 5. If trump is Diamonds, pass Queen of Spades
    if trump_suit == Suit.DIAMONDS:
        if try_add(lambda c: c.rank == Rank.QUEEN and c.suit == Suit.SPADES): return to_pass

    # 6. If trump is Spades, pass Jack of Diamonds
    if trump_suit == Suit.SPADES:
        if try_add(lambda c: c.rank == Rank.JACK and c.suit == Suit.DIAMONDS): return to_pass

    # 7. Nine of trump
    if try_add(lambda c: c.rank == Rank.NINE and c.suit == trump_suit): return to_pass

    # 8. If trump is Diamonds, Jack of Spades
    if trump_suit == Suit.DIAMONDS:
        if try_add(lambda c: c.rank == Rank.JACK and c.suit == Suit.SPADES): return to_pass

    # 9. If trump is Spades, Nine of Diamonds
    if trump_suit == Suit.SPADES:
        if try_add(lambda c: c.rank == Rank.NINE and c.suit == Suit.DIAMONDS): return to_pass

    # 10. If trump is Diamonds, Nine of Spades
    if trump_suit == Suit.DIAMONDS:
        if try_add(lambda c: c.rank == Rank.NINE and c.suit == Suit.SPADES): return to_pass

    # 11. If trump is Diamonds, King of Spades
    if trump_suit == Suit.DIAMONDS:
        if try_add(lambda c: c.rank == Rank.KING and c.suit == Suit.SPADES): return to_pass

    # 12. Pass whatever is left of one suit (avoid trump), keeping kings/queens if possible
    # Group by suit
    suits = defaultdict(list)
    for card in hand_copy:
        suits[card.suit].append(card)

    # Sort suits by number of cards (try to unload short suits)
    suit_order = sorted(suits.items(), key=lambda item: len(item[1]))

    for suit, cards in suit_order:
        if suit == trump_suit:
            continue
        # Prefer to drop non-face cards first
        sorted_cards = sorted(cards, key=lambda c: (c.rank in [Rank.KING, Rank.QUEEN], c.rank.value))
        for card in sorted_cards:
            to_pass.append(card)
            hand_copy.remove(card)
            if len(to_pass) == 4:
                return to_pass

    # Final fallback: drop anything
    for card in hand_copy:
        to_pass.append(card)
        if len(to_pass) == 4:
            return to_pass

    return to_pass


def choose_cards_to_pass_back(hand: Hand, trump: Suit) -> List[Card]:
    cards_to_consider = hand.cards.copy()
    suit_counts = defaultdict(list)

    for card in cards_to_consider:
        suit_counts[card.suit].append(card)

    # Helper: get counts ignoring suits that only have Aces
    def effective_suits():
        return {
            suit: [c for c in cards if c.rank != Rank.ACE]
            for suit, cards in suit_counts.items()
        }

    # Try to reduce to two effective suits
    non_ace_suits = effective_suits()
    if len([cards for cards in non_ace_suits.values() if cards]) > 2:
        suits_by_count = sorted(non_ace_suits.items(), key=lambda x: len(x[1]))
        cards_to_pass = []
        for suit, cards in suits_by_count:
            for card in suit_counts[suit]:
                if card.rank != Rank.ACE:  # Never pass Aces
                    cards_to_pass.append(card)
                    if len(cards_to_pass) == 4:
                        return cards_to_pass
        # If we still couldn't get 4, fallback to rules

    to_pass = []

    # Helper function to add a card if it's not an Ace and not already added
    def try_add(condition):
        nonlocal to_pass
        for card in list(cards_to_consider):  # Safe copy of list to allow removal
            if condition(card):
                to_pass.append(card)
                cards_to_consider.remove(card)  # Remove from the original list
                if len(to_pass) == 4:
                    return True
        return False

    # 1. Pass trump Aces first
    if try_add(lambda c: c.rank == Rank.ACE and c.suit == trump):
        return to_pass[:4]

    # 2. Pass Aces from non-trump suits (try to balance)
    ace_suits = [suit for suit in Suit if suit != trump]
    for suit in ace_suits:
        if try_add(lambda c, s=suit: c.rank == Rank.ACE and c.suit == s): 
            return to_pass[:4]

    # 3. Non-trump, non-Ace cards
    for card in cards_to_consider:
        if card.suit != trump and card.rank != Rank.ACE:
            try_add(lambda c: c == card)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # 4. Non-trump 10s without Ace in that suit
    for suit in Suit:
        if suit == trump:
            continue
        ten = Card(suit, Rank.TEN)
        if ten in cards_to_consider and Card(suit, Rank.ACE) not in cards_to_consider:
            try_add(lambda c: c == ten)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # 5. Non-trump Kings without Ace or Ten in suit
    for suit in Suit:
        if suit == trump:
            continue
        king = Card(suit, Rank.KING)
        if king in cards_to_consider and Card(suit, Rank.ACE) not in cards_to_consider and Card(suit, Rank.TEN) not in cards_to_consider:
            try_add(lambda c: c == king)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # 6. Non-trump Queens (special rule for Q♠ + J♦ when trump is ♦)
    for suit in Suit:
        if suit == trump:
            continue
        queen = Card(suit, Rank.QUEEN)
        if queen in cards_to_consider:
            if trump == Suit.DIAMONDS and suit == Suit.SPADES:
                if Card(Suit.DIAMONDS, Rank.JACK) in cards_to_consider:
                    continue
            try_add(lambda c: c == queen)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # 7. Non-trump Jacks and Nines (special rule: keep J♦ if Q♠ and trump ♠)
    for suit in Suit:
        if suit == trump:
            continue
        jack = Card(suit, Rank.JACK)
        nine = Card(suit, Rank.NINE)

        if jack == Card(Suit.DIAMONDS, Rank.JACK) and trump == Suit.SPADES:
            if Card(Suit.SPADES, Rank.QUEEN) in cards_to_consider:
                continue

        if nine in cards_to_consider:
            try_add(lambda c: c == nine)
        if jack in cards_to_consider:
            try_add(lambda c: c == jack)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # 8. Trump 9s last
    trump_nine = Card(trump, Rank.NINE)
    if trump_nine in cards_to_consider:
        try_add(lambda c: c == trump_nine)
    if len(to_pass) >= 4:
        return to_pass[:4]

    # Fallback: lowest ranked non-trump, non-Ace cards
    rank_order = {Rank.ACE: 0, Rank.TEN: 1, Rank.KING: 2, Rank.QUEEN: 3, Rank.JACK: 4, Rank.NINE: 5}
    fallback = [c for c in cards_to_consider if c.suit != trump and c.rank != Rank.ACE]
    sorted_hand = sorted(fallback, key=lambda c: rank_order[c.rank])
    return sorted_hand[:4]

def cardPlay(cards, currentCards, cardsPlayed, trump, haveBid):
    def rank_value(card):
        return card.rank.value

    def is_trump(card):
        return card.suit == trump

    def all_played(card):
        return cardsPlayed.count(card) == 2

    def get_unplayed_trumps():
        all_trumps = [Card(trump, rank) for rank in Rank]
        return [card for card in all_trumps if cardsPlayed.count(card) < 2]

    def get_strongest_unplayed_trumps():
        return sorted(get_unplayed_trumps(), key=rank_value, reverse=True)

    def sort_cards_by_rank(card_list, reverse=True):
        return sorted(card_list, key=rank_value, reverse=reverse)

    # LEADING THE TRICK
    if len(currentCards) == 0:
        if haveBid:
            # Try to pull trump
            my_trumps = [c for c in cards if is_trump(c)]
            my_trumps_sorted = sort_cards_by_rank(my_trumps)

            for card in my_trumps_sorted:
                stronger_unplayed = [c for c in get_strongest_unplayed_trumps() if rank_value(c) > rank_value(card)]
                if not stronger_unplayed:
                    return card  # No stronger trump left
                if all_played(Card(card.suit, Rank.ACE)) or card.rank == Rank.ACE:
                    return card  # Play Ace or weaker trump if stronger Aces are gone

            # No safe trumps to pull – play all your aces
            aces = [c for c in cards if c.rank == Rank.ACE and not is_trump(c)]
            if aces:
                return aces[0]

            # Play Queen, then Jack, then Nine, then King
            for rank in [Rank.QUEEN, Rank.JACK, Rank.NINE, Rank.KING]:
                choice = next((c for c in cards if c.rank == rank), None)
                if choice:
                    return choice

            # If nothing else, play a random card
            return random.choice(cards)

        else:
            # You don't have the bid, try to play high card in a suit where all higher cards have been played
            for suit in Suit:
                suit_cards = [c for c in cards if c.suit == suit and not is_trump(c)]
                if not suit_cards:
                    continue
                suit_cards_sorted = sort_cards_by_rank(suit_cards)
                for card in suit_cards_sorted:
                    higher_ranks = [r for r in Rank if r.value > card.rank.value]
                    if all(Card(suit, r) in cardsPlayed for r in higher_ranks):
                        return card

            # Otherwise play any non-trump card
            non_trumps = [c for c in cards if not is_trump(c)]
            if non_trumps:
                return random.choice(non_trumps)

            return random.choice(cards)

    # NOT LEADING
    else:
        partner_index = (len(currentCards) + 1) % 4 == 3  # Assume 4 players, partner is opposite
        if partner_index:
            partner_card = currentCards[0]
            winning_card = currentCards[0]
            for card in currentCards[1:]:
                if (card.suit == trump and winning_card.suit != trump) or \
                   (card.suit == winning_card.suit and rank_value(card) > rank_value(winning_card)):
                    winning_card = card
            
            if partner_card == winning_card:
                # Partner is currently winning the trick

                # Try to help with points (A, 10, K)
                trump_cards = [c for c in cards if is_trump(c) and c.rank in {Rank.ACE, Rank.TEN, Rank.KING}]
                if trump_cards:
                    # Play highest point-giving trump to help partner
                    return sort_cards_by_rank(trump_cards)[0]

                # No point trumps, try to give a 10 or King in another suit
                point_cards = [c for c in cards if c.rank in {Rank.TEN, Rank.KING}]
                if point_cards:
                    return sort_cards_by_rank(point_cards)[0]

                # Avoid playing Ace — keep it to cover later
                low_cards = [c for c in cards if rank_value(c) <= Rank.QUEEN.value and c.rank != Rank.ACE]
                if low_cards:
                    return sort_cards_by_rank(low_cards, reverse=False)[0]

                # Nothing else left — play lowest available card (even Ace if forced)
                return sort_cards_by_rank(cards, reverse=False)[0]

        else:
            # Try to take trick if possible
            led_suit = currentCards[0].suit
            same_suit = [c for c in cards if c.suit == led_suit]
            if same_suit:
                winning = max((c for c in currentCards if c.suit == led_suit), key=rank_value)
                # TODO: CHECK THAT WE ARE PLAYING THE LOWEST BEATABLE
                beatable = [c for c in same_suit if rank_value(c) > rank_value(winning)]
                if beatable:
                    # Play the lowest card that can beat the winning card
                    return sort_cards_by_rank(beatable)[0]
                else:
                    # Can't beat the winning card, but have same-suit cards — play the lowest
                    return sort_cards_by_rank(same_suit, reverse=False)[0]

            # *** NEW LOGIC: If can't follow suit and has trump, must trump ***
            trumps_in_hand = [c for c in cards if is_trump(c)]
            if trumps_in_hand:
                return sort_cards_by_rank(trumps_in_hand)[0]

            # Can't follow suit or trump, dump low card
            low_cards = [c for c in cards if rank_value(c) <= Rank.QUEEN.value]
            if low_cards:
                return sort_cards_by_rank(low_cards)[-1]

        # If nothing else makes sense, play a random card
        return random.choice(cards)
