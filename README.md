# Pinochle AI Tutor

An AI-powered tutor to help beginners learn and improve their Pinochle game skills.

## Project Overview

This project implements an AI tutor that assists Pinochle players by providing:
- Bid recommendations based on hand analysis
- Card tracking for trumps, aces, and counter cards
- Strategic play suggestions

## Features

- Command-line interface for game interaction
- Real-time bid suggestions
- Card tracking system
- Basic play recommendations
- Game state monitoring

## Setup

1. Ensure you have Python 3.8+ installed
2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the program:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main entry point of the program
- `game/`: Core game logic
  - `card.py`: Card representation and deck management
  - `hand.py`: Hand management and evaluation
  - `game_state.py`: Game state tracking
- `ai/`: AI components
  - `bidder.py`: Bidding strategy implementation
  - `player.py`: Play recommendation system
- `utils/`: Utility functions and constants

## Author

Brooke Simpson (A02335559) 
