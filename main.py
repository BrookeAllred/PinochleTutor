#!/usr/bin/env python3

from game.card import Card, Deck, Suit
from game.hand import Hand
from game.game_state import GameState
from ai.player import Player
from ai.bidHelper import BidHelper
from ai.bidder import Bidder
from ai.helperFunctions import *
import random


def main():
    print("\033[94mWelcome to the Pinochle AI Tutor!\033[0m")
    print("\033[92mThis program will help you learn and improve your Pinochle game.\033[0m")
    
    user_input = input("Type 'info' to read the basics on how to play Pinochle, or press Enter to skip to playing: ").strip().lower()

    if user_input == "info":
        print_pinochle_rules()
        input("\nPress Enter to start the game...")
    else:
        print("\nSkipping rules... Let's get started!\n")
    
    # Initialize game components
    deck = Deck()
    game_state = GameState()
    player = Player()

    start_new_game(deck, game_state, player)
    
def start_new_game(deck: Deck, game_state: GameState, player: Player):
    print("\n\033[94mYou are Player 0. Player 2 is your partner. \nStarting a new game...\033[0m")
    print("\033[92mFirst, we'll deal the cards...\033[0m")
    input("Press Enter to continue...")
    
    # Reset game state
    game_state.__init__()
    deck.shuffle()
        
    # Deal hands (3 cards at a time until each player has 12)
    for _ in range(4):  
        game_state.player_hands.append(Hand())  # Initialize hands

    for _ in range(4):  # 4 rounds of dealing
        for hand in game_state.player_hands:
            for card in deck.draw_hand(3):
                hand.add_card(card)
    
    print("\n\033[92mCards are passed out. Here is your hand:\033[0m")
    print("Look at your hand and evaluate if you want to bid or pass.")
    print(f"\n\033[91mBUT REMEMBER!\nIf you take the bid and don't make the points, the bid you choose will be subtracted from your score.\033[0m")
    print(game_state.player_hands[0])

    print("Don't worry, we will help you out with some stats.")

    input("\n\033[94mBefore we start the bidding phase, let's evaluate your cards.\033[0m")

    bidders = []
    for i in range(3):
        # Create bidder for each computer 
        helper = BidHelper(game_state.player_hands[i+1])
        neededCards = helper.closest_family_suits()
        
        # Find best suit based on probability
        best_suit = None
        best_prob = 0
        best_needed = None
        
        for suit, needed in zip(Suit, neededCards):
            if len(needed) <= 4:  # Only consider suits where we can get all needed cards
                prob = helper.calculate_hypergeometric_probability(needed, len(needed))
                if prob > best_prob:
                    best_prob = prob
                    best_suit = suit
                    best_needed = needed
        
        if best_suit is not None:
            # Calculate minimum bid (current meld + tricks)
            game_state.player_hands[i+1].add_meld_def(best_suit)
            min_meld = game_state.player_hands[i+1].evaluate_melds()
            min_tricks = helper.estimate_tricks(game_state.player_hands[i+1].cards, best_suit)
            min_bid = min_meld + min_tricks
            
            # Calculate maximum bid (potential meld + tricks with needed cards)
            max_meld = helper.create_bid_hand(best_suit, best_needed)
            temp_hand = game_state.player_hands[i+1].cards + best_needed
            max_tricks = helper.estimate_tricks(temp_hand, best_suit)
            max_bid = max_meld + max_tricks
            
            # Generate bid based on probability
            # If probability is 50% or higher, bias towards higher bids
            if best_prob >= 0.5:
                # Use a triangular distribution favoring higher bids
                # The higher the probability, the more we favor the max bid
                bid_range = max_bid - min_bid
                # Scale probability to be between 0.5 and 1.0 for high probability cases
                scaled_prob = 0.5 + (best_prob - 0.5) * 0.5
                # Generate bid with bias towards max_bid
                bid = int(min_bid + bid_range * (1 - (1 - scaled_prob) ** 2))
            else:
                # For lower probabilities, be more conservative
                # Scale probability to be between 0 and 0.5
                scaled_prob = best_prob * 0.5
                # Generate bid with bias towards min_bid
                bid = int(min_bid + (max_bid - min_bid) * scaled_prob)
            

            if bid > 250:
                bidders.append(Bidder(bid, best_suit))
            else:
                bidders.append(Bidder(250, best_suit))

        else:
            bid = 0     
            bidders.append(Bidder(250, Suit.CLUBS))   


    helper = BidHelper(game_state.player_hands[0])
    neededCards = helper.closest_family_suits()

    # Create a summary string for later use
    suit_summary = ""

    # Loop through the suits in the enum
    for suit, needed in zip(Suit, neededCards):
        print(f"\n\033[93mAnalyzing {suit.value}  :\033[0m")
        if len(needed) > 4:
            print(f"\033[91mFor {suit.value}   you need more than 4 cards to get a family. Your partner can only pass 4 cards. It would be hard to make a high bid in this suit without a family.\033[0m")
            suit_summary += f"{suit.value}  : Need more than 4 cards\n"
        elif len(needed) == 0:
            print(f"\033[92mFor {suit.value}  , you already have all the cards needed for a family!\033[0m")
            suit_summary += f"{suit.value}  : Have all needed cards\n"
        else:
            likely = helper.calculate_hypergeometric_probability(needed, len(needed))
            print(f"\033[94mLikelihood of getting the cards you need in {suit.value}  is {likely * 100:.2f}%\033[0m")
            print(f"You are missing {needed}")
            suit_summary += f"{suit.value}  : {likely * 100:.2f}% - Missing {needed}\n"
            print(f"\nIf you went into this suit and didn't get any cards here is what will happen...")
            game_state.player_hands[0].add_meld_def(suit)
            meld = game_state.player_hands[0].evaluate_melds()
            print(f"The most you can make on your current meld is {meld}")
            tricks = helper.estimate_tricks(game_state.player_hands[0].cards, suit)
            print(f"We calculate the tricks you will be able to win will total {tricks} points.")
            print(f"\nTherefore the lowest bid we suggest you bid is {meld + tricks}")
            print()

            print("\nIf you went into this suit and got all the cards you need, here is what will happen...")
            meld = helper.create_bid_hand(suit, needed)
            print(f"The most you can make on your current meld is {meld}")
            temp = game_state.player_hands[0].cards + needed
            tricks = helper.estimate_tricks(temp, suit)
            print(f"We calculate the tricks you will be able to win will total {tricks} points.")
            print(f"We will add 40 points for potential points your partner will make in Meld \n(This is just a set number, not a calculation.)")
            print(f"\nTherefore the largest bid we suggest you bid is {meld + tricks + 40}. \nBut remember there is only a {likely * 100:.2f}% chance that you will get this!")

            print()

        input("\nPress Enter to continue to next suit...")

    print("\n________________________________________________________________________________")
    print("\n\033[94mBidding Phase:\033[0m")

    user_input = input("Type 'info' to read the basics on how Meld works, or press Enter to skip to bidding: ").strip().lower()

    if user_input == "info":
        print_meld_phase_rules()
        input("\nPress Enter to start the game...")

    # Take random number for who will open
    current_player = random.randint(0, 3)

    print("\n\033[94mA random number was picked to choose who will open.\033[0m")
    print("Usually this is the person to the left of the dealer.")
    current_bid = 250
    passes = {0: False, 1: False, 2: False, 3: False}

    if current_player == 0:
        print("\033[92mYou were randomly picked to open.\033[0m")
    print(f"\n\033[93mPlayer {current_player} has to open at 250\033[0m")
    game_state.place_bid(current_player, current_bid)
    input("\nPress Enter to continue with bidding...")

    while list(passes.values()).count(True) < 3:
        current_player = (current_player + 1) % 4

        if passes[current_player]:
            continue

        if current_player == 0:
            print("\n\033[92mYour turn to bid.\033[0m")
            print(f"\033[94mCurrent bid: {current_bid}\033[0m")
            print("\033[92mYour hand:\033[0m")
            print(game_state.player_hands[current_player])
            if game_state.winning_bidder == 2:
                print(f"\n\033[92mYour partner Player 2 currently has the bid at {current_bid}.\033[0m")
            else:
                print(f"\n\033[91mPlayer {game_state.winning_bidder} currently has the bid at {current_bid}.\033[0m")

            while True:
                bid_input = input("\nEnter your bid (or 'pass'): ").lower()
                if bid_input == 'pass':
                    passes[current_player] = True
                    print("\033[91mYou passed.\033[0m")
                    input("\nPress Enter to continue...")
                    break

                try:
                    bid = int(bid_input)
                except ValueError:
                    print("\033[91mInvalid input. Please enter a number or 'pass'.\033[0m")
                    continue

                if bid < current_bid + 10:
                    print(f"\033[91mBid must be at least {current_bid + 10}\033[0m")
                    continue

                if game_state.place_bid(current_player, bid):
                    current_bid = bid
                    break
                else:
                    print("\033[91mInvalid bid. Please try again.\033[0m")
                    continue

        elif current_player == 2:
            print(f"\n\033[92mPlayer {current_player}'s turn to bid (your partner)\033[0m")
            input("Press Enter to see their bid...")
            bid_input = bidders[current_player - 1].get_next_bid(current_bid)

            if bid_input == 'pass':
                passes[current_player] = True
                print(f"\n\033[91mPlayer {current_player} passed. \n(Remember, this is your partner—losing the bid gives it to the other team.)\033[0m")
                input("\nPress Enter to continue...")
                continue

            bid = int(bid_input)
            if bid < current_bid + 10:
                print(f"\033[91mPlayer {current_player} attempted to bid below {current_bid + 10}. Passing instead.\033[0m")
                passes[current_player] = True
                input("\nPress Enter to continue...")
                continue

            if game_state.place_bid(current_player, bid):
                current_bid = bid
                print(f"\n\033[92mPlayer {current_player} placed a bid of {current_bid}.\033[0m")
                input("\nPress Enter to continue...")
            else:
                print(f"\033[91mError with Player {current_player}'s bid\033[0m")

        else:
            print(f"\n\033[91mPlayer {current_player}'s turn to bid.\033[0m")
            input("Press Enter to see their bid...")
            bid_input = bidders[current_player - 1].get_next_bid(current_bid)

            if bid_input == 'pass':
                passes[current_player] = True
                print(f"\033[91mPlayer {current_player} passed.\033[0m")
                input("\nPress Enter to continue...")
                continue

            bid = int(bid_input)
            if bid < current_bid + 10:
                print(f"\033[91mPlayer {current_player} attempted to bid below {current_bid + 10}. Passing instead.\033[0m")
                passes[current_player] = True
                input("\nPress Enter to continue...")
                continue

            if game_state.place_bid(current_player, bid):
                current_bid = bid
                print(f"\033[91mPlayer {current_player} placed a bid of {current_bid}.\033[0m")
                input("\nPress Enter to continue...")
            else:
                print(f"\033[91mError with Player {current_player}'s bid\033[0m")

    # Announce winner
    print("\n\033[94mBidding phase complete.\033[0m")
    print(f"\033[92mPlayer {game_state.winning_bidder} wins the bid at {current_bid}.\033[0m")
    input("\nPress Enter to continue to trump selection...")

    if game_state.winning_bidder == 0:
        print(f"\n\033[92mCongratulations, you won the bid!\033[0m")
        print("\033[91mBut now comes the hard part. You need to be careful, if you don't make your bid it will now be subtracted from your score.\033[0m")
        print("For a reminder, here is what you need to do in each suit:")
        print(suit_summary)
        input("\nPress Enter to select trump...")
        
        # Trump selection
        print("\n\033[93mTrump Selection:\033[0m")
        print("0. ♠️  Spades")
        print("1. ♥️  Hearts")
        print("2. ♣️  Clubs")
        print("3. ♦️  Diamonds")
        
        while True:
            try:
                trump_choice = int(input("\nSelect trump suit (0-3): "))
                if 0 <= trump_choice <= 3:
                    game_state.set_trump(list(Suit)[trump_choice])
                    break
                print("\033[91mInvalid choice. Please try again.\033[0m")
            except ValueError:
                print("\033[91mPlease enter a number between 0 and 3\033[0m")
 
    elif game_state.winning_bidder == 2:
        print(f"\n\033[92mCongratulations, your partner won the bid. In this situation it's now your job to back them up!\033[0m")
        input("\nPress Enter to see what trump suit they chose...")
        game_state.set_trump(bidders[1].best_suit)
    else:
        print("\n\033[91mSadly the other team won the bid, your job now is to get as many points as you can and try to stop the other team from making their bid.\033[0m")
        input("\nPress Enter to see what trump suit they chose...")
        game_state.set_trump(bidders[game_state.winning_bidder - 1].best_suit)

    print(f"\n\033[93mTrump suit chosen is {game_state.trump_suit.value}\033[0m")
    input("\nPress Enter to continue to the trading phase...")

    # Put Trump for each hand
    game_state.player_hands[0].add_meld_def(game_state.trump_suit)
    game_state.player_hands[1].add_meld_def(game_state.trump_suit)
    game_state.player_hands[2].add_meld_def(game_state.trump_suit)
    game_state.player_hands[3].add_meld_def(game_state.trump_suit)

    print("\n________________________________________________________________________________")
    print("\n\033[94mTrading Phase:\033[0m")

    user_input = input("Type 'info' to read the basics tips and tricks on trading, or press Enter to skip to trading: ").strip().lower()

    if user_input == "info":
        print_passing_rules()
        input("Press Enter to begin trading...")

    if game_state.winning_bidder == 0:
        # Player 2 passes to Player 0 (user)
        print("\n\033[92mWaiting for your partner's cards...\033[0m")
        input("Press Enter to see what cards they're passing you...")
        
        cards = choose_cards_to_pass(game_state.player_hands[2], game_state.trump_suit)
        print("\n\033[92mYour partner (Player 2) is passing you these cards:\033[0m")
        for card in cards:
            print(f"  - {card}")
            game_state.player_hands[2].remove_card(card)
            game_state.player_hands[0].add_card(card)

        input("\nPress Enter to see your updated hand...")
        print("\n\033[92mYour hand after receiving partner's cards:\033[0m")
        print(game_state.player_hands[0])
        
        # Recommend cards to pass back
        recommended = choose_cards_to_pass_back(game_state.player_hands[0], game_state.trump_suit)
        print("\n\033[92m--- Now it's your turn to pass back cards ---\033[0m")
        cards = prompt_user_to_pass_cards(game_state.player_hands[0], recommended)
        for card in cards:
            game_state.player_hands[0].remove_card(card)
            game_state.player_hands[2].add_card(card)

    elif game_state.winning_bidder == 2:
        # Player 0 (user) passes cards to Player 2
        recommended = choose_cards_to_pass(game_state.player_hands[0], game_state.trump_suit)
        print("\n\033[92m--- Your partner won the bid ---\033[0m")
        print("\033[92m--- Choose cards to pass to your partner (Player 2) ---\033[0m")
        cards = prompt_user_to_pass_cards(game_state.player_hands[0], recommended)
        for card in cards:
            game_state.player_hands[0].remove_card(card)
            game_state.player_hands[2].add_card(card)

        print("\n\033[92mWaiting for your partner's cards...\033[0m")
        input("Press Enter to see what cards they're passing back...")

        # Partner (Player 2) sends cards back
        cards = choose_cards_to_pass_back(game_state.player_hands[2], game_state.trump_suit)
        print("\n\033[92mYour partner is passing these cards back to you:\033[0m")
        for card in cards:
            print(f"  - {card}")
            game_state.player_hands[2].remove_card(card)
            game_state.player_hands[0].add_card(card)

        print("\n\033[92mYour final hand after trading:\033[0m")
        print(game_state.player_hands[0])
        input("\nPress Enter to continue...")

    elif game_state.winning_bidder == 3:
        print("\n\033[91mPlayers 1 and 3 are trading cards...\033[0m")
        input("Press Enter to continue...")
        # Player 1 passes cards to player 3
        cards = choose_cards_to_pass(game_state.player_hands[1], game_state.trump_suit)
        for card in cards:
            game_state.player_hands[1].remove_card(card)
            game_state.player_hands[3].add_card(card)

        cards = choose_cards_to_pass_back(game_state.player_hands[3], game_state.trump_suit)
        for card in cards:
            game_state.player_hands[3].remove_card(card)
            game_state.player_hands[1].add_card(card)
    elif game_state.winning_bidder == 1:
        print("\n\033[91mPlayers 1 and 3 are trading cards...\033[0m")
        input("Press Enter to continue...")
        # Player 3 passes cards to player 1
        cards = choose_cards_to_pass(game_state.player_hands[3], game_state.trump_suit)
        for card in cards:
            game_state.player_hands[3].remove_card(card)
            game_state.player_hands[1].add_card(card)

        cards = choose_cards_to_pass_back(game_state.player_hands[1], game_state.trump_suit)
        for card in cards:
            game_state.player_hands[1].remove_card(card)
            game_state.player_hands[3].add_card(card)

    print("\n________________________________________________________________________________")
    print("\n\033[94mMeld Phase:\033[0m")
    input("Press Enter to count your meld...")

    points = game_state.player_hands[0].evaluate_melds()
    print("\n\033[92mLet's count your meld:\033[0m ")

    for meld in game_state.player_hands[0].melds:
        name, points, cards = meld
        print(f"\t\033[93m{name.name.capitalize()}:\033[0m")
        print(f"\t{cards} for {points} points.\n")
    
    print(f"\t\033[92mTotal: {game_state.player_hands[0].meldPoints}\033[0m")
    input("\nPress Enter to see Player 1's meld...")

    print("\n\033[91mNow let's total Player 1's meld:\033[0m")
    points = game_state.player_hands[1].evaluate_melds()

    for meld in game_state.player_hands[1].melds:
        name, points, cards = meld
        print(f"\t\033[93m{name.name.capitalize()}:\033[0m")
        print(f"\t{cards} for {points} points.\n")
    
    print(f"\t\033[91mTotal: {game_state.player_hands[1].meldPoints}\033[0m")
    input("\nPress Enter to see Player 2's meld...")

    print("\n\033[92mNow let's total Player 2's meld:\033[0m")
    points = game_state.player_hands[2].evaluate_melds()

    for meld in game_state.player_hands[2].melds:
        name, points, cards = meld
        print(f"\t\033[93m{name.name.capitalize()}:\033[0m")
        print(f"\t{cards} for {points} points.\n")
    
    print(f"\t\033[92mTotal: {game_state.player_hands[2].meldPoints}\033[0m")
    input("\nPress Enter to see Player 3's meld...")

    print("\n\033[91mNow let's total Player 3's meld:\033[0m")
    points = game_state.player_hands[3].evaluate_melds()

    for meld in game_state.player_hands[3].melds:
        name, points, cards = meld
        print(f"\t\033[93m{name.name.capitalize()}:\033[0m")
        print(f"\t{cards} for {points} points.\n")
    
    print(f"\t\033[91mTotal: {game_state.player_hands[3].meldPoints}\033[0m")
    input("\nPress Enter to begin playing tricks...")

    print("\n________________________________________________________________________________")
    print("\n\033[94mPlaying Phase:\033[0m")

    user_input = input("Type 'info' to read the basics on how Playing Phase works, or press Enter to skip to Playing: ").strip().lower()

    if user_input == "info":
        print_card_play_rules()

    cardsLeft = Deck()
    # Initialize cardsLeft with all cards in the deck
    # We'll remove cards as they're played

    def view_remaining_cards():
        print("\n\033[94mRemaining cards in play:\033[0m")
        print("\033[93mTrump suit:\033[0m", game_state.trump_suit.value)
        print("\n\033[94mCards by suit:\033[0m")
        for suit in Suit:
            suit_cards = [card for card in cardsLeft.cards if card.suit == suit]
            if suit_cards:
                print(f"{suit.value}  : {suit_cards}")
            else:
                print(f"{suit.value}  : None")
        
        print("\n\033[94mTricks won:\033[0m")
        print(f"\033[92mYour team (Players 0 & 2):\033[0m {game_state.tricks_won[0]}")
        print(f"\033[91mOpponent team (Players 1 & 3):\033[0m {game_state.tricks_won[1]}")

        # Calculate tricks needed based on who won the bid
        if game_state.winning_bidder in [0, 2]:  # Your team won the bid
            your_meld = game_state.player_hands[0].meldPoints + game_state.player_hands[2].meldPoints
            your_tricks_needed = (game_state.current_bid - your_meld) // 10
            print(f"\n\033[92mYour team needs {your_tricks_needed} more tricks to make your bid of {game_state.current_bid}\033[0m")
        else:  # Opponent team won the bid
            their_meld = game_state.player_hands[1].meldPoints + game_state.player_hands[3].meldPoints
            their_tricks_needed = (game_state.current_bid - their_meld) // 10
            print(f"\n\033[91mOpponent team needs {their_tricks_needed} more tricks to make their bid of {game_state.current_bid}\033[0m")

        input("\nPress Enter to continue...")

    # Start with the winning bidder
    current_player = game_state.winning_bidder
    print(f"\n\033[93mPlayer {current_player} leads the first trick.\033[0m")
    input("Press Enter to begin...")
    
    round = 0

    # Continue until all cards are played
    while any(len(hand.cards) > 0 for hand in game_state.player_hands):
        round += 1
        print(f"\n\033[94mRound {round}:\033[0m")
        input("Press Enter to start this round...")
        
        # Clear the current trick
        game_state.current_trick = []

        for i in range(4):
            player_idx = (current_player + i) % 4
            hand = game_state.player_hands[player_idx]
            game_state.current_player = player_idx

            valid_cards = [card for card in hand.cards if game_state.is_valid_play(card)]

            if not valid_cards:
                print(f"\033[91mPlayer {player_idx} has no valid cards! Skipping turn.\033[0m")
                continue

            if player_idx == 0:
                print("\n\033[92mYour turn! Choose a card to play:\033[0m")
                print("\nYour hand:")
                for idx, card in enumerate(hand.cards):
                    print(f"{idx + 1}. {card}")
                
                while True:
                    try:
                        choice = input("\nEnter the number of the card to play (or 'view' to see remaining cards): ")
                        if choice.lower() == 'view':
                            view_remaining_cards()
                            print("\n\033[92mYour turn! Choose a card to play:\033[0m")
                            print("\nYour hand:")
                            for idx, card in enumerate(hand.cards):
                                print(f"{idx + 1}. {card}")
                            continue
                        choice = int(choice) - 1
                        if 0 <= choice < len(hand.cards):
                            selected_card = hand.cards[choice]
                            if selected_card in valid_cards:
                                card = selected_card
                                break
                            else:
                                print(f"\033[91mInvalid choice. {selected_card} cannot be played right now. Please choose a valid card.\nYou must follow lead suit. If you don't have lead suit you must trump. \nOnly when you don't have lead suit or trump can you play anything.\033[0m")
                        else:
                            print(f"\033[91mPlease enter a number between 1 and {len(hand.cards)}.\033[0m")
                    except ValueError:
                        print("\033[91mInvalid input. Please enter a number or 'view'.\033[0m")
            else:
                if player_idx == 2:
                    print(f"\n\033[92mPlayer {player_idx}'s turn (your partner)...\033[0m")
                else:
                    print(f"\n\033[91mPlayer {player_idx}'s turn...\033[0m")
                input("Press Enter to see their play...")
                card = cardPlay(valid_cards, game_state.current_trick, game_state.played_cards, game_state.trump_suit, (game_state.winning_bidder % 2 == player_idx % 2))

            hand.remove_card(card)
            game_state.play_card(card)
            cardsLeft.remove_card(card)  # Remove the card from cardsLeft when it's played

            if player_idx in [0, 2]:
                print(f"\033[92mPlayer {player_idx} played {card}\033[0m")
            else:
                print(f"\033[91mPlayer {player_idx} played {card}\033[0m")
            if player_idx != 0:
                input("Press Enter to continue...")

        # Determine trick winner
        winner = game_state.get_trick_winner(current_player)
        if winner in [0, 2]:
            print(f"\n\033[92mPlayer {winner} won the trick!\033[0m")
        else:
            print(f"\n\033[91mPlayer {winner} won the trick!\033[0m")
        game_state.complete_trick(winner)
        current_player = winner

        if len(game_state.player_hands[0].cards) > 0:
            input("\nPress Enter to see your remaining cards...")
            print("\n\033[92mYour remaining cards:\033[0m")
            print(game_state.player_hands[0])
            input("\nPress Enter to continue to next trick...")

    print("\n________________________________________________________________________________")
    print("\n\033[94mGame Over!\033[0m")
    input("Press Enter to see the final scores...")

    yourPoints = game_state.tricks_won[0] * 10
    if yourPoints > 0:
        yourPoints += game_state.player_hands[0].meldPoints + game_state.player_hands[2].meldPoints
    enemyPoints = game_state.tricks_won[1] * 10
    if enemyPoints > 0:
        enemyPoints += game_state.player_hands[1].meldPoints + game_state.player_hands[3].meldPoints

    print(f"\n\033[92mYour Score: {yourPoints}\033[0m")
    print(f"\033[91mEnemy Score: {enemyPoints}\033[0m")
    print("\n\033[94mThank you for playing!\033[0m")


# def practice_bidding(deck: Deck, bidder: Bidder):
#     print("\nStarting bidding practice...")
    

# def practice_card_play(deck: Deck, player: Player):
#     print("\nStarting card play practice...")


def print_pinochle_rules():
    print("\033[96m" + "=" * 50)
    print("            HOW TO PLAY PINOCHLE")
    print("=" * 50 + "\033[0m")
    
    print("\n\033[93mObjective:\033[0m")
    print("  Score points by forming 'melds' and by taking tricks during the play phase.")
    
    print("\n\033[93mPlayers:\033[0m")
    print("  4 players in two teams. Teammates sit across from each other.")

    print("\n\033[93mDeck:\033[0m")
    print("  48 cards: two copies each of 9, 10, J, Q, K, A in all four suits.")

    print("\n\033[93mGame Phases:\033[0m")

    print("  1. \033[94mDealing:\033[0m")
    print("     Each player gets 12 cards, 3 at a time.")

    print("  2. \033[94mBidding:\033[0m")
    print("     Players bid for the right to choose the trump suit and trade 4 cards.")
    print("     Bids start at a minimum (like 250) and go up. Highest bidder wins.")

    print("  3. \033[94mMeld Phase:\033[0m")
    print("     Players reveal 'melds' (card combinations) worth points.")
    print("     Examples: Marriage (K+Q of trump), Runs (A-10-K-Q-J of trump), Pinochle (J♦ + Q♠).")

    print("  4. \033[94mPlay Phase:\033[0m")
    print("     Teams play tricks.")
    print("     Must follow suit if possible and if you can beat a card you have to beat (No Sluffing). Trump beats other suits.")
    print("     Ten points are earned for taking certain cards in tricks (A, 10, K).")

    print("\n\033[93mScoring:\033[0m")
    print("  - Meld Points: Earned before playing tricks.")
    print("  - Trick Points: Earned during play phase.")
    print("  - Must meet your bid or you go set (lose points).")

    print("\n\033[93mWinning:\033[0m")
    print("  First team to reach the target score (usually 1500) wins.")
    print("  But for this game we will only play a single round for practice.")

    print("\n\033[96m" + "=" * 50)
    print("          ENJOY PLAYING PINOCHLE!")
    print("=" * 50 + "\033[0m")


def print_meld_phase_rules():
    print("\033[96m" + "=" * 50)
    print("            MELD PHASE: PLACING DOWN")
    print("=" * 50 + "\033[0m")

    print("\n\033[93mOverview:\033[0m")
    print("  After bidding, the winning team selects the trump suit.")
    print("  Then, players reveal combinations of cards called \033[92mmelds\033[0m to earn points.")
    print("  Only the team that wins the bid scores their melds.")

    print("\n\033[93mMeld Types and Point Values:\033[0m")

    melds = [
        ("Nine of Trump", 10, "One 9 in the trump suit"),
        ("Marriage (non-trump)", 20, "King + Queen of the same suit (non-trump)"),
        ("Marriage in Trump", 40, "King + Queen of the trump suit"),
        ("Pinochle", 40, "Queen of Spades + Jack of Diamonds"),
        ("Polygamy", 40, "Two Kings + Two Queens of the trump suit"),
        ("Four Jacks Around", 40, "One Jack of each suit"),
        ("Four Queens Around", 60, "One Queen of each suit"),
        ("Four Kings Around", 80, "One King of each suit"),
        ("Four Aces Around", 100, "One Ace of each suit"),
        ("Family (Trump Run)", 150, "A-10-K-Q-J all in the trump suit"),
        ("Four Marriages", 240, "One Marriage (K+Q) in each suit"),
        ("Double Pinochle", 300, "2x Queen of Spades + 2x Jack of Diamonds"),
        ("Eight Jacks Around", 400, "Two of each Jack in all four suits"),
        ("Eight Queens Around", 600, "Two of each Queen in all four suits"),
        ("Eight Kings Around", 800, "Two of each King in all four suits"),
        ("Eight Aces Around", 1000, "Two of each Ace in all four suits"),
        ("Double Family", 1500, "2x each A-10-K-Q-J in the trump suit"),
    ]

    for name, points, desc in melds:
        print(f"  - \033[94m{name:<20}\033[0m ... {points} points :: {desc}")

    print("\n\033[93mMeld Rules:\033[0m")
    print("  - Meld cards can count in multiple melds if valid.")
    print("  - You cannot reuse a card in the same type of meld (e.g., two Marriages with the same Queen).")
    print("  - Both partners meld is totaled in the calculation of meld points.")

    print("\n\033[93mStrategy Tips:\033[0m")
    print("  - Melds in the trump suit score more and often help in trick-taking.")
    print("  - Some melds like Double Family or Eight Aces are very rare but score huge!")


    print("\n\033[96m" + "=" * 50)
    print("          END OF MELD PHASE INSTRUCTIONS")
    print("=" * 50 + "\033[0m")


def print_passing_rules():
    print("\033[96m" + "=" * 50)
    print("               PASSING PHASE RULES")
    print("=" * 50 + "\033[0m")

    print("\n\033[93mWho Passes:\033[0m")
    print("  - Only the team that \033[92mwins the bid\033[0m can pass cards.")
    print("  - The \033[92mbid winner selects the trump suit\033[0m.")
    print("  - Their \033[92mpartner passes 4 cards first\033[0m, taking the chosen trump into account.")
    print("  - After receiving these 4 cards, the \033[92mbid winner returns 4 cards\033[0m back to their partner.")

    print("\n\033[93mTips for Passing to the Bid Winner:\033[0m")
    print("  - \033[94m1.\033[0m Prioritize cards that help complete a Family (A-10-K-Q-J of trump).")
    print("  - \033[94m2.\033[0m Next, pass Aces—especially one from each suit for extra melds.")
    print("  - \033[94m3.\033[0m If stuck, and trump is Diamonds or Spades, pass a Queen of Spades + Jack of Diamonds to try for a Pinochle.")
    print("  - \033[94m4.\033[0m Avoid breaking up your own melds unless it clearly benefits your partner.")

    print("\n\033[93mTips for Passing Back as the Bid Taker:\033[0m")
    print("  - \033[94m1.\033[0m Try to shape your hand into only \033[92mtwo suits\033[0m (not counting Aces).")
    print("     Aces of other suits \033[3mdon’t ruin a two-suited hand\033[0m.")
    print("  - \033[94m2.\033[0m Keep all cards in the trump suit—including Nines!")
    print("     (A Nine of trump beats an Ace of any non-trump suit.)")
    print("  - \033[94m3.\033[0m Pass Kings and Queens from non-trump suits to give your partner potential Marriages.")

    print("\n\033[93mPassing Summary:\033[0m")
    print("  - \033[92mPartner passes 4 cards first.\033[0m")
    print("  - \033[92mBid taker receives cards, selects best hand, and passes back 4 cards.\033[0m")

    print("\n\033[96m" + "=" * 50)
    print("            END OF PASSING PHASE RULES")
    print("=" * 50 + "\033[0m")




def print_card_play_rules():
    print("\033[95m" + "=" * 60)
    print("                CARD PLAY PHASE RULES")
    print("=" * 60 + "\033[0m")

    print("\n\033[93m🎯 Goal:\033[0m")
    print("  - Win tricks containing \033[92mAces (A), Tens (10), and Kings (K)\033[0m.")
    print("  - If \033[94myou took the bid\033[0m, \033[1mcontrol the round\033[0m and pull trump early.")
    print("  - If \033[94myour partner took the bid\033[0m, support their control.")
    print("  - If the other team took the bid, \033[91msteal control\033[0m and try to win at least one trick.")
    print("    \033[1;91m⚠️ If you win 0 tricks, your meld score is lost.\033[0m")

    print("\n\033[93m🃏 How Play Works:\033[0m")
    print("  - The first card played sets the \033[94mleading suit\033[0m.")
    print("  - You must \033[1mfollow suit\033[0m if possible, and \033[1;94mbeat\033[0m the highest card if you can.")
    print("  - If you can’t follow suit:")
    print("    - You must \033[92mplay trump\033[0m if you have it.")
    print("    - If you have no trump, play any card.")

    print("\n\033[93m👑 Winning the Trick:\033[0m")
    print("  - If trump is played: highest trump wins.")
    print("  - Otherwise: highest card in the leading suit wins.")

    print("\n\033[93m🤔 Strategy Tips:\033[0m")
    print("  - Bid winner: lead trump early to \033[1;92mdraw out opponents' trump\033[0m.")
    print("  - Partner: don't overplay your best cards unless necessary.")
    print("  - Opponent: \033[91msave trump and high cards\033[0m unless you can take control.")
    print("  - Track which suits have been played and try to void yourself in suits to use trump strategically.")

    print("\n\033[93m📘 Example Trick:\033[0m")
    print("  Trump suit is \033[92mHearts\033[0m.")
    print("  You're last to play. Here's the trick so far:")
    print("    Player 1 (Lead): \033[94m10♠\033[0m")
    print("    Player 2: \033[94mK♠\033[0m")
    print("    Player 3: \033[91m9♥\033[0m (Trumped)")

    print("\n  Your Hand: A♠, Q♠, Q♥, 10♦")
    print("\033[93m  What should you play?\033[0m")
    print("    → The lead suit is ♠ (Spades). You have A♠, so \033[1;92mplay it to try and beat K♠\033[0m.")
    print("    However, Player 3 already trumped, so your A♠ \033[1;91mwon't win\033[0m.")
    print("    → Best play: \033[94mQ♠\033[0m — a low card in the lead suit since you can't win.")

    print("\n\033[95m" + "=" * 60)
    print("              END OF CARD PLAY PHASE RULES")
    print("=" * 60 + "\033[0m")
    

if __name__ == "__main__":
    main() 