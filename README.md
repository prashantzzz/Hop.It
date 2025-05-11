# Hop.It Game
Fully AI generated using prompt engineering in Cursor.
A vertical platformer game where the player jumps on platforms to reach higher and achieve a better score. Test your reflexes and timing as you navigate increasingly difficult platforms, beating the high score each time!
Have a score boost by using the Jetpack tht appears occasionally.

### Find all the prompts, AI generated content in [GamePrompt.docx](https://github.com/prashantzzz/Hop.It/blob/main/GamePrompt.docx) file, and Video walkthrough [Hopit.mp4](https://github.com/prashantzzz/Hop.It/blob/main/Hop.It.mp4) file in the repository.
<a href="https://prashantzz.itch.io/hopit">
  <img src="https://github.com/prashantzzz/Hop.It/blob/main/Hop.It.gif?raw=true" alt="Hop It Gameplay" width="400"/>
</a>

## Requirements

- Python 3.x
- Pygame library (`pip install pygame`)
- For online multiplayer: `websockets` and `asyncio` libraries
  ```bash
  pip install websockets
  ```

## How To Play (3 ways)
### [Try it here](https://prashantzz.itch.io/hopit) - Requires reload after game ends

### Using exe to run it as GUI (Best & simple way)

1. Download the dist.zip fle from [release](https://github.com/prashantzzz/Hop.It/releases/tag/Hop.It)
2. Unzip it then go to dist/main/main.exe
3. Run the .exe file

### Cloning

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
- **Online Mode Controls**: Use mouse to navigate menus, create/join rooms, and start games

## Game Mechanics

### Core Gameplay
- The player automatically jumps when landing on platforms
- The objective is to climb as high as possible without falling
- Score increases based on height reached
- The game ends if the player falls below the bottom of the screen
- **Online multiplayer mode**: Compete against another player in real-time to see who can reach the highest score

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

## Online Multiplayer

### Features
- Real-time multiplayer through WebSocket connections
- Create your own room or join an existing one using a room code
- See opponent's score in real-time during gameplay
- Win/lose detection based on height and player status
- Clean disconnection handling

### How to Play Online
1. Click the "Online" button on the home screen
2. Create a new room or enter an existing room code
3. Wait for an opponent to join (if creating a room) or connect to an existing room
4. Press "Start" when both players are ready
5. Compete to reach the highest score - if you fall, you'll immediately see if you've won or lost!

### Technical Details
- Uses a WebSocket server hosted at wss://hop-it-server.onrender.com
- Real-time data synchronization between players
- Proper error handling for connection issues

## Future Improvements

- Additional platform types with special effects
- More power-ups and collectibles
- Multiple character options
- Difficulty settings
- Additional online game modes and features
 
