# Dungeon Explorer

A simple, procedurally generated dungeon exploration game built with Python and PgZero (Pygame Zero).

## Game Overview

Dungeon Explorer is a grid-based adventure game where you navigate a procedurally generated dungeon, avoid patrolling enemies, and search for the golden exit. Each round increases in difficulty with more enemies and new dungeon layouts. Explore new areas to earn points and survive as long as possible!

## Features

- Procedurally generated dungeons with rooms and corridors
- Animated player and enemy sprites
- Enemy patrol territories (highlighted in red)
- Health, score, and round tracking
- Audio support for music and sound effects (toggleable)
- Multiple rounds with increasing difficulty
- Simple, responsive controls

## Controls

- **Move:** Arrow keys or WASD
- **Menu/Back:** Click the "Menu" button
- **Start/Continue:** Use mouse to click buttons
- **Restart after Game Over:** Press `Space`
- **Next Round:** Press `Space` after completing a round
- **Toggle Music/Sound:** Use the main menu buttons

## How to Play

1. Use the arrow keys or WASD to move your character through the dungeon.
2. Avoid enemies and their patrol territories (red borders).
3. Explore new areas to earn points.
4. Find the golden exit to complete the round and advance.
5. Survive as long as possible—each round adds more enemies!

## Requirements

- Python 3.7+
- [Pygame Zero (pgzero)](https://pygame-zero.readthedocs.io/en/stable/)
- Pygame

## Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd oa
   ```
2. Install dependencies:
   ```bash
   pip install pgzero pygame
   ```

## Running the Game

1. Ensure you are in the project directory (`oa`).
2. Run the game with PgZero:
   ```bash
   pgzrun main.py
   ```

## Assets

- Place your sound effects in the `sounds/` directory (e.g., `click.wav`, `step.wav`, `hit.wav`).
- Place your background music in the `music/` directory (e.g., `background_music.mp3`).
- Sprite images are in the `images/` directory.

## Notes

- The game will automatically check for required audio files and directories.
- For best experience, play with audio enabled.

## License

MIT License
