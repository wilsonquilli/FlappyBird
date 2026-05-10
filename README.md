# Flappy Bird Evolutions

`Flappy Bird Evolutions` is a multi-level Flappy Bird remake built with Python, `pygame`, and `opencv-python`. The game starts with classic Flappy Bird and gradually shifts into themed stages with new visuals, music, movement changes, and hazards.
Download the game here: wilito2401.itch.io/flappy-bird-evolutions

## Features

- 13 playable levels from `0` through `12`
- Custom birds, backgrounds, floors, obstacle art, and music by level
- Score-based progression with transition screens between levels
- Special mechanics including vines, wind, poison clouds, weapon attacks, asteroids, and black holes
- Ending video, credits video, and ending music after the final clear

## Requirements

- Python `3.10+`
- `pip`

## Install

1. Clone or download this repository.
2. Open a terminal in the project folder.
3. Create a virtual environment:

```bash
python3 -m venv .venv
```

4. Activate it:

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

## How To Play

- Press `Space` to start.
- Press `Space` while playing to flap upward.
- Press `Space` on a level intro screen to continue into that level.
- Press `Space` after game over to restart.
- Close the game window to quit.

## Scoring And Progression

- You earn `10` points for each obstacle pair you clear.
- Level transitions are based on total score.
- The game pauses for a `12` second transition when you reach the next level threshold.
- After each transition, a level intro screen explains the next mechanic.
- The final stage is level `12`, and the full clear happens at `5000` points.

## Level Thresholds

| Level | Name | Score To Reach |
| --- | --- | ---: |
| 0 | Normal | Start of game |
| 1 | Neon City | 200 |
| 2 | Jungle | 600 |
| 3 | Volcano | 1000 |
| 4 | Ice / Snow | 1400 |
| 5 | Ocean | 1800 |
| 6 | Toxic Lab | 2200 |
| 7 | Backrooms | 2600 |
| 8 | Castle Oblivion | 3000 |
| 9 | Space | 3400 |
| 10 | Black Hole | 3800 |
| 11 | Sky / Heaven | 4200 |
| 12 | Retro | 4600 |
| Final Clear | Ending sequence | 5000 |

## Level Guide

| Level | Name | Description |
| --- | --- | --- |
| 0 | Normal | Classic Flappy Bird gameplay. Pass through pipes to score. |
| 1 | Neon City | Faster pacing. Pipes move quicker and the bird responds faster. |
| 2 | Jungle | Swinging vines appear as extra hazards while you fly through wider gaps. |
| 3 | Volcano | Heat distortion and screen shake make the level harder to read. |
| 4 | Ice / Snow | Wind gusts push the bird left after a warning icon appears. |
| 5 | Ocean | Lower gravity and buoyancy make movement floatier than normal. |
| 6 | Toxic Lab | Poison cloud hazards appear in the play space. |
| 7 | Backrooms | Creepy smiley enemies add moving danger between obstacles. |
| 8 | Castle Oblivion | Organization weapon attacks fly across the screen. |
| 9 | Space | Low gravity returns and asteroid pairs become the main hazard. |
| 10 | Black Hole | Black holes pull the bird inward and can kill on contact. |
| 11 | Sky / Heaven | Smaller pipe gaps and a tougher gap pattern raise the difficulty. |
| 12 | Retro | Final challenge with much faster gameplay. |

## Project Structure

```text
FlappyBird/
├── FlappyBird.py
├── FlappyBird.spec
├── requirements.txt
├── README.md
└── assets/
    ├── images/
    │   ├── backgrounds/
    │   ├── bird_models/
    │   ├── floors/
    │   └── objects/
    ├── music/
    └── videos/
```

## Assets

- Images are loaded from `assets/images/`
- Gameplay object art is loaded from `assets/images/objects/`
- Music is loaded from `assets/music/`
- Ending videos are loaded from `assets/videos/`

## Dependencies

- `pygame` for the game loop, rendering, audio, and input
- `opencv-python` for the ending and credits video playback

## Notes

- The game tracks score and high score for the current run only.
- If `opencv-python` is missing, the game can still run, but ending video playback will fail.
