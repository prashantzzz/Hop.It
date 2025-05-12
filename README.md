# Hop.It Game

**Game Title**: Hop.It

**Description**: A vertical platformer game where players jump on platforms to reach higher and score more points. Features both single-player and real-time 1v1 online multiplayer mode. Test your reflexes and timing as you beat the high score or defeat your opponent in an intense vertical climb.
Catch the Jetpack on higher floors to get a temporary boost and cross a few platforms (see below attached gif).

**Theme**: Fast-paced reflex platformer

**Links**: 
   * [GitHub Zipped File](https://drive.google.com/file/d/1H_VZMBZCf7Mitfg8a5TfqWoEGp_0-9sH/)
   * [Hop.It.exe (GitHub Release)](https://github.com/prashantzzz/Hop.It/releases/download/Hop.It/Hop.It.exe)

Fully AI generated using prompt engineering in Cursor and ChatGPT. Suno AI for bg music and ElevenLabs for sound effects.

<a href="https://prashantzz.itch.io/hopit">
  <img src="https://github.com/prashantzzz/Hop.It/blob/main/Hop.It.gif?raw=true" alt="Hop It Gameplay" width="400"/>
</a>

### Find all the prompts, AI generated content in [GamePrompt.docx](https://github.com/prashantzzz/Hop.It/blob/main/GamePrompt.docx) file, and Video walkthrough [Hopit.mp4](https://github.com/prashantzzz/Hop.It/blob/main/Hop.It.mp4) file in the repository.

## Unique Features

* AI-generated visuals and gameplay concepts
* Real-time online 1v1 mode with WebSocket support
* Jetpack power-up for upward boosts
* Moving platform on higher floors for increased difficulty
* Auto-jumping mechanic
* Animated characters and cartoon-style design

## Requirements

- Python 3.x
- Pygame library (`pip install pygame`)
- For online multiplayer: `websockets` and `asyncio` libraries
  ```bash
  pip install websockets
  ```

## Installation Instructions

### Run the Standalone .exe (Simplest Way)

* Download the `.exe` directly:
   * [Hop.It.exe (GitHub Release)](https://github.com/prashantzzz/Hop.It/releases/download/Hop.It/Hop.It.exe)
* Double-click the file to launch the game.
  * ⚠️ Note: You may need to bypass the windows security warning to run the game.
  * If red window appears, click "More info" and then "Run anyway".
* No installation or Python required.

### Or Run from Source

1. Clone or download this repository.

2. Install dependencies:
   ```bash
   pip install pygame websockets asyncio pygbag
   ```

3. Run the game as GUI using Pygame:
   ```bash
   python main.py
   ```


### [Try it on itch.io](https://prashantzz.itch.io/hopit) - Doesn't support online mode
⚠️ Note: The itch.io version supports only the single-player mode. To experience the 1v1 online multiplayer mode, use the standalone `.exe` version.

## Game Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Mouse Controls**: Use mouse to navigate menus, create/join rooms, and start games

## Game Mechanics

### Core Gameplay
- The player automatically jumps when landing on platforms
- The objective is to climb as high as possible without falling
- Score increases based on height reached
- The game ends if the player falls below the bottom of the screen

### Direction to play 1V1
- Click Online button on the home screen
- Generate a room code and share it with another player and hit Play
- The other enters the code in their game and clicks Join and hits Play
- Once both players are ready, click "Start" to begin the game
- The player who reaches the highest score without falling wins

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
- Simple but effective cartoon-style design

### Audio Features
- Background music plays during gameplay
- Level-up sound plays when beating your high score or collecting a jetpack
- Game over sound plays when you lose

## Scoring System

- Score increases proportionally to your height
- High scores are saved between game sessions in `score.txt`
- High score is displayed at the top right of the screen

## Game Modes
- **Single Player**: Jump as high as possible and beat your own high score
- **Online 1v1**: Compete in real-time; whoever reaches higher and survives longer wins

## Technical Details

- Built with Python and Pygame
- Game runs at 60 FPS for smooth gameplay
- Includes collision detection and basic physics
- Scrolling camera that follows the player's ascent
- For cloning: All assets must be present in the `assets` folder:
  - `jump1.png`, `jump2.png`, `jump3.png`, `jet.png`, `jet-char.png`, `platform.png`, `bg.png`, `over.png`
  - `jump.wav`, `level-up.mp3`, `over.mp3`, `bg-music.mp3`

## Tech Stack
* Python 3.x
* Pygame
* Websockets
* Asyncio
* Pygbag

## AI Tools:
- Cursor AI (Code gen)
- ChatGPT & Leonardo AI (Game assets & images)
- SunoAI (Background music)
- ElevenLabs (Sound effects)

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

## Known Limitations
* Online mode requires stable internet
* Web version may not support `websockets` (black screen issue)
* Jetpack power-up triggers only after score threshold

## Licenses and Attributes
* Game code: MIT License
* Assets: Created using AI and open-use tools; attribution embedded in GamePrompt.docx
* Background music and SFX: Royalty-free / AI-generated

## Additional Resources
* [Hosted backend repo](https://github.com/prashantzzz/Hop.It-Server)
* [AI Prompt Log (GamePrompt.docx)](https://github.com/prashantzzz/Hop.It/blob/main/GamePrompt.docx)

## Future Improvements

- Additional platform types with special effects
- More power-ups and collectibles
- Multiple character options
- Difficulty settings
- Additional online game modes and features
