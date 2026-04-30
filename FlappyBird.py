import random
import sys
from pathlib import Path

import pygame

WIDTH, HEIGHT = 750, 900
FLOOR_Y = 520
PIPE_SPEED = 3
GRAVITY = 10
FLAP_STRENGTH = 10

ASSET_DIR = Path(__file__).resolve().parent
IMAGE_DIR = ASSET_DIR / "images"
MUSIC_DIR = ASSET_DIR / "music"

def load_image(filename, *, alpha=False):
    path = IMAGE_DIR / filename
    image = pygame.image.load(str(path))
    return image.convert_alpha() if alpha else image.convert()

def draw_floor():
    screen.blit(floor_img, (floor_x, FLOOR_Y))
    screen.blit(floor_img, (floor_x + floor_img.get_width(), FLOOR_Y))

def create_pipes():
    pipe_y = random.choice(pipe_heights)
    bottom_pipe = pipe_img.get_rect(midtop=(WIDTH + 60, pipe_y))
    top_pipe = pipe_img.get_rect(midbottom=(WIDTH + 60, pipe_y - 160))
    return top_pipe, bottom_pipe

def move_and_draw_pipes():
    global game_over, score_ready

    remaining_pipes = []
    flipped_pipe = pygame.transform.flip(pipe_img, False, True)

    for pipe in pipes:
        pipe.centerx -= PIPE_SPEED

        if pipe.bottom >= HEIGHT:
            screen.blit(pipe_img, pipe)
        else:
            screen.blit(flipped_pipe, pipe)

        if pipe.right > -50:
            remaining_pipes.append(pipe)

        if bird_rect.colliderect(pipe):
            game_over = True

        if pipe.centerx < bird_rect.centerx and score_ready:
            score_point.play()
            score_tracker["score"] += 0.5
            score_ready = False

        if pipe.centerx < bird_rect.centerx - 40:
            score_ready = True

    pipes[:] = remaining_pipes

def draw_score(game_state):
    if game_state == "game_on":
        score_text = score_font.render(str(int(score_tracker["score"])), True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, 66))
        screen.blit(score_text, score_rect)
    else:
        score_text = score_font.render(f"Score: {int(score_tracker['score'])}", True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(WIDTH // 2, 66))
        screen.blit(score_text, score_rect)

        high_score_text = score_font.render(
            f"High Score: {int(score_tracker['high_score'])}",
            True,
            (255, 255, 255),
        )
        high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, 110))
        screen.blit(high_score_text, high_score_rect)

def update_score():
    if score_tracker["score"] > score_tracker["high_score"]:
        score_tracker["high_score"] = score_tracker["score"]

def animate_bird():
    new_bird = birds[bird_index]
    new_rect = new_bird.get_rect(center=bird_rect.center)
    return new_bird, new_rect

def rotate_bird(bird):
    return pygame.transform.rotozoom(bird, bird_movement * -3, 1)

def reset_game():
    global bird_rect, bird_movement, pipes, game_over, score_ready

    pipes = []
    bird_rect = bird_img.get_rect(center=(67, HEIGHT // 2))
    bird_movement = 0
    game_over = False
    score_ready = True
    score_tracker["score"] = 0

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")
try:
    pygame.mixer.init()
    pygame.mixer.music.load(str(MUSIC_DIR / "FB-BG-music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1)
except pygame.error:
    pass

back_img = load_image("background_img.png")
floor_img = load_image("floor_img.png")
pipe_img = load_image("pipe_img.webp", alpha=True)
over_img = load_image("game_over.png", alpha=True)

bird_up = load_image("bird_up.jpg", alpha=True)
bird_mid = load_image("bird_mid.png", alpha=True)
bird_down = load_image("bird_down.jpeg", alpha=True)
birds = [bird_up, bird_mid, bird_down]
bird_index = 0
bird_img = birds[bird_index]
bird_rect = bird_img.get_rect(center=(67, HEIGHT // 2))
bird_movement = 0

bird_flap = pygame.USEREVENT
create_pipe = pygame.USEREVENT + 1
pygame.time.set_timer(bird_flap, 200)
pygame.time.set_timer(create_pipe, 1200)

pipe_heights = [400, 350, 533, 490]
pipes = []
floor_x = 0
game_over = False
score_ready = True
score_tracker = {"score": 0, "high_score": 0}
score_font = pygame.font.Font("freesansbold.ttf", 27)
over_rect = over_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))

class SilentSound:
    def play(self):
        return None

score_point = SilentSound()

running = True
while running:
    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not game_over:
                bird_movement = FLAP_STRENGTH
            else:
                reset_game()

        if event.type == bird_flap:
            bird_index = (bird_index + 1) % len(birds)
            bird_img, bird_rect = animate_bird()

        if event.type == create_pipe and not game_over:
            pipes.extend(create_pipes())

    screen.blit(back_img, (0, 0))

    if not game_over:
        bird_movement += GRAVITY
        bird_rect.centery += bird_movement

        rotated_bird = rotate_bird(bird_img)
        screen.blit(rotated_bird, bird_rect)

        move_and_draw_pipes()
        update_score()
        draw_score("game_on")

        if bird_rect.top <= -20 or bird_rect.bottom >= FLOOR_Y:
            game_over = True
    else:
        screen.blit(bird_img, bird_rect)
        screen.blit(over_img, over_rect)
        draw_score("game_over")

    floor_x -= 1
    if floor_x <= -floor_img.get_width():
        floor_x = 0
    draw_floor()

    pygame.display.update()

pygame.quit()
sys.exit()