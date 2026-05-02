# Flappy Bird Evolutions

A simple Flappy Bird remake built with Python and `pygame`.

## Features

- Side-scrolling Flappy Bird gameplay
- Animated bird sprite
- Pipe obstacles and score tracking
- High score display
- Looping background music

## Project Structure

```text
FlappyBird/
├── FlappyBird.py
├── requirements.txt
├── images/
│   ├── background_img.png
│   ├── bird_down.jpeg
│   ├── bird_mid.png
│   ├── bird_up.jpg
│   ├── floor_img.png
│   ├── game_over.png
│   └── pipe_img.webp
└── music/
    └── FB-BG-music.mp3
```

## Requirements

- Python 3.10+
- `pip`

## Installation

1. Clone or download this project.
2. Open a terminal in the project folder.
3. Create a virtual environment:

```bash
python3 -m venv .venv
```

4. Activate the virtual environment:

```bash
source .venv/bin/activate
```

5. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run The Game

```bash
python3 FlappyBird.py
```

## Controls

- `Space` to flap
- Close the window to quit

## Music

The game loads background music from:

```text
music/FB-BG-music.mp3 - Mario Odyssey Seaside Kingdom
```

If you want to swap the soundtrack, replace that file with your own music file using the same name, or update the path in [FlappyBird.py](/Users/wilito2401/Documents/FlappyBird/FlappyBird.py:100).

## Notes

- All image assets are loaded from the `images/` folder.
- If a file is missing or renamed, the game may fail to start until the path is updated in `FlappyBird.py`.