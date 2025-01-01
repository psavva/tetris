
# Retro Tetris (Python/Pygame)

A **Tetris clone** in Python using the Pygame library. This game features:

- **Classic pivot-based rotation** for each shape  
- **3D / beveled block** rendering for a retro look  
- **Soft drop** (press Down) with auto-repeat for Left/Right keys  
- **Line flash** before clearing lines  
- **Simple sine-wave beep** sounds for locking pieces and clearing lines  
- **Leveling up**: every 10 lines cleared increases the level and speeds up gameplay

## Features

1. **Pivot-based Rotation**  
   Each shape has a designated pivot cell, similar to older Tetris versions, ensuring minimal “jumping” when rotating.

2. **3D Block Rendering**  
   Blocks have highlight and shadow edges, giving a 3D or “beveled” look.

3. **Soft Drop**  
   Holding the Down arrow accelerates the falling speed. Releasing it restores normal speed.

4. **Line Flash & Clear**  
   Completed lines briefly flash white, then get removed.

5. **Leveling System**  
   Every 10 lines raised increases the level, which speeds up falling pieces.

6. **Retro Beeps**  
   - **Lock** beep when a piece lands  
   - **Line-clear** beep when lines are removed

## Installation

1. **Clone or Download** this repository:
   ```bash
   git clone https://github.com/YourUsername/RetroTetris.git
   cd RetroTetris
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Game**:
   ```bash
   python tetris.py
   ```

## Requirements

- Python 3.7+  
- [Pygame](https://www.pygame.org/)  
- [NumPy](https://numpy.org/) for generating the beep waveforms  

The exact packages and versions are listed in [requirements.txt](./requirements.txt).

## Controls

- **Left/Right Arrow**: Move the falling piece horizontally (auto-repeat if held)  
- **Up Arrow**: Rotate the piece 90° clockwise around its pivot  
- **Down Arrow**: Soft drop (accelerate falling)  
- **Close the window**: Ends the game

## License

Distributed under the [MIT License](LICENSE) (or whichever license you choose). Feel free to modify as you wish.

## Contributing

1. Fork or clone this repository  
2. Create a new branch for your feature or bug fix  
3. Submit a pull request with a clear explanation of changes

Enjoy this retro Tetris clone! If you encounter any issues, please open a GitHub issue or submit a pull request.