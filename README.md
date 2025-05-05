# Hop.It Game
Fully AI generated using prompt engineering in Cursor.
A vertical platformer game where the player jumps on platforms to reach higher and achieve a better score. Test your reflexes and timing as you navigate increasingly difficult platforms!

## Find all the prompts, AI generated content in GamePrompt.docx file, and Video walkthrough .mp4 file in the repository.

## Requirements

- Python 3.x
- Pygame library (`pip install pygame`)

## [Try it here](https://prashantzz.itch.io/hopit)

## Using exe to run it as GUI

1. Download the dist.zip fle from release
2. Unzip it then go to dist/main/main.exe
3. Run the .exe file

## Cloning

1. Clone or download this repository.

2. Install dependencies:
   ```bash
   pip install pygame pygbag
   ```

3. Run the game as GUI using Pygame:
   ```bash
   python main.py
   ```

4. Run directly in browser:
   ```bash
   python -m pygbag .
   ```

## Game Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space**: Restart game after Game Over

## Game Mechanics

### Core Gameplay
- The player automatically jumps when landing on platforms
- The objective is to climb as high as possible without falling
- Score increases based on height reached
- The game ends if the player falls below the bottom of the screen

### Platform & Jetpack Mechanics
- Regular platforms are stationary
- Moving platforms appear after reaching 500 points
- Platforms become strategically positioned as you climb higher
- Landing on platforms gives a velocity boost upward
- **Jetpack power-up**: Appears every 500 points (after 400 points). Collect to temporarily turn into a jetpack character and get a short upward boost, crossing a few platforms. The jetpack effect ends automatically after a short duration.
- Jets move down with the camera, just like platforms

### Visual Elements
- Animated character using `jump1.png`, `jump2.png`, `jump3.png`, and `jet-char.png` for jetpack mode
- Game over screen uses a custom image (`over.png`)
- Score display at the top left, high score at the top right (always within the window)
- Simple but effective pixel art design

### Audio Features
- Background music plays during gameplay
- Level-up sound plays when beating your high score or collecting a jetpack
- Game over sound plays when you lose

## Scoring System

- Score increases proportionally to your height
- High scores are saved between game sessions in `score.txt`
- High score is displayed at the top right of the screen

## Technical Details

- Built with Python and Pygame
- Game runs at 60 FPS for smooth gameplay
- Includes collision detection and basic physics
- Scrolling camera that follows the player's ascent
- For cloning: All assets must be present in the `assets` folder:
  - `jump1.png`, `jump2.png`, `jump3.png`, `jet.png`, `jet-char.png`, `platform.png`, `bg.png`, `over.png`
  - `jump.wav`, `level-up.mp3`, `over.mp3`, `bg-music.mp3`

## Future Improvements

- Additional platform types with special effects
- More power-ups and collectibles
- Multiple character options
- Difficulty settings
 
