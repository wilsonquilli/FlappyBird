import math
import random
import sys
from collections import deque
from pathlib import Path
import pygame

#DISPLAY / PHYSICS CONSTANTS
WIDTH, HEIGHT = 750, 900
FLOOR_HEIGHT = 180
FLOOR_Y = HEIGHT - FLOOR_HEIGHT
GROUND_SEAM_HEIGHT = 4
BASE_PIPE_SPEED = 4
BASE_GRAVITY = 0.38
FLAP_STRENGTH = -8.5
PIPE_GAP = 230
PIPE_SPAWN_X = WIDTH + 120
BASE_PIPE_SPAWN_INTERVAL = 1550
BIRD_START_X = 160
BIRD_START_Y = HEIGHT // 2 - 40
BIRD_SIZE = (68, 48)
PIPE_WIDTH = 150
PIPE_HEIGHT = 620
JUNGLE_TREE_HEIGHT = 240
GAME_OVER_WIDTH = 360
GAME_OVER_TOP = 180
LEVEL_TRANSITION_FRAMES = 75
PIPE_MARGIN_TOP = 110
PIPE_MARGIN_BOTTOM = 110
ASSET_DIR = Path(__file__).resolve().parent
IMAGE_DIR = ASSET_DIR / "images"
MUSIC_DIR = ASSET_DIR / "music"
IMAGE_SEARCH_DIRS = (
    IMAGE_DIR,
    IMAGE_DIR / "assets",
    IMAGE_DIR / "backgrounds",
    IMAGE_DIR / "bird_models",
    IMAGE_DIR / "pipe_images",
)

#LEVEL CONFIG (score threshold per level)
LEVEL_SCORE_THRESHOLDS = [0, 50, 100]
MAX_LEVEL = 12  # 0-11 = normal…black-hole, 12 = retro final

LEVEL_MUSIC = {
    0: "FB-BG-music.mp3",
    1: "Neon_City_Music.mp3",      
    2: "Jungle_Theme.mp3",           
    3: "Volcano_Lava_Theme.mp3",         
    4: "Ice_Snow_Theme.mp3",              
    5: "Ocean_Theme.mp3",           
    6: "Toxic_Lab.mp3",         
    7: "Backrooms_Theme.mp3",       
    8: "Castle_Oblivion.mp3",           
    9: "Space_Theme.mp3",            
    10: "Black_Hole_Theme.mp3",     
    11: "Heaven_Sky_Theme.mp3",        
    12: "Retro_Theme.mp3",          
}

LEVEL_BACKGROUNDS = {
    0: "background_img.png",
    1: "Cyberpunk_Background.jpg",           
    2: "Jungle_Background.jpg",            
    3: "Volcano_Background.jpg",           
    4: "Ice_Background.jpg",               
    5: "Underwater_Background.webp",            
    6: "Toxic_Lab_Background.gif",            
    7: "Backrooms_Background.jpg",         
    8: "Castle_Oblivion_Background.jpg",             
    9: "Space_Background.jpg",               
    10: "Black_Hole_Background.jpg",         
    11: "Sky_Background.jpg",             
    12: "Retro_Background.jpg",              
}

LEVEL_BIRD_FRAMES = {
    0: ("bird_up.jpg", "bird_mid.png", "bird_down.jpeg"),
    1: ("Cyber_Bird_Up.png", "Cyber_Bird_Mid.png", "Cyber_Bird_Down.png"),   
    2: ("Scarlet_Macaw_Up.png", "Scarlet_Macaw_Mid.png", "Scarlet_Macaw_Down.png"),
    3: ("bird3_up.png", "bird3_mid.png", "bird3_down.png"),    # flame
    4: ("bird4_up.png", "bird4_mid.png", "bird4_down.png"),    # icy
    5: ("bird5_up.png", "bird5_mid.png", "bird5_down.png"),    # fish
    6: ("bird6_up.png", "bird6_mid.png", "bird6_down.png"),    # mutant
    7: ("bird7_up.png", "bird7_mid.png", "bird7_down.png"),    # smiley
    8: ("bird8_up.png", "bird8_mid.png", "bird8_down.png"),    # robe
    9: ("bird9_up.png", "bird9_mid.png", "bird9_down.png"),    # star trail
    10: ("bird10_up.png", "bird10_mid.png", "bird10_down.png"),# glitched
    11: ("bird11_up.png", "bird11_mid.png", "bird11_down.png"),# angel
    12: ("bird_up.jpg", "bird_mid.png", "bird_down.jpeg"),     # retro (reuse or pixel version)
}

LEVEL_PIPE_VARIANTS = {
    0: ("pipe_img.webp",),
    1: ("Neon_Building_1.png", "Neon_Building_2.png", "Neon_Building_3.png"),
    2: ("Jungle_Tree_1.png", "Jungle_Tree_2.png", "Jungle_Tree_3.png"),
}

#IMAGE / AUDIO HELPERS
def load_image(filename, *, alpha=False):
    path = None
    for base_dir in IMAGE_SEARCH_DIRS:
        candidate = base_dir / filename
        if candidate.exists():
            path = candidate
            break
    if path is None:
        raise FileNotFoundError(f"Unable to locate image asset '{filename}' in {IMAGE_SEARCH_DIRS}")
    image = pygame.image.load(str(path))
    return image.convert_alpha() if alpha else image.convert()

def scale_image(image, size):
    return pygame.transform.smoothscale(image, size)

def trim_top_edge(image, pixels):
    width, height = image.get_size()
    if pixels <= 0 or pixels >= height:
        return image
    return image.subsurface((0, pixels, width, height - pixels)).copy()

def trim_sprite(image, threshold=220):
    source = image.convert_alpha()
    bounds = []
    for x in range(source.get_width()):
        for y in range(source.get_height()):
            r, g, b, _ = source.get_at((x, y))
            if min(r, g, b) < threshold:
                bounds.append((x, y))
    if not bounds:
        return source
    left = min(x for x, _ in bounds)
    right = max(x for x, _ in bounds) + 1
    top = min(y for _, y in bounds)
    bottom = max(y for _, y in bounds) + 1
    return source.subsurface((left, top, right - left, bottom - top)).copy()

def remove_background_from_edges(image, tolerance=65):
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    corners = [
        cleaned.get_at((0, 0))[:3],
        cleaned.get_at((width - 1, 0))[:3],
        cleaned.get_at((0, height - 1))[:3],
        cleaned.get_at((width - 1, height - 1))[:3],
    ]
    target = tuple(sum(c) // len(corners) for c in zip(*corners))
    visited = set()
    queue = deque()
    for x in range(width):
        queue.append((x, 0)); queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y)); queue.append((width - 1, y))
    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))
        r, g, b, a = cleaned.get_at((x, y))
        if max(abs(r - target[0]), abs(g - target[1]), abs(b - target[2])) > tolerance:
            continue
        cleaned.set_at((x, y), (r, g, b, 0))
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))
    return cleaned

def remove_bright_background_from_edges(image, threshold=235):
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    for x in range(width):
        queue.append((x, 0))
        queue.append((x, height - 1))
    for y in range(height):
        queue.append((0, y))
        queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        if (x, y) in visited:
            continue
        visited.add((x, y))

        red, green, blue, alpha = cleaned.get_at((x, y))
        if red < threshold or green < threshold or blue < threshold:
            continue

        cleaned.set_at((x, y), (red, green, blue, 0))

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    return cleaned

def load_bird_frame(filename):
    image = load_image(filename, alpha=True)
    image = remove_bright_background_from_edges(image)
    image = remove_background_from_edges(image)
    image = trim_sprite(image)
    return scale_image(image, BIRD_SIZE)

def load_gameplay_sprite(filename, size):
    image = load_image(filename, alpha=True)
    image = remove_background_from_edges(image)
    return scale_image(image, size)

def fit_sprite_to_box(image, box_size):
    box_width, box_height = box_size
    width, height = image.get_size()
    scale = min(box_width / width, box_height / height)
    scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return scale_image(image, scaled_size)

def build_obstacle_surface(filename, *, flipped=False, remove_bg=True):
    sprite = load_image(filename, alpha=True)
    if remove_bg:
        sprite = remove_background_from_edges(sprite)
        sprite = trim_sprite(sprite)

    if flipped:
        sprite = pygame.transform.flip(sprite, False, True)

    surface = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)

    if filename.startswith("Jungle_Tree_"):
        fitted = fit_sprite_to_box(sprite, (PIPE_WIDTH, JUNGLE_TREE_HEIGHT))
        x = (PIPE_WIDTH - fitted.get_width()) // 2
        y = 0 if flipped else PIPE_HEIGHT - fitted.get_height()
    else:
        fitted = fit_sprite_to_box(sprite, (PIPE_WIDTH, PIPE_HEIGHT))
        x = (PIPE_WIDTH - fitted.get_width()) // 2
        y = PIPE_HEIGHT - fitted.get_height() if flipped else 0

    surface.blit(fitted, (x, y))
    return surface

def try_load_bird_frames(level):
    """Load bird frames for a level, falling back to level-0 frames on missing files."""
    frames_names = LEVEL_BIRD_FRAMES.get(level, LEVEL_BIRD_FRAMES[0])
    loaded = []
    fallback_names = LEVEL_BIRD_FRAMES[0]
    for i, name in enumerate(frames_names):
        try:
            loaded.append(load_bird_frame(name))
        except Exception:
            loaded.append(load_bird_frame(fallback_names[i]))
    return loaded

def try_load_background(level):
    """Load background for a level, falling back to level-0 on missing files."""
    name = LEVEL_BACKGROUNDS.get(level, LEVEL_BACKGROUNDS[0])
    try:
        return scale_image(load_image(name), (WIDTH, HEIGHT))
    except Exception:
        return scale_image(load_image(LEVEL_BACKGROUNDS[0]), (WIDTH, HEIGHT))

def try_play_music(level):
    name = LEVEL_MUSIC.get(level, LEVEL_MUSIC[0])
    path = MUSIC_DIR / name
    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

def build_pipe_variant(filename):
    if filename == "pipe_img.webp":
        image = load_gameplay_sprite(filename, (PIPE_WIDTH, PIPE_HEIGHT))
        top_image = pygame.transform.flip(image, False, True)
    else:
        should_remove_bg = not filename.startswith("Neon_Building_")
        image = build_obstacle_surface(filename, flipped=False, remove_bg=should_remove_bg)
        top_image = build_obstacle_surface(filename, flipped=True, remove_bg=should_remove_bg)
    return {
        "bottom": image,
        "bottom_mask": pygame.mask.from_surface(image),
        "top": top_image,
        "top_mask": pygame.mask.from_surface(top_image),
    }

def try_load_pipe_variants(level):
    variant_names = LEVEL_PIPE_VARIANTS.get(level, LEVEL_PIPE_VARIANTS[0])
    variants = []
    for name in variant_names:
        try:
            variants.append(build_pipe_variant(name))
        except Exception:
            continue
    if not variants:
        for fallback_name in LEVEL_PIPE_VARIANTS[0]:
            variants.append(build_pipe_variant(fallback_name))
    return variants

#PIPE SPEED / GRAVITY PER LEVEL
def get_level_pipe_speed(level):
    if level == 1:
        return BASE_PIPE_SPEED * 1.25
    if level == 5:
        return BASE_PIPE_SPEED * 0.8      
    if level == 12:
        return BASE_PIPE_SPEED * 2.0       
    return BASE_PIPE_SPEED

def get_level_bird_speed_multiplier(level):
    if level == 1:
        return 1.25
    return 1.0

def get_level_gravity(level):
    if level == 9:
        return BASE_GRAVITY * 0.5         
    if level == 5:
        return BASE_GRAVITY * 0.75        
    return BASE_GRAVITY

def get_level_pipe_gap(level):
    if level == 2:
        return 400
    if level == 11:
        return PIPE_GAP * 1.45            
    return PIPE_GAP

def get_level_spawn_interval(level):
    if level == 1:
        return int(BASE_PIPE_SPAWN_INTERVAL / 1.25)
    if level == 5:
        return int(BASE_PIPE_SPAWN_INTERVAL / 0.8)
    if level == 12:
        return int(BASE_PIPE_SPAWN_INTERVAL / 2.0)
    return BASE_PIPE_SPAWN_INTERVAL

#DRAWING HELPERS
def draw_floor():
    pygame.draw.rect(screen, ground_fill_color, (0, FLOOR_Y, WIDTH, GROUND_SEAM_HEIGHT))
    screen.blit(floor_img, (floor_x, FLOOR_Y))
    screen.blit(floor_img, (floor_x + floor_img.get_width(), FLOOR_Y))

def draw_score(game_state):
    if game_state == "game_on":
        score_text = score_font.render(str(int(score_tracker["score"])), True, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 70)))

        lvl_text = prompt_font.render(f"Level {current_level}", True, (255, 255, 0))
        screen.blit(lvl_text, lvl_text.get_rect(center=(WIDTH // 2, 100)))
    elif game_state == "welcome":
        welcome_text = prompt_font.render("Press Space to Start!", True, (255, 255, 255))
        screen.blit(welcome_text, welcome_text.get_rect(center=(WIDTH // 2, 120)))
    else:
        score_text = score_font.render(f"Score: {int(score_tracker['score'])}", True, (255, 255, 255))
        screen.blit(score_text, score_text.get_rect(center=(WIDTH // 2, 80)))
        hs_text = score_font.render(f"High Score: {int(score_tracker['high_score'])}", True, (255, 255, 255))
        screen.blit(hs_text, hs_text.get_rect(center=(WIDTH // 2, 125)))
        restart_text = prompt_font.render("Press Space to go Again", True, (255, 255, 255))
        screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, 170)))

def draw_level_transition():
    if transition_timer <= 0 or pending_level is None:
        return

    fade_strength = min(transition_timer, LEVEL_TRANSITION_FRAMES - transition_timer)
    alpha = max(85, min(190, fade_strength * 6))
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 12, 22, alpha))
    screen.blit(overlay, (0, 0))

    title_text = prompt_font.render("Level Up", True, (255, 230, 120))
    level_text = score_font.render(f"Level {pending_level}", True, (255, 255, 255))
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 24)))
    screen.blit(level_text, level_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 16)))

def animate_bird():
    new_bird = current_birds[bird_index]
    new_rect = new_bird.get_rect(center=bird_rect.center)
    return new_bird, new_rect

def rotate_bird(bird):
    return pygame.transform.rotozoom(bird, bird_movement * -3, 1)

def update_score():
    if score_tracker["score"] > score_tracker["high_score"]:
        score_tracker["high_score"] = score_tracker["score"]

#PIPE CREATION / MOVEMENT
def create_pipes():
    gap = get_level_pipe_gap(current_level)
    pipe_center_min = PIPE_MARGIN_TOP + gap // 2
    pipe_center_max = FLOOR_Y - PIPE_MARGIN_BOTTOM - gap // 2
    gap_center = random.randint(pipe_center_min, pipe_center_max)

    variant_index = random.randrange(len(current_pipe_variants))
    variant = current_pipe_variants[variant_index]

    if current_level == 2:
        top_pipe = variant["top"].get_rect(topleft=(PIPE_SPAWN_X, 0))
        bottom_pipe = variant["bottom"].get_rect(bottomleft=(PIPE_SPAWN_X, FLOOR_Y))

        return {
            "top": top_pipe,
            "bottom": bottom_pipe,
            "scored": False,
            "variant_index": variant_index,
        }

    bottom_pipe = variant["bottom"].get_rect(midtop=(PIPE_SPAWN_X, gap_center + gap // 2))
    top_pipe = variant["top"].get_rect(midbottom=(PIPE_SPAWN_X, gap_center - gap // 2))

    return {
        "top": top_pipe,
        "bottom": bottom_pipe,
        "scored": False,
        "variant_index": variant_index,
    }

def collides_with_pipe(bird_surface, bird_surface_rect, pipe_surface, pipe_rect, pipe_mask):
    if not bird_surface_rect.colliderect(pipe_rect):
        return False
    bird_mask = pygame.mask.from_surface(bird_surface)
    offset = (pipe_rect.left - bird_surface_rect.left, pipe_rect.top - bird_surface_rect.top)
    return bird_mask.overlap(pipe_mask, offset) is not None

def move_and_draw_pipes(bird_surface, bird_surface_rect):
    global game_over

    pipe_speed = get_level_pipe_speed(current_level)
    remaining = []

    for pipe_pair in pipes:
        if not isinstance(pipe_pair, dict):
            continue

        variant = current_pipe_variants[pipe_pair.get("variant_index", 0) % len(current_pipe_variants)]

        top_pipe = pipe_pair["top"]
        bottom_pipe = pipe_pair["bottom"]

        top_pipe.centerx -= pipe_speed
        bottom_pipe.centerx -= pipe_speed

        if current_level == 1:
            draw_pipe_neon(top_pipe, bottom_pipe, variant)
        else:
            screen.blit(variant["top"], top_pipe)
            screen.blit(variant["bottom"], bottom_pipe)

        if True:
            top_hit = collides_with_pipe(
                bird_surface,
                bird_surface_rect,
                variant["top"],
                top_pipe,
                variant["top_mask"]
            )

            bottom_hit = collides_with_pipe(
                bird_surface,
                bird_surface_rect,
                variant["bottom"],
                bottom_pipe,
                variant["bottom_mask"]
            )

            if top_hit or bottom_hit:
                game_over = True

        if top_pipe.right > -variant["bottom"].get_width():
            remaining.append(pipe_pair)

        if not pipe_pair["scored"] and bottom_pipe.centerx < bird_rect.centerx:
            score_point.play()
            score_tracker["score"] += 10
            pipe_pair["scored"] = True

    pipes[:] = remaining

def draw_existing_pipes():
    for pipe_pair in pipes:
        if not isinstance(pipe_pair, dict):
            continue
        variant = current_pipe_variants[pipe_pair.get("variant_index", 0) % len(current_pipe_variants)]
        screen.blit(variant["top"], pipe_pair["top"])
        screen.blit(variant["bottom"], pipe_pair["bottom"])

#LEVEL EFFECT STATE
effect_state = {}

def reset_effect_state():
    effect_state.clear()
    effect_state["neon_timer"] = 0
    effect_state["neon_bright"] = True
    effect_state["vines"] = []
    effect_state["shake_timer"] = 0
    effect_state["shake_offset"] = (0, 0)
    effect_state["vine_spawn_timer"] = 0
    effect_state["heat_shake_timer"] = 0
    effect_state["heat_shake_offset"] = (0, 0)
    effect_state["heat_wave_lines"] = []
    effect_state["wind_active"] = False
    effect_state["wind_timer"] = 0
    effect_state["wind_next"] = random.randint(180, 360)
    effect_state["buoy_timer"] = 0
    effect_state["buoy_next"] = random.randint(120, 240)
    effect_state["gas_clouds"] = []
    effect_state["gas_spawn_timer"] = 0
    effect_state["smileys"] = []
    effect_state["smiley_spawn_timer"] = 0
    effect_state["beams"] = []
    effect_state["beam_spawn_timer"] = 0
    effect_state["asteroids"] = []
    effect_state["asteroid_spawn_timer"] = 0
    effect_state["black_holes"] = []
    effect_state["bh_spawn_timer"] = 0
    effect_state["blink_timer"] = 0
    effect_state["blink_next"] = random.randint(120, 300)
    effect_state["blink_active"] = False
    effect_state["gold_pulse"] = 0
    effect_state["scanline_offset"] = 0
    effect_state["light_bands"] = []
    effect_state["light_spawn_timer"] = 0

#PER-LEVEL EFFECTS
#Level 1: Neon / Cyberpunk 
def draw_pipe_neon(top_pipe, bottom_pipe, variant):
    """Draw neon building obstacles without extra flashing overlays."""
    screen.blit(variant["top"], top_pipe)
    screen.blit(variant["bottom"], bottom_pipe)

def apply_level_effects_post_bird(bird_surface_ref, bird_rect_ref, bird_movement_ref):
    """Called after bird is drawn — returns movement delta."""
    dy_extra = 0

    if current_level == 1:
        t = pygame.time.get_ticks()
        pulse_alpha = 90 + int(45 * math.sin(t / 200))

        mask = pygame.mask.from_surface(bird_surface_ref)
        outline = mask.outline()

        if outline:
            padding = 16
            glow_surf = pygame.Surface(
                (bird_rect_ref.width + padding * 2, bird_rect_ref.height + padding * 2),
                pygame.SRCALPHA
            )

            offset_outline = [(x + padding, y + padding) for x, y in outline]

            for thickness in range(10, 2, -2):
                pygame.draw.lines(
                    glow_surf,
                    (255, 35, 45, max(15, pulse_alpha - thickness * 7)),
                    True,
                    offset_outline,
                    thickness
                )

            pygame.draw.lines(
                glow_surf,
                (255, 0, 0, 210),
                True,
                offset_outline,
                2
            )

            screen.blit(
                glow_surf,
                (bird_rect_ref.x - padding, bird_rect_ref.y - padding)
            )

    if current_level == 3:
        draw_ember_trail(bird_rect_ref.center)

    if current_level == 4:
        draw_frost_trail(bird_rect_ref.center)
        dx = update_wind(bird_movement_ref)
        bird_rect_ref.centerx += dx
        bird_rect_ref.centerx = max(0, min(WIDTH, bird_rect_ref.centerx))

    if current_level == 5:
        dy_extra = update_buoyancy(bird_movement_ref)

    if current_level == 6:
        update_draw_gas_clouds(bird_rect_ref)

    if current_level == 7:
        update_draw_smileys(bird_rect_ref)

    if current_level == 8:
        update_draw_beams(bird_rect_ref)

    if current_level == 9:
        draw_star_trail(bird_rect_ref.center)
        update_draw_asteroids(bird_rect_ref)

    if current_level == 10:
        dy_extra = update_draw_black_holes(bird_rect_ref, bird_movement_ref)

    if current_level == 12:
        draw_scanlines()

    return dy_extra

#Level 2: Jungle
def point_to_segment_distance(px, py, ax, ay, bx, by):
    abx = bx - ax
    aby = by - ay
    ab_len_sq = abx * abx + aby * aby
    if ab_len_sq == 0:
        return math.hypot(px - ax, py - ay)
    projection = ((px - ax) * abx + (py - ay) * aby) / ab_len_sq
    projection = max(0.0, min(1.0, projection))
    closest_x = ax + projection * abx
    closest_y = ay + projection * aby
    return math.hypot(px - closest_x, py - closest_y)

def spawn_vine():
    from_top = random.choice([True, False])

    vine = {
        "x": PIPE_SPAWN_X + PIPE_WIDTH + random.randint(80, 220),
        "from_top": from_top,
        "length": random.randint(250, 390),
        "angle": random.uniform(-0.18, 0.18),
        "swing": random.uniform(-0.018, 0.018),
        "timer": 0,
    }

    effect_state["vines"].append(vine)

def draw_vine_sprite(vine, base_x, base_y, tip_x, tip_y):
    vine_width = max(38, min(72, vine["length"] // 4))
    vine_surface = scale_image(vine_img, (vine_width, vine["length"]))

    if not vine["from_top"]:
        vine_surface = pygame.transform.flip(vine_surface, False, True)

    dx = tip_x - base_x
    dy = tip_y - base_y

    angle = -math.degrees(math.atan2(dx, dy))
    rotated_vine = pygame.transform.rotate(vine_surface, angle)

    vine_rect = rotated_vine.get_rect(
        center=(
            int((base_x + tip_x) / 2),
            int((base_y + tip_y) / 2),
        )
    )

    screen.blit(rotated_vine, vine_rect)

def update_draw_vines(bird_rect_ref):
    global game_over

    effect_state["vine_spawn_timer"] += 1

    if effect_state["vine_spawn_timer"] > 120:
        effect_state["vine_spawn_timer"] = 0
        spawn_vine()

    remaining = []

    for vine in effect_state["vines"]:
        vine["timer"] += 1
        vine["angle"] += vine["swing"]
        vine["x"] -= get_level_pipe_speed(current_level)

        base_x = vine["x"]
        base_y = 0 if vine["from_top"] else FLOOR_Y

        tip_x = base_x + math.sin(vine["angle"]) * 70

        if vine["from_top"]:
            tip_y = base_y + vine["length"]
        else:
            tip_y = base_y - vine["length"]

        draw_vine_sprite(vine, base_x, base_y, tip_x, tip_y)

        bird_radius = max(14, min(bird_rect_ref.width, bird_rect_ref.height) // 3)

        line_distance = point_to_segment_distance(
            bird_rect_ref.centerx,
            bird_rect_ref.centery,
            base_x,
            base_y,
            tip_x,
            tip_y,
        )

        leaf_distance = math.hypot(
            bird_rect_ref.centerx - tip_x,
            bird_rect_ref.centery - tip_y
        )

        if line_distance <= bird_radius + 10 or leaf_distance <= bird_radius + 14:
            game_over = True

        if vine["x"] > -120:
            remaining.append(vine)

    effect_state["vines"] = remaining

def update_jungle_shake():
    effect_state["shake_timer"] += 1
    shake_interval = random.randint(300, 600)
    if effect_state["shake_timer"] > shake_interval:
        effect_state["shake_timer"] = 0
        effect_state["shake_offset"] = (random.randint(-6, 6), random.randint(-4, 4))
    else:
        ox, oy = effect_state["shake_offset"]
        ox = int(ox * 0.85)
        oy = int(oy * 0.85)
        effect_state["shake_offset"] = (ox, oy)
    return effect_state["shake_offset"]

#Level 3: Volcano
def update_heat_shake():
    effect_state["heat_shake_timer"] += 1
    if effect_state["heat_shake_timer"] > random.randint(200, 400):
        effect_state["heat_shake_timer"] = 0
        effect_state["heat_shake_offset"] = (random.randint(-4, 4), random.randint(-3, 3))
    else:
        ox, oy = effect_state["heat_shake_offset"]
        ox = int(ox * 0.8)
        oy = int(oy * 0.8)
        effect_state["heat_shake_offset"] = (ox, oy)
    return effect_state["heat_shake_offset"]

def draw_heat_waves():
    t = pygame.time.get_ticks()
    for i in range(0, HEIGHT, 40):
        offset = int(3 * math.sin((t / 300) + i * 0.05))
        heat_color = (255, 80, 0, 30)
        s = pygame.Surface((WIDTH, 3), pygame.SRCALPHA)
        s.fill(heat_color)
        screen.blit(s, (offset, i))

def draw_ember_trail(bird_center):
    """Draw a small ember particle trail behind the bird for level 3."""
    for _ in range(3):
        ex = bird_center[0] - random.randint(10, 30)
        ey = bird_center[1] + random.randint(-8, 8)
        r = random.randint(3, 7)
        col = random.choice([(255, 120, 0), (255, 60, 0), (255, 220, 0)])
        pygame.draw.circle(screen, col, (ex, ey), r)

#Level 4: Ice / Snow
def update_wind(bird_movement_val):
    """Returns a horizontal push to apply to bird_rect each frame."""
    effect_state["wind_timer"] += 1
    if not effect_state["wind_active"]:
        if effect_state["wind_timer"] >= effect_state["wind_next"]:
            effect_state["wind_active"] = True
            effect_state["wind_timer"] = 0
    else:
        if effect_state["wind_timer"] >= 60:
            effect_state["wind_active"] = False
            effect_state["wind_timer"] = 0
            effect_state["wind_next"] = random.randint(180, 360)
    return -2 if effect_state["wind_active"] else 0  

def draw_snowflakes():
    if "snowflakes" not in effect_state:
        effect_state["snowflakes"] = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1, 3)]
            for _ in range(80)
        ]
    for flake in effect_state["snowflakes"]:
        pygame.draw.circle(screen, (220, 240, 255), (int(flake[0]), int(flake[1])), int(flake[2]))
        flake[1] += flake[2] * 0.7
        flake[0] += random.uniform(-0.5, 0.5)
        if flake[1] > FLOOR_Y:
            flake[1] = 0
            flake[0] = random.randint(0, WIDTH)

def draw_frost_trail(bird_center):
    for _ in range(2):
        fx = bird_center[0] - random.randint(8, 24)
        fy = bird_center[1] + random.randint(-6, 6)
        r = random.randint(3, 6)
        pygame.draw.circle(screen, (180, 220, 255, 180), (fx, fy), r)

#Level 5: Ocean
def update_buoyancy(bird_movement_ref):
    """Periodically apply gentle upward push (buoyancy)."""
    effect_state["buoy_timer"] += 1
    if effect_state["buoy_timer"] >= effect_state["buoy_next"]:
        effect_state["buoy_timer"] = 0
        effect_state["buoy_next"] = random.randint(120, 240)
        return -1.5 
    return 0

def draw_bubbles():
    if "bubbles" not in effect_state:
        effect_state["bubbles"] = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(4, 10), random.uniform(0.5, 1.5)]
            for _ in range(40)
        ]
    for b in effect_state["bubbles"]:
        pygame.draw.circle(screen, (100, 180, 255), (int(b[0]), int(b[1])), b[2], 1)
        b[1] -= b[3]
        if b[1] < 0:
            b[1] = FLOOR_Y
            b[0] = random.randint(0, WIDTH)

#Level 6: Toxic Lab 
def spawn_gas_cloud():
    from_top = random.choice([True, False])
    effect_state["gas_clouds"].append({
        "x": WIDTH + 40,
        "y": random.randint(0, 80) if from_top else random.randint(FLOOR_Y - 100, FLOOR_Y - 20),
        "radius": random.randint(30, 60),
        "alpha": random.randint(80, 150),
        "from_top": from_top,
    })

def update_draw_gas_clouds(bird_rect_ref):
    global game_over
    effect_state["gas_spawn_timer"] += 1
    if effect_state["gas_spawn_timer"] > random.randint(180, 300):
        effect_state["gas_spawn_timer"] = 0
        spawn_gas_cloud()

    remaining = []
    for cloud in effect_state["gas_clouds"]:
        cloud["x"] -= 2
        s = pygame.Surface((cloud["radius"] * 2, cloud["radius"] * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (0, 200, 60, cloud["alpha"]), (cloud["radius"], cloud["radius"]), cloud["radius"])
        screen.blit(s, (int(cloud["x"] - cloud["radius"]), int(cloud["y"] - cloud["radius"])))

        cloud_rect = pygame.Rect(cloud["x"] - cloud["radius"], cloud["y"] - cloud["radius"],
                                 cloud["radius"] * 2, cloud["radius"] * 2)
        if cloud_rect.colliderect(bird_rect_ref):
            game_over = True

        if cloud["x"] > -cloud["radius"] * 2:
            remaining.append(cloud)
    effect_state["gas_clouds"] = remaining

#Level 7: Backrooms
def spawn_smiley():
    effect_state["smileys"].append({
        "x": WIDTH + 60,
        "y": random.randint(80, FLOOR_Y - 80),
        "radius": random.randint(28, 45),
        "speed": random.uniform(2, 4),
    })

def update_draw_smileys(bird_rect_ref):
    global game_over
    effect_state["smiley_spawn_timer"] += 1
    if effect_state["smiley_spawn_timer"] > random.randint(250, 450):
        effect_state["smiley_spawn_timer"] = 0
        spawn_smiley()

    remaining = []
    for s in effect_state["smileys"]:
        s["x"] -= s["speed"]
        cx, cy, r = int(s["x"]), int(s["y"]), s["radius"]
        pygame.draw.circle(screen, (255, 230, 0), (cx, cy), r)
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r, 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx - r // 3, cy - r // 4), r // 6)
        pygame.draw.circle(screen, (0, 0, 0), (cx + r // 3, cy - r // 4), r // 6)
        smile_rect = pygame.Rect(cx - r // 2, cy, r, r // 2)
        pygame.draw.arc(screen, (0, 0, 0), smile_rect, math.pi, 2 * math.pi, 2)

        smiley_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        if smiley_rect.colliderect(bird_rect_ref):
            game_over = True

        if s["x"] > -r * 2:
            remaining.append(s)
    effect_state["smileys"] = remaining

#Level 8: Castle Oblivion
def spawn_beam():
    effect_state["beams"].append({
        "x": random.randint(60, WIDTH - 60),
        "timer": 0,
        "width": random.randint(20, 50),
        "life": random.randint(30, 60),
    })

def update_draw_beams(bird_rect_ref):
    global game_over
    effect_state["beam_spawn_timer"] += 1
    if effect_state["beam_spawn_timer"] > random.randint(200, 400):
        effect_state["beam_spawn_timer"] = 0
        spawn_beam()

    remaining = []
    for beam in effect_state["beams"]:
        beam["timer"] += 1
        progress = beam["timer"] / beam["life"]
        alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        s = pygame.Surface((beam["width"], FLOOR_Y), pygame.SRCALPHA)
        s.fill((255, 255, 255, alpha))
        screen.blit(s, (beam["x"] - beam["width"] // 2, 0))

        beam_rect = pygame.Rect(beam["x"] - beam["width"] // 2, 0, beam["width"], FLOOR_Y)
        if beam_rect.colliderect(bird_rect_ref):
            game_over = True

        if beam["timer"] < beam["life"]:
            remaining.append(beam)
    effect_state["beams"] = remaining

#Level 9: Space
def spawn_asteroid():
    effect_state["asteroids"].append({
        "x": WIDTH + 50,
        "y": random.randint(60, FLOOR_Y - 60),
        "radius": random.randint(18, 40),
        "speed": random.uniform(2, 5),
        "angle": 0,
        "rot_speed": random.uniform(-3, 3),
    })

def update_draw_asteroids(bird_rect_ref):
    global game_over
    effect_state["asteroid_spawn_timer"] += 1
    if effect_state["asteroid_spawn_timer"] > random.randint(240, 480):
        effect_state["asteroid_spawn_timer"] = 0
        spawn_asteroid()

    remaining = []
    for ast in effect_state["asteroids"]:
        ast["x"] -= ast["speed"]
        ast["angle"] += ast["rot_speed"]
        cx, cy, r = int(ast["x"]), int(ast["y"]), ast["radius"]
        pts = []
        for i in range(8):
            ang = ast["angle"] + i * (360 / 8)
            rad = math.radians(ang)
            dist = r + random.randint(-r // 4, r // 4)
            pts.append((cx + math.cos(rad) * dist, cy + math.sin(rad) * dist))
        pygame.draw.polygon(screen, (130, 110, 90), pts)
        pygame.draw.polygon(screen, (80, 70, 60), pts, 2)

        ast_rect = pygame.Rect(cx - r, cy - r, r * 2, r * 2)
        if ast_rect.colliderect(bird_rect_ref):
            game_over = True

        if ast["x"] > -r * 2:
            remaining.append(ast)
    effect_state["asteroids"] = remaining

def draw_star_trail(bird_center):
    for _ in range(3):
        sx = bird_center[0] - random.randint(8, 28)
        sy = bird_center[1] + random.randint(-8, 8)
        r = random.randint(2, 5)
        col = random.choice([(255, 255, 180), (255, 255, 80), (200, 200, 255)])
        pygame.draw.circle(screen, col, (sx, sy), r)

#Level 10: Black Hole
def spawn_black_hole():
    from_top = random.choice([True, False])
    effect_state["black_holes"].append({
        "x": random.randint(80, WIDTH - 80),
        "y": 30 if from_top else FLOOR_Y - 30,
        "radius": random.randint(35, 65),
        "pull_radius": 120,
        "timer": 0,
        "life": random.randint(300, 500),
        "from_top": from_top,
    })

def update_draw_black_holes(bird_rect_ref, bird_movement_ref):
    """Returns a movement delta to apply to bird (gravitational pull)."""
    effect_state["bh_spawn_timer"] += 1
    if effect_state["bh_spawn_timer"] > random.randint(200, 350):
        effect_state["bh_spawn_timer"] = 0
        spawn_black_hole()

    effect_state["blink_timer"] += 1
    if not effect_state["blink_active"]:
        if effect_state["blink_timer"] >= effect_state["blink_next"]:
            effect_state["blink_active"] = True
            effect_state["blink_timer"] = 0
    else:
        screen.fill((0, 0, 0))
        if effect_state["blink_timer"] >= 8:
            effect_state["blink_active"] = False
            effect_state["blink_timer"] = 0
            effect_state["blink_next"] = random.randint(120, 300)

    dy_total = 0
    remaining = []
    for bh in effect_state["black_holes"]:
        bh["timer"] += 1
        cx, cy, r = int(bh["x"]), int(bh["y"]), bh["radius"]
        t = pygame.time.get_ticks()
        for ring in range(3):
            ring_r = r + ring * 18 + int(6 * math.sin(t / 200 + ring))
            alpha = max(0, 180 - ring * 50)
            s = pygame.Surface((ring_r * 2, ring_r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (60, 0, 80, alpha), (ring_r, ring_r), ring_r, 3)
            screen.blit(s, (cx - ring_r, cy - ring_r))
        pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r)

        dx = cx - bird_rect_ref.centerx
        dy = cy - bird_rect_ref.centery
        dist = math.hypot(dx, dy)
        if dist < bh["pull_radius"] and dist > 0:
            pull = 0.5 * (1 - dist / bh["pull_radius"])
            dy_total += pull * (dy / dist)

        if bh["timer"] < bh["life"]:
            remaining.append(bh)
    effect_state["black_holes"] = remaining
    return dy_total

#Level 11: Heaven
def draw_golden_pulse():
    t = pygame.time.get_ticks()
    alpha = int(40 + 30 * math.sin(t / 400))
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    s.fill((255, 230, 100, alpha))
    screen.blit(s, (0, 0))

#Level 12: Retro
def draw_scanlines():
    effect_state["scanline_offset"] = (effect_state["scanline_offset"] + 1) % 4
    s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for y in range(effect_state["scanline_offset"], HEIGHT, 4):
        pygame.draw.line(s, (0, 0, 0, 60), (0, y), (WIDTH, y))
    screen.blit(s, (0, 0))

def apply_level_effects_pre_pipes():
    """Called after background draw, before pipes — returns (shake_x, shake_y)."""
    if current_level == 2:
        update_draw_vines(bird_rect)
        return update_jungle_shake()
    if current_level == 3:
        draw_heat_waves()
        return update_heat_shake()
    if current_level == 4:
        draw_snowflakes()
    if current_level == 5:
        draw_bubbles()
    if current_level == 11:
        draw_golden_pulse()
    return (0, 0)

def apply_level_effects_post_bird(bird_surface_ref, bird_rect_ref, bird_movement_ref):
    """Called after bird is drawn — returns movement delta."""
    dy_extra = 0

    if current_level == 1:
        t = pygame.time.get_ticks()
        pulse_alpha = 90 + int(45 * math.sin(t / 200))

        mask = pygame.mask.from_surface(bird_surface_ref)
        outline = mask.outline()

        if outline:
            padding = 16

            glow_surf = pygame.Surface(
                (bird_rect_ref.width + padding * 2, bird_rect_ref.height + padding * 2),
                pygame.SRCALPHA
            )

            offset_outline = [(x + padding, y + padding) for x, y in outline]

            for thickness in range(10, 2, -2):
                pygame.draw.lines(
                    glow_surf,
                    (255, 20, 60, max(15, pulse_alpha - thickness * 7)),
                    True,
                    offset_outline,
                    thickness
                )

            pygame.draw.lines(
                glow_surf,
                (255, 0, 0, 210),
                True,
                offset_outline,
                2
            )

            screen.blit(
                glow_surf,
                (bird_rect_ref.x - padding, bird_rect_ref.y - padding)
            )

    if current_level == 3:
        draw_ember_trail(bird_rect_ref.center)

    if current_level == 4:
        draw_frost_trail(bird_rect_ref.center)
        dx = update_wind(bird_movement_ref)
        bird_rect_ref.centerx += dx
        bird_rect_ref.centerx = max(0, min(WIDTH, bird_rect_ref.centerx))

    if current_level == 5:
        dy_extra = update_buoyancy(bird_movement_ref)

    if current_level == 6:
        update_draw_gas_clouds(bird_rect_ref)

    if current_level == 7:
        update_draw_smileys(bird_rect_ref)

    if current_level == 8:
        update_draw_beams(bird_rect_ref)

    if current_level == 9:
        draw_star_trail(bird_rect_ref.center)
        update_draw_asteroids(bird_rect_ref)

    if current_level == 10:
        dy_extra = update_draw_black_holes(bird_rect_ref, bird_movement_ref)

    if current_level == 12:
        draw_scanlines()

    return dy_extra

#LEVEL TRANSITION
def compute_level(score):
    if score < LEVEL_SCORE_THRESHOLDS[1]:
        return 0
    if score < LEVEL_SCORE_THRESHOLDS[2]:
        return 1
    return min(2 + ((score - LEVEL_SCORE_THRESHOLDS[2]) // 100), MAX_LEVEL)

def start_level_transition(new_level):
    global pending_level, transition_timer

    pending_level = new_level
    transition_timer = LEVEL_TRANSITION_FRAMES

def transition_to_level(new_level):
    global current_level, current_birds, bird_img, bird_rect, current_pipe_spawn_interval
    global back_img, ground_fill_color, current_pipe_variants
    global pipes

    current_level = new_level
    current_birds = try_load_bird_frames(new_level)
    bird_img = current_birds[bird_index]
    bird_rect = bird_img.get_rect(center=bird_rect.center)
    back_img = try_load_background(new_level)
    current_pipe_variants = try_load_pipe_variants(new_level)
    pipes = []
    ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))
    try_play_music(new_level)
    reset_effect_state()

    current_pipe_spawn_interval = get_level_spawn_interval(new_level)
    pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)

#GAME RESET
def reset_game():
    global bird_rect, bird_movement, pipes, game_over, game_started
    global current_level, current_birds, bird_img, back_img, current_pipe_spawn_interval
    global ground_fill_color, current_pipe_variants, pending_level, transition_timer

    pipes = []
    bird_movement = 0
    game_over = False
    game_started = False
    pending_level = None
    transition_timer = 0
    score_tracker["score"] = 0

    current_level = 0
    current_birds = try_load_bird_frames(0)
    bird_img = current_birds[0]
    bird_rect = bird_img.get_rect(center=(BIRD_START_X, BIRD_START_Y))
    back_img = try_load_background(0)
    current_pipe_variants = try_load_pipe_variants(0)
    ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))
    try_play_music(0)
    reset_effect_state()

    current_pipe_spawn_interval = get_level_spawn_interval(0)
    pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)

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

#ASSET LOAD
back_img = try_load_background(0)
floor_img = scale_image(trim_top_edge(load_image("floor_img.png"), 3), (WIDTH, FLOOR_HEIGHT))
pipe_img = load_gameplay_sprite("pipe_img.webp", (PIPE_WIDTH, PIPE_HEIGHT))
pipe_mask = pygame.mask.from_surface(pipe_img)
top_pipe_img = pygame.transform.flip(pipe_img, False, True)
top_pipe_mask = pygame.mask.from_surface(top_pipe_img)
over_img = load_gameplay_sprite("game_over.png", (GAME_OVER_WIDTH, 116))
vine_img = trim_sprite(load_image("Vines.png", alpha=True))

current_level = 0
current_pipe_variants = try_load_pipe_variants(0)
current_birds = try_load_bird_frames(0)
bird_index = 0
bird_img = current_birds[bird_index]
bird_rect = bird_img.get_rect(center=(BIRD_START_X, BIRD_START_Y))
bird_movement = 0

bird_flap = pygame.USEREVENT
create_pipe = pygame.USEREVENT + 1
current_pipe_spawn_interval = BASE_PIPE_SPAWN_INTERVAL
pygame.time.set_timer(bird_flap, 200)
pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)

pipes = []
floor_x = 0
game_over = False
game_started = False
pending_level = None
transition_timer = 0
score_tracker = {"score": 0, "high_score": 0}
score_font = pygame.font.Font("freesansbold.ttf", 27)
prompt_font = pygame.font.Font("freesansbold.ttf", 24)
over_rect = over_img.get_rect(midtop=(WIDTH // 2, GAME_OVER_TOP))
ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))

reset_effect_state()

class SilentSound:
    def play(self):
        return None

score_point = SilentSound()

#MAIN LOOP
running = True
while running:
    clock.tick(120)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not game_started:
                game_started = True
                bird_movement = FLAP_STRENGTH
            elif not game_over:
                bird_movement = FLAP_STRENGTH
            else:
                reset_game()
                game_started = True
                bird_movement = FLAP_STRENGTH

        if event.type == bird_flap:
            bird_index = (bird_index + 1) % len(current_birds)
            bird_img, bird_rect = animate_bird()

        if event.type == create_pipe and game_started and not game_over:
            pipes.append(create_pipes())

    if transition_timer > 0:
        transition_timer -= 1
        if transition_timer == LEVEL_TRANSITION_FRAMES // 2 and pending_level is not None:
            transition_to_level(pending_level)
        if transition_timer == 0:
            pending_level = None
    else:
        new_level = compute_level(score_tracker["score"])
        if new_level != current_level:
            start_level_transition(new_level)

    screen.blit(back_img, (0, 0))

    shake_x, shake_y = (0, 0)
    if game_started and not game_over and transition_timer == 0:
        shake_x, shake_y = apply_level_effects_pre_pipes()

    if shake_x or shake_y:
        view_surf = screen.copy()
        screen.blit(view_surf, (shake_x, shake_y))

    if game_started and not game_over and transition_timer == 0:
        gravity = get_level_gravity(current_level)
        bird_speed_multiplier = get_level_bird_speed_multiplier(current_level)
        bird_movement += gravity * bird_speed_multiplier
        bird_rect.centery += bird_movement * bird_speed_multiplier
        rotated_bird = rotate_bird(bird_img)
        rotated_bird_rect = rotated_bird.get_rect(center=bird_rect.center)
        screen.blit(rotated_bird, rotated_bird_rect)

        dy_extra = apply_level_effects_post_bird(rotated_bird, rotated_bird_rect, bird_movement)
        if dy_extra:
            bird_movement += dy_extra

        if current_level != 10:
            move_and_draw_pipes(rotated_bird, rotated_bird_rect)

        update_score()
        draw_score("game_on")

        if bird_rect.top <= -20 or bird_rect.bottom >= FLOOR_Y:
            game_over = True
            bird_rect.bottom = min(bird_rect.bottom, FLOOR_Y)
    elif game_started and not game_over:
        screen.blit(bird_img, bird_rect)
        draw_existing_pipes()
        draw_score("game_on")
    elif not game_started:
        screen.blit(bird_img, bird_rect)
        draw_score("welcome")
    else:
        screen.blit(bird_img, bird_rect)
        screen.blit(over_img, over_rect)
        draw_score("game_over")

    floor_x -= 1
    if floor_x <= -floor_img.get_width():
        floor_x = 0
    draw_floor()
    draw_level_transition()

    pygame.display.update()

pygame.quit()
sys.exit()
