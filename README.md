# Qix-Game
Overview

This is a Pygame-based implementation of a classic arcade-style game inspired by Qix. The goal is to claim at least 20% of the play area by drawing and enclosing territories while avoiding enemies.

Features

Classic Qix-style gameplay: Draw lines to capture territory while dodging enemies.

Dynamic enemy AI: Sparx move along borders, and Qix moves freely inside the play area.

Multiple Game States: Instructions, Play, Pause, and Game Over screens.

Territory tracking: Displays percentage of claimed area.

Lives system: Lose a life if caught by enemies while drawing lines.

Controls

Arrow Keys: Move along the perimeter or when not drawing.

Spacebar: Start/stop drawing lines to capture territory.

ESC: Pause the game.

Enter: Restart after game over.

How to Play

Move along the border using arrow keys.

Press Spacebar to start drawing and claim territory.

Complete a closed shape to capture the enclosed area.

Avoid touching the enemies:

Sparx (Orange Circles): Patrol the border.

Qix (Purple Circle): Moves randomly inside the play area.

If an enemy touches you while drawing, you lose a life.

Capture at least 20% of the play area to complete the level.

Installation & Running the Game

Prerequisites

Ensure you have Python installed. You also need pygame:

pip install pygame

Running the Game

python qix_game.py

Game Screens

Main Menu

Start: Begin a new game.

Instructions: Learn how to play.

Exit: Quit the game.

Pause Menu

Resume: Continue playing.

Main Menu: Return to the main menu.

Exit Game: Quit the game.

Game Over Screen

Displays the percentage of the area captured.

Press Enter to restart or ESC to quit.

Future Improvements

Additional levels with increasing difficulty.

Power-ups and special abilities.

Enhanced enemy AI.

More visual effects and animations.

License

This project is for educational and personal use. Feel free to modify and expand it!

Credits

Developed using Pygame as part of a programming project.
