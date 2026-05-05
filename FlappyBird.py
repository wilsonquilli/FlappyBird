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
POINTS_PER_PIPE = 10
BIRD_START_X = 160
BIRD_START_Y = HEIGHT // 2 - 40
BIRD_SIZE = (68, 48)
PIPE_WIDTH = 150
PIPE_HEIGHT = 620
PIPE_PATTERN_MAX_STEP = 120  
SKY_PIPE_GAP = 200
SKY_PIPE_PATTERN_MAX_STEP = 145
SKY_PIPE_JITTER = 16
SKY_PIPE_CENTER_PATTERN = (
    0.50, 0.31, 0.68, 0.42,
    0.60, 0.26, 0.74, 0.47,
    0.34, 0.66, 0.39, 0.57,
)
GAME_OVER_WIDTH = 360
GAME_OVER_TOP = 180
LEVEL_TRANSITION_FRAMES = 75
PIPE_MARGIN_TOP = 110
PIPE_MARGIN_BOTTOM = 110
ICY_WIND_INTERVAL_FRAMES = 720  
ICY_WIND_WARNING_FRAMES = 150    
ICY_WIND_DURATION_FRAMES = 72   
ICY_WIND_PUSH = -0.9           
ICY_WIND_WARNING_IMAGE = "Warning.png"
TOXIC_HAZARD_IMAGE = "Hazard.png"
TOXIC_CLOUD_MIN_RADIUS = 48
TOXIC_CLOUD_MAX_RADIUS = 82
MEMBER_WEAPON_MEMBERS = tuple(range(1, 14))
SPINNING_WEAPON_MEMBERS = {6, 7, 10, 11}
MEMBER_WEAPON_MAX_SIZE = (118, 118)
MEMBER_LASER_MAX_SIZE = (150, 58)
MEMBER_WEAPON_PAIR_SPAWN_MIN_FRAMES = 210
MEMBER_WEAPON_PAIR_SPAWN_MAX_FRAMES = 340
MEMBER_WEAPON_SPEED_MIN = 3.1
MEMBER_WEAPON_SPEED_MAX = 4.7
CHECKRAM_IMAGE_NAMES = ("Chekrams.png", "Chekrams.png")
CHECKRAM_SIZE = (112, 112)
ASTEROID_IMAGE = "Asteroid.png"
ASTEROID_SIZE_RANGE = (72, 128)
ASTEROID_SPEED_MIN = 6.8
ASTEROID_SPEED_MAX = 9.0
ASTEROID_PAIR_SPAWN_MIN_FRAMES = 165
ASTEROID_PAIR_SPAWN_MAX_FRAMES = 260
BLACK_HOLE_IMAGE = "Black_Hole.png"
BLACK_HOLE_SIZE = (230, 140)
BLACK_HOLE_PAIR_SPAWN_MIN_FRAMES = 145
BLACK_HOLE_PAIR_SPAWN_MAX_FRAMES = 230
BLACK_HOLE_SPEED_MIN = 3.1
BLACK_HOLE_SPEED_MAX = 4.6
BLACK_HOLE_PULL_RADIUS = 230
BLACK_HOLE_PULL_STRENGTH = 1.15
BLACK_HOLE_KILL_DISTANCE = 38
BLACK_HOLE_BLINK_DURATION = 24
KEYBLADE_PIPE_VARIANT_CACHE = None
ASSET_DIR = Path(__file__).resolve().parent
IMAGE_DIR = ASSET_DIR / "images"
MUSIC_DIR = ASSET_DIR / "music"
VIDEO_DIR = ASSET_DIR / "videos"
IMAGE_SEARCH_DIRS = (
    ASSET_DIR,
    IMAGE_DIR,
    IMAGE_DIR / "assets",
    IMAGE_DIR / "backgrounds",
    IMAGE_DIR / "bird_models",
    IMAGE_DIR / "floors",
    IMAGE_DIR / "pipe_images",
)

#LEVEL CONFIG
SCORE_PER_LEVEL = 50
MAX_LEVEL = 12  # 0-11 = normal…black-hole, 12 = retro final
FINAL_CLEAR_SCORE = (MAX_LEVEL + 1) * SCORE_PER_LEVEL
HAPPY_ENDING_VIDEO_NAME = "flappy_bird_happy_ending.mp4"
CREDITS_VIDEO_NAME = "credits.mp4"
ENDING_MUSIC_NAME = "Ending_Music.mp3"
VIDEO_EXTENSIONS = (".mp4",)
FINISH_FLAG_IMAGE = "Finish_Flag.png"
FINISH_FLAG_SIZE = (90, 90)
FINAL_PIPE_SCORE = FINAL_CLEAR_SCORE - POINTS_PER_PIPE

LEVEL_MUSIC = {
    0: "FB-BG-music.mp3",
    1: "Neon_City_Music.mp3",      
    2: "Jungle_Theme.mp3",           
    3: "Volcano_Lava_Theme.mp3",         
    4: "Ice_Snow_Theme.mp3",              
    5: "Ocean_Theme.mp3",           
    6: "Toxic_Lab_Theme.mp3",         
    7: "Backrooms_Theme.mp3",       
    8: "Castle_Oblivion_Theme.mp3",           
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
    6: "Toxic_Lab_Background.png",            
    7: "Backrooms_Background.png",         
    8: "Castle_Oblivion_Background.png",             
    9: "Space_Background.jpg",               
    10: "Black_Hole_Background.jpg",         
    11: "Sky_Background.jpg",             
    12: "Retro_Background.jpg",              
}

LEVEL_FLOORS = {
    0: "floor_img.png",
    1: "Neon_City_Floor.png",
    2: "Jungle_Floor.png",
    3: "Volcano_Floor.png",
    4: "Icy_Floor.png",
    5: "Ocean_Floor.png",
    6: "Toxic_Floor.png",
    7: "Backrooms_Floor.png",
    8: "Castle_Oblivion_Floor.png",
    9: "Space_Floor.png",
    10: "Black_Hole_Floor.png",
    11: "Sky_Floor.png",
    12: "floor_img.png", 
}

LEVEL_BIRD_FRAMES = {
    0: ("bird_up.jpg", "bird_mid.png", "bird_down.jpeg"),
    1: ("Cyber_Bird_Up.png", "Cyber_Bird_Mid.png", "Cyber_Bird_Down.png"),   
    2: ("Scarlet_Macaw_Up.png", "Scarlet_Macaw_Mid.png", "Scarlet_Macaw_Down.png"),
    3: ("Flame_Bird_Up.png", "Flame_Bird_Mid.png", "Flame_Bird_Down.png"),   
    4: ("Frost_Bird_Up.png", "Frost_Bird_Mid.png", "Frost_Bird_Down.png"),   
    5: ("Ocellaris_Clownfish_Up.png", "Ocellaris_Clownfish_Mid.png", "Ocellaris_Clownfish_Down.png"),
    6: ("Toxic_Bird_Up.png", "Toxic_Bird_Mid.png", "Toxic_Bird_Down.png"),   
    7: ("Backrooms_Bird_Up.png", "Backrooms_Bird_Mid.png", "Backrooms_Bird_Down.png"),  
    8: ("Darkness_Bird_Up.png", "Darkness_Bird_Mid.png", "Darkness_Bird_Down.png"),   
    9: ("Star_Bird_Up.png", "Star_Bird_Mid.png", "Star_Bird_Down.png"),    
    10: ("Glitch_Bird_Up.png", "Glitch_Bird_Mid.png", "Glitch_Bird_Down.png"),
    11: ("Angel_Bird_Up.png", "Angel_Bird_Mid.png", "Angel_Bird_Down.png"),
    12: ("Retro_Bird_Up.png", "Retro_Bird_Mid.png", "Retro_Bird_Down.png"),     
}

LEVEL_PIPE_VARIANTS = {
    0: ("pipe_img.webp",),
    1: ("Neon_Building_Pipe.png",),
    2: ("Jungle_Tree_Pipe.png",),
    3: ("Volcano_Pipe.png",),
    4: ("Icy_Mountain.png",),
    5: ("Sand_Castle.png",),
    6: ("Toxic_Beaker.png",),
    7: ("Backrooms_Pipe.png",),
    8: ("Keyblade.png",),
    9: ("Space_Pipe.png",),
    11: ("Golden_Pipe.png",),
}

LEVEL_NAMES = {
    0: "Normal",
    1: "Neon City",
    2: "Jungle",
    3: "Volcano",
    4: "Ice / Snow",
    5: "Ocean",
    6: "Toxic Lab",
    7: "Backrooms",
    8: "Castle Oblivion",
    9: "Space",
    10: "Black Hole",
    11: "Sky / Heaven",
    12: "Retro",
}

LEVEL_MECHANICS = {
    0: "Classic Flappy Bird gameplay. Pass through pipes to score.",
    1: "Neon City is faster. Pipes move quicker and your bird reacts faster.",
    2: "Jungle has swinging vines. Avoid vines while passing through wider gaps.",
    3: "Volcano has heat distortion and screen shake. Stay focused through the lava chaos.",
    4: "Ice has wind gusts. Watch for the wind warning before the bird gets pushed left.",
    5: "Ocean has lower gravity and buoyancy. The bird floats more than usual.",
    6: "Toxic Lab has poison clouds. Avoid the toxic gas hazards.",
    7: "Backrooms has creepy smiley enemies. Dodge them while flying through pipes.",
    8: "Castle Oblivion has Organization weapon attacks. Avoid the weapons flying across the screen.",
    9: "Space has low gravity and asteroids. Dodge asteroid pairs while controlling floaty movement.",
    10: "Black Hole has gravity wells. Black holes suck you in, so do not get too close.",
    11: "Sky has smaller pipe gaps and a tougher pipe pattern. Stay ready for sudden gap changes.",
    12: "Retro is the final challenge. Everything moves much faster.",
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
        recursive_match = next(IMAGE_DIR.rglob(filename), None)
        if recursive_match is not None:
            path = recursive_match
    if path is None:
        raise FileNotFoundError(f"Unable to locate image asset '{filename}' in {IMAGE_SEARCH_DIRS}")
    image = pygame.image.load(str(path))
    return image.convert_alpha() if alpha else image.convert()

def scale_image(image, size):
    return pygame.transform.smoothscale(image, size)

def fit_sprite_to_box(image, box_size):
    """Scale a sprite into a box while preserving its original shape."""
    width, height = image.get_size()
    box_width, box_height = box_size
    if width <= 0 or height <= 0:
        return pygame.Surface((1, 1), pygame.SRCALPHA)
    scale = min(box_width / width, box_height / height)
    scaled_size = (max(1, int(width * scale)), max(1, int(height * scale)))
    return scale_image(image, scaled_size)

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

def clean_wind_warning_image(image):
    """Remove the warning sprite's exported background and make it pop more."""
    cleaned = image.convert_alpha()
    cleaned = remove_bright_background_from_edges(cleaned, threshold=220)
    cleaned = remove_background_from_edges(cleaned, tolerance=95)

    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_background_like(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 42
        return brightness >= 210 or brightness <= 35 or (grayish and brightness >= 120)

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
        if alpha == 0:
            pass
        elif is_background_like(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    for x in range(width):
        for y in range(height):
            red, green, blue, alpha = cleaned.get_at((x, y))
            if alpha == 0:
                continue
            red = min(255, int(red * 1.28) + 18)
            green = min(255, int(green * 1.28) + 18)
            blue = min(255, int(blue * 1.28) + 18)
            alpha = min(255, int(alpha * 1.25))
            cleaned.set_at((x, y), (red, green, blue, alpha))

    return trim_alpha_sprite(cleaned)

def clean_hazard_image(image):
    """Remove the hazard icon export background so only the symbol appears."""
    cleaned = image.convert_alpha()
    cleaned = remove_bright_background_from_edges(cleaned, threshold=230)

    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_hazard_background(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 28
        return brightness >= 218 and grayish

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
        if alpha == 0:
            pass
        elif is_hazard_background(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    return trim_alpha_sprite(cleaned)


def clean_weapon_image(image):
    """Remove exported image backgrounds and trim to the real weapon pixels.
    This handles member weapon sprites like Member_1_Weapon/Xemnas shots where
    the original file may have a white, gray, black, or transparent canvas. The
    flood fill only removes background-like pixels connected to the outside
    edges, so internal weapon colors/details are kept.
    """
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_weapon_background(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 42
        return (
            brightness >= 214 or
            brightness <= 24 or
            (grayish and brightness >= 150)
        )

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
        if alpha == 0:
            pass
        elif is_weapon_background(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    for _ in range(2):
        to_clear = []
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = cleaned.get_at((x, y))
                if alpha == 0 or not is_weapon_background(red, green, blue):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and cleaned.get_at((nx, ny))[3] == 0:
                        to_clear.append((x, y, red, green, blue))
                        break
        if not to_clear:
            break
        for x, y, red, green, blue in to_clear:
            cleaned.set_at((x, y), (red, green, blue, 0))

    return trim_alpha_sprite(cleaned)

def member_weapon_candidate_names(member):
    names = [
        f"Member_{member}_Weapon.png",
        f"Member_{member}_Weapon.PNG",
        f"Member_{member}_Weapon.webp",
        f"Member_{member}_Weapon.jpg",
        f"Member_{member}_Weapon.jpeg",
        f"Member_{member:02d}_Weapon.png",
        f"Member {member} Weapon.png",
    ]
    if member == 1:
        names.extend([
            "Xemnas_Shot.png",
            "Xemnas_Shots.png",
            "Xemnas_Weapon.png",
            "Xemnas_Laser.png",
        ])
    return names

def load_member_weapon_surface(member):
    for filename in member_weapon_candidate_names(member):
        try:
            image = load_image(filename, alpha=True)
            image = clean_weapon_image(image)
            if image.get_width() <= 1 or image.get_height() <= 1:
                continue
            max_size = MEMBER_LASER_MAX_SIZE if member == 1 else MEMBER_WEAPON_MAX_SIZE
            return trim_alpha_sprite(fit_sprite_to_box(image, max_size))
        except Exception:
            continue
    return None

def try_load_member_weapon_images():
    weapons = []
    for member in MEMBER_WEAPON_MEMBERS:
        surface = load_member_weapon_surface(member)
        if surface is not None:
            weapons.append({
                "member": member,
                "surface": surface,
                "spins": member in SPINNING_WEAPON_MEMBERS,
            })

    if not weapons:
        for filename in CHECKRAM_IMAGE_NAMES:
            try:
                image = load_image(filename, alpha=True)
                image = clean_weapon_image(image)
                surface = trim_alpha_sprite(fit_sprite_to_box(image, CHECKRAM_SIZE))
                weapons.append({"member": 8, "surface": surface, "spins": False})
                break
            except Exception:
                continue
    return weapons

def clean_black_hole_image(image):
    """Remove the exported white/gray background from Black_Hole.png.
    Only edge-connected background pixels are cleared, then the sprite is
    alpha-trimmed. The gameplay mask is made from this cleaned surface, so the
    white canvas around the art never becomes part of the hitbox.
    """
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_black_hole_background(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 30
        return grayish and brightness >= 228

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
        if alpha == 0:
            pass
        elif is_black_hole_background(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    for _ in range(2):
        to_clear = []
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = cleaned.get_at((x, y))
                if alpha == 0 or not is_black_hole_background(red, green, blue):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and cleaned.get_at((nx, ny))[3] == 0:
                        to_clear.append((x, y, red, green, blue))
                        break
        if not to_clear:
            break
        for x, y, red, green, blue in to_clear:
            cleaned.set_at((x, y), (red, green, blue, 0))

    return trim_alpha_sprite(cleaned)

def load_black_hole_image(filename):
    image = load_image(filename, alpha=True)
    image = clean_black_hole_image(image)
    return trim_alpha_sprite(fit_sprite_to_box(image, BLACK_HOLE_SIZE))

def remove_black_background_from_edges(image, threshold=18):
    """Make only edge-connected black background pixels transparent.
    This is used for Vines.png. The vine art is dark green, so we only remove
    nearly-black pixels that connect to the outside of the image instead of
    deleting dark pixels inside the actual vine.
    """
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
        if alpha == 0:
            pass
        elif red <= threshold and green <= threshold and blue <= threshold:
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    return cleaned

def load_vine_image(filename):
    image = load_image(filename, alpha=True)
    image = remove_black_background_from_edges(image, threshold=18)
    return trim_alpha_sprite(image)

def trim_alpha_sprite(image, alpha_threshold=8):
    source = image.convert_alpha()
    points = []
    for x in range(source.get_width()):
        for y in range(source.get_height()):
            if source.get_at((x, y))[3] > alpha_threshold:
                points.append((x, y))
    if not points:
        return source
    left = min(x for x, _ in points)
    right = max(x for x, _ in points) + 1
    top = min(y for _, y in points)
    bottom = max(y for _, y in points) + 1
    return source.subsurface((left, top, right - left, bottom - top)).copy()

def clean_finish_flag_image(image):
    """Remove only the edge-connected checker/export background from the finish flag.
    This keeps the white squares/details inside the flag intact because those
    pixels are enclosed by the black flag art and are not connected to the
    outside image edges.
    """
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_finish_flag_bg(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 20
        return grayish and brightness >= 180

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
        if alpha == 0:
            pass
        elif is_finish_flag_bg(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    return trim_alpha_sprite(cleaned)

def load_finish_flag_image(filename):
    image = load_image(filename, alpha=True)
    image = clean_finish_flag_image(image)
    return trim_alpha_sprite(fit_sprite_to_box(image, FINISH_FLAG_SIZE))

def remove_checker_background_from_edges(image):
    """Remove only the edge-connected checker/export background from Asteroid.png.
    This keeps the asteroid, black outline, and fire intact while deleting the
    light gray/white checkerboard canvas that was exported behind the sprite.
    """
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()
    visited = set()
    queue = deque()

    def is_checker_bg(red, green, blue):
        brightness = (red + green + blue) / 3
        grayish = max(red, green, blue) - min(red, green, blue) <= 18
        return grayish and brightness >= 185

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
        if alpha == 0:
            pass
        elif is_checker_bg(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    for _ in range(2):
        to_clear = []
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = cleaned.get_at((x, y))
                if alpha == 0 or not is_checker_bg(red, green, blue):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and cleaned.get_at((nx, ny))[3] == 0:
                        to_clear.append((x, y, red, green, blue))
                        break
        if not to_clear:
            break
        for x, y, red, green, blue in to_clear:
            cleaned.set_at((x, y), (red, green, blue, 0))

    return cleaned

def load_asteroid_image(filename):
    image = load_image(filename, alpha=True)
    image = remove_checker_background_from_edges(image)
    return trim_alpha_sprite(image)

def asteroid_touches_bird(asteroid_surface, asteroid_rect, bird_surface_ref, bird_rect_ref):
    if not bird_rect_ref.colliderect(asteroid_rect):
        return False

    bird_mask = pygame.mask.from_surface(bird_surface_ref)
    asteroid_mask = pygame.mask.from_surface(asteroid_surface)
    offset = (bird_rect_ref.left - asteroid_rect.left, bird_rect_ref.top - asteroid_rect.top)
    return asteroid_mask.overlap(bird_mask, offset) is not None

def remove_floor_background_and_outline(image):
    """Remove edge-connected white/gray/black boxes and thin halos from floor art.
    Only pixels connected to the outside edges are removed first, so the actual
    floor artwork stays intact while exported canvas backgrounds/outlines vanish.
    """
    cleaned = image.convert_alpha()
    width, height = cleaned.get_size()

    def is_grayish(red, green, blue):
        return max(red, green, blue) - min(red, green, blue) <= 38

    def is_unwanted_floor_bg(red, green, blue):
        brightness = (red + green + blue) / 3
        return (
            brightness >= 215 or      
            brightness <= 42 or       
            (is_grayish(red, green, blue) and (brightness >= 120 or brightness <= 95))
        )

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
        if alpha == 0:
            pass
        elif is_unwanted_floor_bg(red, green, blue):
            cleaned.set_at((x, y), (red, green, blue, 0))
        else:
            continue

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                queue.append((nx, ny))

    for _ in range(2):
        to_clear = []
        for x in range(width):
            for y in range(height):
                red, green, blue, alpha = cleaned.get_at((x, y))
                if alpha == 0 or not is_unwanted_floor_bg(red, green, blue):
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height and cleaned.get_at((nx, ny))[3] == 0:
                        to_clear.append((x, y, red, green, blue))
                        break
        if not to_clear:
            break
        for x, y, red, green, blue in to_clear:
            cleaned.set_at((x, y), (red, green, blue, 0))

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


def crop_single_sprite_frame(image):
    """If an obstacle image is a vertical sprite sheet, crop it down to one frame.
    Some obstacle files, especially Icy_Mountain.png, can contain several copies
    stacked vertically in one image. If we scale that whole sheet, it looks like
    multiple mountains stacked on top of each other. This extracts one usable
    sprite before scaling it into a pipe-sized obstacle.
    """
    source = image.convert_alpha()
    width, height = source.get_size()

    occupied_rows = []
    for y in range(height):
        has_pixel = False
        for x in range(width):
            if source.get_at((x, y))[3] > 10:
                has_pixel = True
                break
        if has_pixel:
            occupied_rows.append(y)

    bands = []
    if occupied_rows:
        start = prev = occupied_rows[0]
        for y in occupied_rows[1:]:
            if y <= prev + 1:
                prev = y
            else:
                bands.append((start, prev))
                start = prev = y
        bands.append((start, prev))

    usable_bands = [(top, bottom) for top, bottom in bands if bottom - top + 1 >= 12]
    if len(usable_bands) >= 2:
        top, bottom = max(usable_bands, key=lambda band: band[1] - band[0])
        return source.subsurface((0, top, width, bottom - top + 1)).copy()

    if height > width * 2.0:
        estimated_frames = max(2, round(height / max(1, width)))
        frame_height = max(1, height // estimated_frames)
        return source.subsurface((0, 0, width, frame_height)).copy()

    return source

def crop_largest_alpha_component(image, alpha_threshold=10):
    """Keep only the largest connected visible sprite in an obstacle image.
    Castle Oblivion's Keyblade asset can export as multiple stacked copies in
    one transparent canvas. Scaling that whole canvas creates an impossible
    wall. This keeps one actual keyblade sprite and removes the extra copies,
    while still preserving pixel-perfect collision masks for the remaining art.
    """
    source = image.convert_alpha()
    width, height = source.get_size()
    visited = set()
    largest_pixels = []

    for start_x in range(width):
        for start_y in range(height):
            if (start_x, start_y) in visited:
                continue

            visited.add((start_x, start_y))
            if source.get_at((start_x, start_y))[3] <= alpha_threshold:
                continue

            pixels = []
            queue = deque([(start_x, start_y)])

            while queue:
                x, y = queue.popleft()
                pixels.append((x, y))

                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < width and 0 <= ny < height):
                        continue
                    if (nx, ny) in visited:
                        continue

                    visited.add((nx, ny))
                    if source.get_at((nx, ny))[3] > alpha_threshold:
                        queue.append((nx, ny))

            if len(pixels) > len(largest_pixels):
                largest_pixels = pixels

    if not largest_pixels:
        return source

    left = max(0, min(x for x, _ in largest_pixels) - 2)
    right = min(width, max(x for x, _ in largest_pixels) + 3)
    top = max(0, min(y for _, y in largest_pixels) - 2)
    bottom = min(height, max(y for _, y in largest_pixels) + 3)

    component = pygame.Surface((right - left, bottom - top), pygame.SRCALPHA)
    for x, y in largest_pixels:
        component.set_at((x - left, y - top), source.get_at((x, y)))

    return trim_alpha_sprite(component)

def build_keyblade_surface(*, flipped=False):
    """Build one clean Keyblade using the same pipe box behavior as other levels.
    The Keyblade image is still cleaned down to one visible sprite so it cannot
    stack after restarting, but the final art is scaled to the full pipe-sized
    surface instead of being centered with empty padding. That keeps the
    Keyblade tips aligned with the playable gap like the normal pipe pairs.
    """
    sprite = load_image("Keyblade.png", alpha=True)
    sprite = remove_background_from_edges(sprite)
    sprite = trim_alpha_sprite(sprite)
    sprite = crop_single_sprite_frame(sprite)
    sprite = crop_largest_alpha_component(sprite)
    sprite = trim_alpha_sprite(sprite)

    if flipped:
        sprite = pygame.transform.flip(sprite, False, True)

    sprite_width, sprite_height = sprite.get_size()
    if sprite_width <= 0 or sprite_height <= 0:
        return pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)

    return scale_image(sprite, (PIPE_WIDTH, PIPE_HEIGHT))

def build_golden_pipe_surface(*, flipped=False):
    """Build Level 11 gold pipes without the transparent T-shaped cutouts.
    The uploaded Golden_Pipe.png is shaped like a T: the cap is wide, but the
    long shaft is narrower with transparent space on both sides. When the whole
    T image is scaled into the pipe box, those transparent side areas look like
    the pipe is cut off. This rebuilds the pipe as a full-width shaft plus a
    cap at the playable gap edge, while still using the colors/details from the
    uploaded image.
    """
    sprite = load_image("Golden_Pipe.png", alpha=True)
    sprite = trim_alpha_sprite(sprite)
    width, height = sprite.get_size()

    alpha_threshold = 8
    row_bounds = []
    for y in range(height):
        xs = [x for x in range(width) if sprite.get_at((x, y))[3] > alpha_threshold]
        if xs:
            row_bounds.append((y, min(xs), max(xs), len(xs)))

    if not row_bounds:
        return pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)

    max_row_width = max(bounds[3] for bounds in row_bounds)
    top_visible_y = row_bounds[0][0]

    cap_bottom_y = top_visible_y
    for y, left, right, row_width in row_bounds:
        if y < top_visible_y + 8 or row_width >= max_row_width * 0.82:
            cap_bottom_y = y
        else:
            break

    body_rows = [bounds for bounds in row_bounds if bounds[0] > cap_bottom_y and bounds[3] > max_row_width * 0.20]
    if not body_rows:
        body_rows = row_bounds

    body_top = min(bounds[0] for bounds in body_rows)
    body_bottom = max(bounds[0] for bounds in body_rows)
    body_left = min(bounds[1] for bounds in body_rows)
    body_right = max(bounds[2] for bounds in body_rows)

    cap_crop = sprite.subsurface((0, 0, width, max(1, cap_bottom_y + 1))).copy()
    body_crop = sprite.subsurface((body_left, body_top, body_right - body_left + 1, body_bottom - body_top + 1)).copy()

    pipe_surface = pygame.Surface((PIPE_WIDTH, PIPE_HEIGHT), pygame.SRCALPHA)

    body_surface = scale_image(body_crop, (PIPE_WIDTH, PIPE_HEIGHT))
    pipe_surface.blit(body_surface, (0, 0))

    cap_height = max(74, min(112, int(PIPE_WIDTH * 0.60)))
    cap_surface = scale_image(cap_crop, (PIPE_WIDTH, cap_height))
    pipe_surface.blit(cap_surface, (0, 0))

    if flipped:
        pipe_surface = pygame.transform.flip(pipe_surface, False, True)

    return pipe_surface

def build_obstacle_surface(filename, *, flipped=False, remove_bg=True):
    """Build every themed obstacle inside the exact same pipe-sized box."""
    if filename == "Keyblade.png":
        return build_keyblade_surface(flipped=flipped)
    if filename == "Golden_Pipe.png":
        return build_golden_pipe_surface(flipped=flipped)

    sprite = load_image(filename, alpha=True)
    if remove_bg:
        if filename.startswith("Neon_Building_"):
            sprite = remove_bright_background_from_edges(sprite, threshold=220)
            sprite = remove_background_from_edges(sprite, tolerance=95)
        else:
            sprite = remove_background_from_edges(sprite)
        sprite = trim_sprite(sprite)

    sprite = crop_single_sprite_frame(sprite)
    if flipped:
        sprite = pygame.transform.flip(sprite, False, True)

    pipe_width = PIPE_WIDTH
    if current_level == 9 and filename == "Space_Pipe.png":
        pipe_width = int(PIPE_WIDTH * 0.7)  

    return scale_image(sprite, (pipe_width, PIPE_HEIGHT))

def build_pipe_variant(filename):
    global KEYBLADE_PIPE_VARIANT_CACHE

    if filename == "pipe_img.webp":
        image = load_gameplay_sprite(filename, (PIPE_WIDTH, PIPE_HEIGHT))
        top_image = pygame.transform.flip(image, False, True)
    elif filename == "Keyblade.png":
        if KEYBLADE_PIPE_VARIANT_CACHE is None:
            bottom = build_obstacle_surface(filename, flipped=False, remove_bg=True)
            top = build_obstacle_surface(filename, flipped=True, remove_bg=True)
            KEYBLADE_PIPE_VARIANT_CACHE = {
                "bottom": bottom,
                "bottom_mask": pygame.mask.from_surface(bottom),
                "top": top,
                "top_mask": pygame.mask.from_surface(top),
            }
        return KEYBLADE_PIPE_VARIANT_CACHE
    else:
        image = build_obstacle_surface(filename, flipped=False, remove_bg=True)
        top_image = build_obstacle_surface(filename, flipped=True, remove_bg=True)
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

def try_load_background(level):
    filename = LEVEL_BACKGROUNDS.get(level, LEVEL_BACKGROUNDS[0])
    fallback = LEVEL_BACKGROUNDS[0]
    try:
        image = load_image(filename)
    except Exception:
        image = load_image(fallback)
    return scale_image(image, (WIDTH, HEIGHT))

def derive_floor_fill_color(image, fallback_color=(76, 64, 54)):
    """Pick a stable solid color that sits behind transparent floor edges."""
    source = image.convert_alpha()
    width, height = source.get_size()
    start_y = max(0, height - max(12, height // 4))
    candidates = []

    for y in range(start_y, height):
        for x in range(width):
            red, green, blue, alpha = source.get_at((x, y))
            if alpha < 170:
                continue
            brightness = (red + green + blue) / 3
            grayish = max(red, green, blue) - min(red, green, blue) <= 26
            if brightness >= 235:
                continue
            if brightness <= 12:
                continue
            if grayish and brightness >= 210:
                continue
            candidates.append((red, green, blue))

    if not candidates:
        return fallback_color

    red = sum(color[0] for color in candidates) // len(candidates)
    green = sum(color[1] for color in candidates) // len(candidates)
    blue = sum(color[2] for color in candidates) // len(candidates)
    return (red, green, blue)

def try_load_floor(level):
    filename = LEVEL_FLOORS.get(level, LEVEL_FLOORS[0])
    fallback = LEVEL_FLOORS[0]

    try:
        image = load_image(filename, alpha=True)
    except Exception:
        try:
            image = load_image(fallback, alpha=True)
        except Exception:
            image = pygame.Surface((WIDTH, FLOOR_HEIGHT), pygame.SRCALPHA)
            image.fill((120, 90, 55, 255))
            return image

    image = trim_top_edge(image, 3)
    image = remove_floor_background_and_outline(image)
    image = scale_image(image, (WIDTH, FLOOR_HEIGHT))
    return remove_floor_background_and_outline(image)

def try_load_bird_frames(level):
    frame_names = LEVEL_BIRD_FRAMES.get(level, LEVEL_BIRD_FRAMES[0])
    frames = []
    for name in frame_names:
        try:
            frames.append(load_bird_frame(name))
        except Exception:
            continue

    if not frames:
        for fallback_name in LEVEL_BIRD_FRAMES[0]:
            frames.append(load_bird_frame(fallback_name))

    return frames

def try_play_music(level):
    if not pygame.mixer.get_init():
        return

    filename = LEVEL_MUSIC.get(level, LEVEL_MUSIC[0])
    path = MUSIC_DIR / filename
    if not path.exists():
        path = MUSIC_DIR / LEVEL_MUSIC[0]

    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

def play_ending_music():
    if not pygame.mixer.get_init():
        return

    path = MUSIC_DIR / ENDING_MUSIC_NAME

    if not path.exists():
        for extension in (".mp3", ".wav", ".ogg"):
            candidate = MUSIC_DIR / f"Ending Music{extension}"
            if candidate.exists():
                path = candidate
                break

    if not path.exists():
        print(f"Ending music not found: {path}")
        return

    try:
        pygame.mixer.music.load(str(path))
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except pygame.error:
        pass

def find_video_file(video_name):
    """Find a video in the videos folder by name, with or without extension."""
    direct_path = VIDEO_DIR / video_name
    if direct_path.exists():
        return direct_path

    for extension in VIDEO_EXTENSIONS:
        candidate = VIDEO_DIR / f"{video_name}{extension}"
        if candidate.exists():
            return candidate

    return None

def play_video(video_path):
    """Play an ending video safely. Returns 'finished', 'quit', or 'failed'."""
    try:
        import cv2
    except ImportError:
        print("OpenCV is not installed. Install it with: pip install opencv-python")
        return "failed"

    if not video_path or not video_path.exists():
        print(f"Ending video not found: {video_path}")
        return "failed"

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Could not open ending video: {video_path}")
        return "failed"

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30

    video_clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                return "quit"

        success, frame = cap.read()
        if not success:
            break

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_surface = pygame.image.frombuffer(
            frame.tobytes(),
            (frame.shape[1], frame.shape[0]),
            "RGB"
        )

        frame_surface = pygame.transform.smoothscale(frame_surface, (WIDTH, HEIGHT))
        screen.blit(frame_surface, (0, 0))
        pygame.display.update()
        video_clock.tick(fps)

    cap.release()
    return "finished"

def play_happy_ending_video():
    video_path = find_video_file(HAPPY_ENDING_VIDEO_NAME)
    return play_video(video_path)

def play_credits_video():
    video_path = find_video_file(CREDITS_VIDEO_NAME)
    return play_video(video_path)

#PIPE SPEED / GRAVITY PER LEVEL
def get_level_pipe_speed(level):
    if level == 1:
        return BASE_PIPE_SPEED * 1.25
    if level == 5:
        return BASE_PIPE_SPEED * 0.8
    if level == 11:
        return BASE_PIPE_SPEED * 1.15
    if level == 12:
        return BASE_PIPE_SPEED * 2.0
    return BASE_PIPE_SPEED

def get_level_bird_speed_multiplier(level):
    if level == 1:
        return 1.25
    return 1.0

def get_level_gravity(level):
    if level == 9:
        return BASE_GRAVITY * 0.65        
    if level == 5:
        return BASE_GRAVITY * 0.75        
    return BASE_GRAVITY

def get_level_pipe_gap(level):
    if level == 2:
        return 400
    if level == 5:   
        return 270   
    if level == 9:  
        return 270   
    if level == 11:
        return SKY_PIPE_GAP
    return PIPE_GAP

def get_level_spawn_interval(level):
    if level == 1:
        return int(BASE_PIPE_SPAWN_INTERVAL / 1.25)
    if level == 5:
        return int(BASE_PIPE_SPAWN_INTERVAL / 0.8)
    if level == 11:
        return int(BASE_PIPE_SPAWN_INTERVAL / 1.18)
    if level == 12:
        return int(BASE_PIPE_SPAWN_INTERVAL / 2.0)
    return BASE_PIPE_SPAWN_INTERVAL

#DRAWING HELPERS
def draw_floor():
    pygame.draw.rect(screen, floor_fill_color, (0, FLOOR_Y, WIDTH, FLOOR_HEIGHT))
    screen.blit(floor_img, (floor_x, FLOOR_Y))
    screen.blit(floor_img, (floor_x + floor_img.get_width(), FLOOR_Y))

def draw_text_with_outline(text, font, color, outline_color, center_pos):
    base = font.render(text, True, color)
    outline = font.render(text, True, outline_color)

    rect = base.get_rect(center=center_pos)

    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-2,-2),(2,-2),(-2,2),(2,2)]:
        screen.blit(outline, rect.move(dx, dy))

    screen.blit(base, rect)

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
        draw_text_with_outline(
            f"Score: {int(score_tracker['score'])}",
            score_font,
            (255, 255, 255),   
            (0, 0, 0),        
            (WIDTH // 2, 80)
        )

        draw_text_with_outline(
            f"High Score: {int(score_tracker['high_score'])}",
            score_font,
            (255, 255, 255),
            (0, 0, 0),
            (WIDTH // 2, 125)
        )   

        draw_text_with_outline(
            "Press Space to go Again",
            prompt_font,
            (255, 255, 255),
            (0, 0, 0),
            (WIDTH // 2, 170)
        )

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

def draw_level_intro_screen():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 165))
    screen.blit(overlay, (0, 0))

    level_name = LEVEL_NAMES.get(current_level, f"Level {current_level}")
    title_text = score_font.render(f"Level {current_level}: {level_name}", True, (255, 230, 120))
    screen.blit(title_text, title_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 115)))

    mechanic = LEVEL_MECHANICS.get(current_level, "Survive the level and keep scoring.")
    words = mechanic.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if prompt_font.size(test_line)[0] <= 620:
            current_line = test_line
        else:
            lines.append(current_line.strip())
            current_line = word + " "

    if current_line:
        lines.append(current_line.strip())

    start_y = HEIGHT // 2 - 45
    for index, line in enumerate(lines):
        line_surface = prompt_font.render(line, True, (255, 255, 255))
        screen.blit(line_surface, line_surface.get_rect(center=(WIDTH // 2, start_y + index * 34)))

    continue_text = prompt_font.render("Press Space to Continue", True, (160, 255, 160))
    screen.blit(continue_text, continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 115)))

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
    global last_pipe_gap_center, sky_pipe_pattern_index

    gap = int(get_level_pipe_gap(current_level))
    pipe_center_min = int(PIPE_MARGIN_TOP + gap // 2)
    pipe_center_max = int(FLOOR_Y - PIPE_MARGIN_BOTTOM - gap // 2)

    if pipe_center_min > pipe_center_max:
        pipe_center_min = gap // 2 + 20
        pipe_center_max = FLOOR_Y - gap // 2 - 20

    if current_level == 11:
        pattern_value = SKY_PIPE_CENTER_PATTERN[sky_pipe_pattern_index % len(SKY_PIPE_CENTER_PATTERN)]
        sky_pipe_pattern_index += 1

        target_center = pipe_center_min + int((pipe_center_max - pipe_center_min) * pattern_value)
        target_center += random.randint(-SKY_PIPE_JITTER, SKY_PIPE_JITTER)

        if last_pipe_gap_center is None:
            gap_center = max(pipe_center_min, min(pipe_center_max, target_center))
        else:
            low = max(pipe_center_min, int(last_pipe_gap_center - SKY_PIPE_PATTERN_MAX_STEP))
            high = min(pipe_center_max, int(last_pipe_gap_center + SKY_PIPE_PATTERN_MAX_STEP))
            gap_center = max(low, min(high, target_center))
    elif last_pipe_gap_center is None:
        gap_center = random.randint(pipe_center_min, pipe_center_max)
    else:
        low = max(pipe_center_min, int(last_pipe_gap_center - PIPE_PATTERN_MAX_STEP))
        high = min(pipe_center_max, int(last_pipe_gap_center + PIPE_PATTERN_MAX_STEP))
        gap_center = random.randint(low, high)

    gap_center = int(gap_center)
    last_pipe_gap_center = gap_center

    variant_index = random.randrange(len(current_pipe_variants))
    variant = current_pipe_variants[variant_index]

    bottom_pipe = variant["bottom"].get_rect(midtop=(PIPE_SPAWN_X, gap_center + gap // 2))
    top_pipe = variant["top"].get_rect(midbottom=(PIPE_SPAWN_X, gap_center - gap // 2))

    return {
        "top": top_pipe,
        "bottom": bottom_pipe,
        "scored": False,
        "variant_index": variant_index,
        "show_finish_flag": False,
    }

def collides_with_pipe(bird_surface, bird_surface_rect, pipe_rect, pipe_mask):
    if not bird_surface_rect.colliderect(pipe_rect):
        return False
    bird_mask = pygame.mask.from_surface(bird_surface)
    offset = (pipe_rect.left - bird_surface_rect.left, pipe_rect.top - bird_surface_rect.top)
    return bird_mask.overlap(pipe_mask, offset) is not None

def move_and_draw_pipes(bird_surface, bird_surface_rect):
    global game_over

    pipe_speed = get_level_pipe_speed(current_level)
    remaining = []
    scored_this_frame = False
    update_finish_flag_target()

    for pipe_pair in pipes:
        if not isinstance(pipe_pair, dict):
            continue

        variant = current_pipe_variants[pipe_pair.get("variant_index", 0) % len(current_pipe_variants)]

        top_pipe = pipe_pair["top"]
        bottom_pipe = pipe_pair["bottom"]
        previous_centerx = pipe_pair.get("previous_centerx", bottom_pipe.centerx)

        top_pipe.centerx -= pipe_speed
        bottom_pipe.centerx -= pipe_speed

        if current_level == 1:
            draw_pipe_neon(top_pipe, bottom_pipe, variant)
        else:
            screen.blit(variant["top"], top_pipe)
            screen.blit(variant["bottom"], bottom_pipe)
        draw_finish_flag_for_pipe(pipe_pair)

        top_hit = collides_with_pipe(
                bird_surface,
                bird_surface_rect,
                top_pipe,
                variant["top_mask"]
            )

        bottom_hit = collides_with_pipe(
                bird_surface,
                bird_surface_rect,
                bottom_pipe,
                variant["bottom_mask"]
            )

        if top_hit or bottom_hit:
            game_over = True

        if top_pipe.right > -variant["bottom"].get_width():
            remaining.append(pipe_pair)

        crossed_bird = previous_centerx >= bird_rect.centerx and bottom_pipe.centerx < bird_rect.centerx
        if not pipe_pair["scored"] and crossed_bird:
            if not scored_this_frame:
                score_point.play()
                score_tracker["score"] += POINTS_PER_PIPE
                scored_this_frame = True
            pipe_pair["scored"] = True

        pipe_pair["previous_centerx"] = bottom_pipe.centerx

    pipes[:] = remaining

def draw_existing_pipes():
    update_finish_flag_target()

    for pipe_pair in pipes:
        if not isinstance(pipe_pair, dict):
            continue
        variant = current_pipe_variants[pipe_pair.get("variant_index", 0) % len(current_pipe_variants)]
        screen.blit(variant["top"], pipe_pair["top"])
        screen.blit(variant["bottom"], pipe_pair["bottom"])
        draw_finish_flag_for_pipe(pipe_pair)

def should_show_finish_flag():
    return (
        current_level == MAX_LEVEL
        and not happy_ending_played
        and score_tracker["score"] == FINAL_PIPE_SCORE
    )

def update_finish_flag_target():
    for pipe_pair in pipes:
        if isinstance(pipe_pair, dict):
            pipe_pair["show_finish_flag"] = False

    if not should_show_finish_flag():
        return

    upcoming_pairs = [
        pipe_pair for pipe_pair in pipes
        if isinstance(pipe_pair, dict)
        and not pipe_pair.get("scored", False)
        and pipe_pair["bottom"].right >= bird_rect.left - 8
    ]

    if upcoming_pairs:
        target_pair = min(upcoming_pairs, key=lambda pair: pair["bottom"].centerx)
        target_pair["show_finish_flag"] = True


def draw_finish_flag_for_pipe(pipe_pair):
    if finish_flag_img is None or not pipe_pair.get("show_finish_flag", False):
        return

    anchor_x = pipe_pair["bottom"].left + min(52, pipe_pair["bottom"].width // 2)
    anchor_y = pipe_pair["bottom"].top - 4
    flag_rect = finish_flag_img.get_rect(midbottom=(anchor_x, anchor_y))
    screen.blit(finish_flag_img, flag_rect)

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
    effect_state["wind_warning"] = False
    effect_state["wind_timer"] = 0
    effect_state["wind_cycle_timer"] = 0
    effect_state["wind_next"] = ICY_WIND_INTERVAL_FRAMES
    effect_state["wind_push_x"] = float(BIRD_START_X)
    effect_state["buoy_timer"] = 0
    effect_state["buoy_next"] = random.randint(120, 240)
    effect_state["gas_clouds"] = []
    effect_state["gas_spawn_timer"] = 0
    effect_state["smileys"] = []
    effect_state["smiley_spawn_timer"] = 0
    effect_state["beams"] = []
    effect_state["beam_spawn_timer"] = 0
    effect_state["member_weapons"] = []
    effect_state["member_weapon_spawn_timer"] = 0
    effect_state["member_weapon_next_spawn"] = random.randint(
        MEMBER_WEAPON_PAIR_SPAWN_MIN_FRAMES,
        MEMBER_WEAPON_PAIR_SPAWN_MAX_FRAMES,
    )
    effect_state["asteroids"] = []
    effect_state["asteroid_spawn_timer"] = 0
    effect_state["black_holes"] = []
    effect_state["bh_spawn_timer"] = 0
    effect_state["bh_next_spawn"] = random.randint(
        BLACK_HOLE_PAIR_SPAWN_MIN_FRAMES,
        BLACK_HOLE_PAIR_SPAWN_MAX_FRAMES,
    )
    effect_state["bh_pair_id"] = 0
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

def build_vine_surface_and_rect(vine, base_x, base_y, tip_x, tip_y):
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

    return rotated_vine, vine_rect

def bird_touches_vine_pixels(vine_surface, vine_rect, bird_rect_ref):
    if not bird_rect_ref.colliderect(vine_rect):
        return False

    bird_mask = pygame.mask.from_surface(bird_img)
    vine_mask = pygame.mask.from_surface(vine_surface)
    offset = (bird_rect_ref.left - vine_rect.left, bird_rect_ref.top - vine_rect.top)
    return vine_mask.overlap(bird_mask, offset) is not None

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

        vine_surface, vine_rect = build_vine_surface_and_rect(vine, base_x, base_y, tip_x, tip_y)
        screen.blit(vine_surface, vine_rect)

        if bird_touches_vine_pixels(vine_surface, vine_rect, bird_rect_ref):
            game_over = True
        if vine_rect.right > -120:
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
    """Stronger lava heat shimmer: visibly warps screen strips and adds hot-air bands."""
    t = pygame.time.get_ticks()
    original = screen.copy()

    band_height = 6
    amplitude = 11
    for y in range(0, FLOOR_Y, band_height):
        offset = int(amplitude * math.sin((t / 105) + y * 0.07))
        strip = original.subsurface((0, y, WIDTH, band_height)).copy()
        screen.blit(strip, (offset, y))

        if offset > 0:
            screen.blit(strip, (offset - WIDTH, y))
        elif offset < 0:
            screen.blit(strip, (offset + WIDTH, y))

    for y in range(0, FLOOR_Y, 24):
        offset = int(amplitude * math.sin((t / 130) + y * 0.08))
        heat_color = (255, 90, 0, 70)
        s = pygame.Surface((WIDTH, 4), pygame.SRCALPHA)
        s.fill(heat_color)
        screen.blit(s, (offset, y))

    glow = pygame.Surface((WIDTH, FLOOR_Y), pygame.SRCALPHA)
    glow.fill((255, 55, 0, 24))
    screen.blit(glow, (0, 0))

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
    """Level 4 icy wind cycle: warning, shove, cooldown, repeat."""
    effect_state["wind_cycle_timer"] += 1

    warning_start = max(0, effect_state["wind_next"] - ICY_WIND_WARNING_FRAMES)

    if not effect_state["wind_active"]:
        effect_state["wind_warning"] = (
            warning_start <= effect_state["wind_cycle_timer"] < effect_state["wind_next"]
        )

        if effect_state["wind_cycle_timer"] >= effect_state["wind_next"]:
            effect_state["wind_active"] = True
            effect_state["wind_warning"] = False
            effect_state["wind_timer"] = 0
    else:
        effect_state["wind_timer"] += 1

        if effect_state["wind_timer"] >= ICY_WIND_DURATION_FRAMES:
            effect_state["wind_active"] = False
            effect_state["wind_warning"] = False
            effect_state["wind_timer"] = 0
            effect_state["wind_cycle_timer"] = 0
            effect_state["wind_next"] = ICY_WIND_INTERVAL_FRAMES

    return ICY_WIND_PUSH if effect_state["wind_active"] else 0

def draw_wind_warning():
    """Draw the Level 4 avalanche warning without any circle/background glow."""
    if not effect_state.get("wind_warning"):
        return

    t = pygame.time.get_ticks()
    alpha = 215 + int(40 * abs(math.sin(t / 120)))

    if wind_warning_img is not None:
        warning = wind_warning_img.copy()
        warning.set_alpha(alpha)
        rect = warning.get_rect(center=(WIDTH // 2, 135))
        screen.blit(warning, rect)

        warning_text = "WIND WARNING"
        text_alpha = 220 + int(35 * abs(math.sin(t / 120)))
        text_surface = prompt_font.render(warning_text, True, (255, 245, 80))
        outline_surface = prompt_font.render(warning_text, True, (20, 35, 55))
        text_surface.set_alpha(text_alpha)
        outline_surface.set_alpha(text_alpha)

        text_rect = text_surface.get_rect(center=(WIDTH // 2, rect.bottom + 24))
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)):
            screen.blit(outline_surface, text_rect.move(ox, oy))
        screen.blit(text_surface, text_rect)
    else:
        warning = pygame.Surface((170, 92), pygame.SRCALPHA)
        pygame.draw.polygon(warning, (255, 245, 40, alpha), [(85, 4), (166, 88), (4, 88)])
        pygame.draw.polygon(warning, (20, 20, 20, alpha), [(85, 4), (166, 88), (4, 88)], 5)
        pygame.draw.line(warning, (20, 20, 20, alpha), (85, 30), (85, 58), 8)
        pygame.draw.circle(warning, (20, 20, 20, alpha), (85, 73), 5)
        rect = warning.get_rect(center=(WIDTH // 2, 135))
        screen.blit(warning, rect)

        warning_text = "AVALANCHE WARNING"
        text_surface = prompt_font.render(warning_text, True, (255, 245, 80))
        outline_surface = prompt_font.render(warning_text, True, (20, 35, 55))
        text_rect = text_surface.get_rect(center=(WIDTH // 2, rect.bottom + 24))
        for ox, oy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, -2), (-2, 2), (2, 2)):
            screen.blit(outline_surface, text_rect.move(ox, oy))
        screen.blit(text_surface, text_rect)

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
    radius = random.randint(TOXIC_CLOUD_MIN_RADIUS, TOXIC_CLOUD_MAX_RADIUS)
    center_y = random.randint(radius + 10, 135) if from_top else random.randint(FLOOR_Y - 135, FLOOR_Y - radius - 10)
    puffs = [
        (0.00, 0.00, 1.00),
        (-0.55, -0.05, 0.72),
        (0.55, -0.03, 0.76),
        (-0.28, -0.42, 0.62),
        (0.28, -0.45, 0.66),
        (-0.18, 0.42, 0.58),
        (0.22, 0.38, 0.54),
    ]

    effect_state["gas_clouds"].append({
        "x": WIDTH + radius + 35,
        "y": center_y,
        "radius": radius,
        "alpha": random.randint(150, 200),
        "from_top": from_top,
        "puffs": puffs,
        "wobble": random.uniform(0, math.pi * 2),
    })

def draw_toxic_cloud_surface(cloud):
    radius = cloud["radius"]
    padding = int(radius * 0.55)
    size = radius * 2 + padding * 2
    center = size // 2
    surface = pygame.Surface((size, size), pygame.SRCALPHA)

    for ox, oy, scale in cloud["puffs"]:
        puff_radius = max(8, int(radius * scale))
        px = int(center + ox * radius)
        py = int(center + oy * radius)
        pygame.draw.circle(surface, (5, 72, 20, cloud["alpha"] - 35), (px, py), puff_radius)
        pygame.draw.circle(surface, (0, 145, 45, max(70, cloud["alpha"] - 75)), (px, py), max(5, int(puff_radius * 0.72)))

    pygame.draw.circle(surface, (0, 45, 15, 105), (center, center), int(radius * 0.92))
    pygame.draw.circle(surface, (95, 255, 70, 42), (center - int(radius * 0.25), center - int(radius * 0.28)), int(radius * 0.45))

    if hazard_img is not None:
        icon_size = max(34, int(radius * 1.05))
        icon = scale_image(hazard_img, (icon_size, icon_size))
        icon.set_alpha(230)
        surface.blit(icon, icon.get_rect(center=(center, center)))
    else:
        pygame.draw.circle(surface, (255, 235, 0, 220), (center, center), int(radius * 0.42))
        pygame.draw.circle(surface, (5, 5, 5, 230), (center, center), int(radius * 0.42), 4)
        pygame.draw.circle(surface, (5, 5, 5, 230), (center, center), int(radius * 0.11))

    return surface

def update_draw_gas_clouds(bird_rect_ref):
    global game_over
    effect_state["gas_spawn_timer"] += 1
    if effect_state["gas_spawn_timer"] > random.randint(180, 300):
        effect_state["gas_spawn_timer"] = 0
        spawn_gas_cloud()

    remaining = []
    for cloud in effect_state["gas_clouds"]:
        cloud["x"] -= 2
        cloud["wobble"] += 0.04
        cloud_y = cloud["y"] + math.sin(cloud["wobble"]) * 2

        cloud_surface = draw_toxic_cloud_surface(cloud)
        cloud_rect = cloud_surface.get_rect(center=(int(cloud["x"]), int(cloud_y)))
        screen.blit(cloud_surface, cloud_rect)

        hit_radius = int(cloud["radius"] * 0.92)
        hit_rect = pygame.Rect(
            int(cloud["x"] - hit_radius),
            int(cloud_y - hit_radius),
            hit_radius * 2,
            hit_radius * 2,
        )
        if hit_rect.colliderect(bird_rect_ref):
            game_over = True

        if cloud_rect.right > -120:
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
def spawn_member_weapon_pair():
    top_y = random.randint(95, max(120, FLOOR_Y // 2 - 95))
    bottom_y = random.randint(min(FLOOR_Y - 105, FLOOR_Y // 2 + 95), FLOOR_Y - 95)
    base_speed = random.uniform(MEMBER_WEAPON_SPEED_MIN, MEMBER_WEAPON_SPEED_MAX)

    for y, drift in ((top_y, 0.55), (bottom_y, -0.55)):
        weapon_index = random.randrange(len(member_weapon_images)) if member_weapon_images else -1
        weapon_data = member_weapon_images[weapon_index] if weapon_index >= 0 else None
        should_spin = bool(weapon_data and weapon_data.get("spins"))
        effect_state["member_weapons"].append({
            "x": WIDTH + 85,
            "y": y,
            "speed": base_speed + random.uniform(-0.25, 0.25),
            "angle": random.uniform(0, 360) if should_spin else 0,
            "rot_speed": random.choice([-1, 1]) * random.uniform(4.0, 7.0) if should_spin else 0,
            "drift": drift,
            "phase": random.uniform(0, math.pi * 2),
            "weapon_index": weapon_index,
        })


def member_weapon_touches_bird(weapon_surface, weapon_rect, bird_surface_ref, bird_rect_ref):
    if not bird_rect_ref.colliderect(weapon_rect):
        return False

    bird_mask = pygame.mask.from_surface(bird_surface_ref)
    weapon_mask = pygame.mask.from_surface(weapon_surface)
    offset = (bird_rect_ref.left - weapon_rect.left, bird_rect_ref.top - weapon_rect.top)
    return weapon_mask.overlap(bird_mask, offset) is not None


def build_fallback_member_weapon():
    surface = pygame.Surface((104, 36), pygame.SRCALPHA)
    pygame.draw.rect(surface, (210, 20, 30), (8, 8, 88, 20), border_radius=10)
    pygame.draw.rect(surface, (255, 115, 120), (18, 12, 58, 6), border_radius=3)
    return surface

def update_draw_member_weapons(bird_surface_ref, bird_rect_ref):
    global game_over
    effect_state["member_weapon_spawn_timer"] += 1
    if effect_state["member_weapon_spawn_timer"] >= effect_state["member_weapon_next_spawn"]:
        effect_state["member_weapon_spawn_timer"] = 0
        effect_state["member_weapon_next_spawn"] = random.randint(
            MEMBER_WEAPON_PAIR_SPAWN_MIN_FRAMES,
            MEMBER_WEAPON_PAIR_SPAWN_MAX_FRAMES,
        )
        spawn_member_weapon_pair()

    remaining = []
    for weapon in effect_state["member_weapons"]:
        weapon["x"] -= weapon["speed"]
        weapon["phase"] += 0.045
        weapon["angle"] += weapon["rot_speed"]
        draw_y = weapon["y"] + math.sin(weapon["phase"]) * 10 + weapon["drift"]

        weapon_data = None
        if member_weapon_images and 0 <= weapon.get("weapon_index", -1) < len(member_weapon_images):
            weapon_data = member_weapon_images[weapon["weapon_index"]]

        base_surface = weapon_data["surface"] if weapon_data is not None else build_fallback_member_weapon()
        if weapon_data is not None and weapon_data.get("spins"):
            draw_surface = pygame.transform.rotate(base_surface, weapon["angle"])
        else:
            draw_surface = base_surface

        draw_surface = trim_alpha_sprite(draw_surface)
        rect = draw_surface.get_rect(center=(int(weapon["x"]), int(draw_y)))
        screen.blit(draw_surface, rect)

        if member_weapon_touches_bird(draw_surface, rect, bird_surface_ref, bird_rect_ref):
            game_over = True

        if rect.right > -120:
            remaining.append(weapon)

    effect_state["member_weapons"] = remaining

def update_draw_checkrams(bird_surface_ref, bird_rect_ref):
    update_draw_member_weapons(bird_surface_ref, bird_rect_ref)

#Level 9: Space
def spawn_asteroid_pair():
    top_size = random.randint(ASTEROID_SIZE_RANGE[0], ASTEROID_SIZE_RANGE[1])
    bottom_size = random.randint(ASTEROID_SIZE_RANGE[0], ASTEROID_SIZE_RANGE[1])
    top_y = random.randint(top_size // 2 + 35, max(top_size // 2 + 40, FLOOR_Y // 2 - 90))
    bottom_y = random.randint(min(FLOOR_Y - bottom_size // 2 - 35, FLOOR_Y // 2 + 90), FLOOR_Y - bottom_size // 2 - 35)
    base_speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)

    for y, size, x_offset in ((top_y, top_size, 0), (bottom_y, bottom_size, random.randint(35, 115))):
        effect_state["asteroids"].append({
            "x": WIDTH + size + x_offset,
            "y": y,
            "size": size,
            "speed": base_speed + random.uniform(-0.35, 0.35),
            "angle": 0,
            "rot_speed": 0,
        })

def spawn_asteroid():
    spawn_asteroid_pair()

def update_draw_asteroids(bird_surface_ref, bird_rect_ref):
    global game_over

    if not effect_state["asteroids"]:
        spawn_asteroid_pair()
        effect_state["asteroid_spawn_timer"] = 0

    effect_state["asteroid_spawn_timer"] += 1
    if effect_state["asteroid_spawn_timer"] >= random.randint(ASTEROID_PAIR_SPAWN_MIN_FRAMES, ASTEROID_PAIR_SPAWN_MAX_FRAMES):
        effect_state["asteroid_spawn_timer"] = 0
        spawn_asteroid_pair()

    remaining = []
    for ast in effect_state["asteroids"]:
        ast["x"] -= ast["speed"]

        if asteroid_img is not None:
            asteroid_surface = scale_image(asteroid_img, (ast["size"], ast["size"]))
        else:
            r = ast["size"] // 2
            asteroid_surface = pygame.Surface((ast["size"], ast["size"]), pygame.SRCALPHA)
            pygame.draw.circle(asteroid_surface, (130, 85, 45), (r, r), r)
            pygame.draw.circle(asteroid_surface, (40, 25, 15), (r, r), r, 4)

        asteroid_rect = asteroid_surface.get_rect(center=(int(ast["x"]), int(ast["y"])))
        screen.blit(asteroid_surface, asteroid_rect)

        if asteroid_touches_bird(asteroid_surface, asteroid_rect, bird_surface_ref, bird_rect_ref):
            game_over = True

        if asteroid_rect.right > -120:
            remaining.append(ast)
    effect_state["asteroids"] = remaining

def draw_star_trail(bird_center):
    for _ in range(3):
        sx = bird_center[0] - random.randint(8, 28)
        sy = bird_center[1] + random.randint(-8, 8)
        r = random.randint(2, 5)
        col = random.choice([(255, 255, 180), (255, 255, 80), (200, 200, 255)])
        pygame.draw.circle(screen, col, (sx, sy), r)

#Level 10: Black Hole / Chaos
def spawn_black_hole_pair():
    """Spawn a top/bottom pair that replaces pipes on Level 10."""
    effect_state["bh_pair_id"] += 1
    pair_id = effect_state["bh_pair_id"]
    base_speed = random.uniform(BLACK_HOLE_SPEED_MIN, BLACK_HOLE_SPEED_MAX)
    top_y = 78
    bottom_y = FLOOR_Y - 78
    x_offset = random.randint(0, 70)

    for from_top, y in ((True, top_y), (False, bottom_y)):
        effect_state["black_holes"].append({
            "x": WIDTH + 125 + x_offset,
            "y": y,
            "speed": base_speed + random.uniform(-0.18, 0.18),
            "pull_radius": BLACK_HOLE_PULL_RADIUS,
            "timer": 0,
            "from_top": from_top,
            "pair_id": pair_id,
            "scored": False,
            "previous_x": WIDTH + 125 + x_offset,
            "wobble": random.uniform(0, math.pi * 2),
        })

def spawn_black_hole():
    spawn_black_hole_pair()

def black_hole_touches_bird(black_hole_surface, black_hole_rect, bird_surface_ref, bird_rect_ref):
    if not bird_rect_ref.colliderect(black_hole_rect):
        return False

    bird_mask = pygame.mask.from_surface(bird_surface_ref)
    black_hole_mask = pygame.mask.from_surface(black_hole_surface)
    offset = (bird_rect_ref.left - black_hole_rect.left, bird_rect_ref.top - black_hole_rect.top)
    return black_hole_mask.overlap(bird_mask, offset) is not None


def build_fallback_black_hole_surface():
    surface = pygame.Surface(BLACK_HOLE_SIZE, pygame.SRCALPHA)
    cx, cy = BLACK_HOLE_SIZE[0] // 2, BLACK_HOLE_SIZE[1] // 2
    pygame.draw.ellipse(surface, (255, 120, 0, 230), (4, cy - 28, BLACK_HOLE_SIZE[0] - 8, 56), 8)
    pygame.draw.circle(surface, (0, 0, 0, 255), (cx, cy), 36)
    pygame.draw.circle(surface, (255, 220, 40, 180), (cx, cy), 48, 5)
    return surface

def update_draw_black_holes(bird_surface_ref, bird_rect_ref, bird_movement_ref):
    """Draw Level 10 black holes and pull the bird toward nearby holes."""
    global game_over, bird_rect

    if not effect_state["black_holes"]:
        spawn_black_hole_pair()
        effect_state["bh_spawn_timer"] = 0

    effect_state["bh_spawn_timer"] += 1
    if effect_state["bh_spawn_timer"] >= effect_state["bh_next_spawn"]:
        effect_state["bh_spawn_timer"] = 0
        effect_state["bh_next_spawn"] = random.randint(
            BLACK_HOLE_PAIR_SPAWN_MIN_FRAMES,
            BLACK_HOLE_PAIR_SPAWN_MAX_FRAMES,
        )
        spawn_black_hole_pair()

    effect_state["blink_timer"] += 1
    if not effect_state["blink_active"]:
        if effect_state["blink_timer"] >= effect_state["blink_next"]:
            effect_state["blink_active"] = True
            effect_state["blink_timer"] = 0
    else:
        screen.fill((0, 0, 0))
        if effect_state["blink_timer"] >= BLACK_HOLE_BLINK_DURATION:
            effect_state["blink_active"] = False
            effect_state["blink_timer"] = 0
            effect_state["blink_next"] = random.randint(120, 300)

    dy_total = 0
    remaining = []
    scored_pairs = set()

    for bh in effect_state["black_holes"]:
        bh["timer"] += 1
        bh["previous_x"] = bh.get("x", WIDTH + 125)
        bh["x"] -= bh["speed"]
        bh["wobble"] += 0.04

        draw_x = bh["x"]
        draw_y = bh["y"] + math.sin(bh["wobble"]) * 4

        if black_hole_img is not None:
            black_hole_surface = black_hole_img
        else:
            black_hole_surface = build_fallback_black_hole_surface()

        black_hole_surface = trim_alpha_sprite(black_hole_surface)
        black_hole_rect = black_hole_surface.get_rect(center=(int(draw_x), int(draw_y)))
        screen.blit(black_hole_surface, black_hole_rect)

        dx = black_hole_rect.centerx - bird_rect_ref.centerx
        dy = black_hole_rect.centery - bird_rect_ref.centery
        dist = math.hypot(dx, dy)
        if 0 < dist < bh["pull_radius"]:
            pull = BLACK_HOLE_PULL_STRENGTH * (1 - dist / bh["pull_radius"])
            bird_rect_ref.centerx += int((dx / dist) * pull * 7)
            dy_total += (dy / dist) * pull * 1.35
            bird_rect_ref.centerx = max(28, min(WIDTH - 28, bird_rect_ref.centerx))
            bird_rect.centerx = bird_rect_ref.centerx

        if (
            dist <= BLACK_HOLE_KILL_DISTANCE
            or black_hole_touches_bird(black_hole_surface, black_hole_rect, bird_surface_ref, bird_rect_ref)
        ):
            game_over = True

        crossed_bird = bh["previous_x"] >= bird_rect_ref.centerx and bh["x"] < bird_rect_ref.centerx
        if bh["from_top"] and not bh["scored"] and crossed_bird and bh["pair_id"] not in scored_pairs:
            score_point.play()
            score_tracker["score"] += POINTS_PER_PIPE
            scored_pairs.add(bh["pair_id"])
            bh["scored"] = True

        if black_hole_rect.right > -140:
            remaining.append(bh)

    for bh in remaining:
        if bh["pair_id"] in scored_pairs:
            bh["scored"] = True

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
    global bird_rect
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

        if dx:
            if "wind_push_x" not in effect_state:
                effect_state["wind_push_x"] = float(bird_rect_ref.centerx)

            effect_state["wind_push_x"] += dx

            min_x = bird_rect_ref.width // 2
            max_x = WIDTH - bird_rect_ref.width // 2

            bird_rect_ref.centerx = int(max(min_x, min(max_x, effect_state["wind_push_x"])))
            bird_rect.centerx = bird_rect_ref.centerx
        else:
            effect_state["wind_push_x"] = float(bird_rect_ref.centerx)
        
        draw_wind_warning()

    if current_level == 5:
        dy_extra = update_buoyancy(bird_movement_ref)

    if current_level == 6:
        update_draw_gas_clouds(bird_rect_ref)

    if current_level == 7:
        update_draw_smileys(bird_rect_ref)

    if current_level == 8:
        update_draw_checkrams(bird_surface_ref, bird_rect_ref)

    if current_level == 9:
        draw_star_trail(bird_rect_ref.center)
        update_draw_asteroids(bird_surface_ref, bird_rect_ref)

    if current_level == 10:
        dy_extra = update_draw_black_holes(bird_surface_ref, bird_rect_ref, bird_movement_ref)
    
    if current_level == 12:
        draw_scanlines()

    return dy_extra

#LEVEL TRANSITION
def score_needed_for_next_level(level):
    return (level + 1) * SCORE_PER_LEVEL

def compute_level(score):
    return min(int(score) // SCORE_PER_LEVEL, MAX_LEVEL)

def should_level_up():
    if current_level >= MAX_LEVEL or pending_level is not None or transition_timer > 0:
        return False
    return score_tracker["score"] >= score_needed_for_next_level(current_level)

def start_level_transition(new_level):
    global pending_level, transition_timer

    for pipe_pair in pipes:
        if isinstance(pipe_pair, dict):
            pipe_pair["scored"] = True

    score_tracker["score"] = new_level * SCORE_PER_LEVEL

    pending_level = new_level
    transition_timer = LEVEL_TRANSITION_FRAMES

def transition_to_level(new_level):
    global current_level, current_birds, bird_img, bird_rect, current_pipe_spawn_interval
    global back_img, floor_img, ground_fill_color, current_pipe_variants, floor_fill_color
    global pipes, last_pipe_gap_center, sky_pipe_pattern_index

    current_level = new_level
    current_birds = try_load_bird_frames(new_level)
    bird_img = current_birds[bird_index]
    bird_rect = bird_img.get_rect(center=bird_rect.center)
    back_img = try_load_background(new_level)
    ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))
    floor_img = try_load_floor(new_level)
    floor_fill_color = derive_floor_fill_color(floor_img, ground_fill_color[:3])
    current_pipe_variants = try_load_pipe_variants(new_level)
    pipes = []
    last_pipe_gap_center = None
    sky_pipe_pattern_index = 0
    try_play_music(new_level)
    reset_effect_state()

    current_pipe_spawn_interval = get_level_spawn_interval(new_level)
    pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)
    pygame.event.clear(create_pipe)


def get_start_level():
    return 0

def get_start_score():
    return 0

#GAME RESET
def reset_game():
    global bird_rect, bird_movement, pipes, game_over, game_started, level_intro_pending, happy_ending_played
    global current_level, current_birds, bird_img, back_img, floor_img, current_pipe_spawn_interval
    global ground_fill_color, current_pipe_variants, pending_level, transition_timer, floor_fill_color
    global last_pipe_gap_center, sky_pipe_pattern_index

    pipes = []
    last_pipe_gap_center = None
    sky_pipe_pattern_index = 0
    bird_movement = 0
    game_over = False
    game_started = False
    level_intro_pending = False
    happy_ending_played = False
    pending_level = None
    transition_timer = 0
    current_level = get_start_level()
    score_tracker["score"] = get_start_score()

    current_birds = try_load_bird_frames(current_level)
    bird_img = current_birds[0]
    bird_rect = bird_img.get_rect(center=(BIRD_START_X, BIRD_START_Y))
    back_img = try_load_background(current_level)
    ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))
    floor_img = try_load_floor(current_level)
    floor_fill_color = derive_floor_fill_color(floor_img, ground_fill_color[:3])
    current_pipe_variants = try_load_pipe_variants(current_level)
    try_play_music(current_level)
    reset_effect_state()

    current_pipe_spawn_interval = get_level_spawn_interval(current_level)
    pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)
    pygame.event.clear(create_pipe)

pygame.init()
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird")

try:
    pygame.mixer.init()
except pygame.error:
    pass

#ASSET LOAD
current_level = get_start_level()
back_img = try_load_background(current_level)
ground_fill_color = back_img.get_at((0, back_img.get_height() - 1))
floor_img = try_load_floor(current_level)
floor_fill_color = derive_floor_fill_color(floor_img, ground_fill_color[:3])
pipe_img = load_gameplay_sprite("pipe_img.webp", (PIPE_WIDTH, PIPE_HEIGHT))
pipe_mask = pygame.mask.from_surface(pipe_img)
top_pipe_img = pygame.transform.flip(pipe_img, False, True)
top_pipe_mask = pygame.mask.from_surface(top_pipe_img)
over_img = load_gameplay_sprite("game_over.png", (GAME_OVER_WIDTH, 116))
vine_img = load_vine_image("Vines.png")
try:
    hazard_img = clean_hazard_image(load_image(TOXIC_HAZARD_IMAGE, alpha=True))
except Exception:
    hazard_img = None
member_weapon_images = try_load_member_weapon_images()
try:
    raw_wind_warning_img = load_image(ICY_WIND_WARNING_IMAGE, alpha=True)
    wind_warning_img = scale_image(clean_wind_warning_image(raw_wind_warning_img), (165, 165))
except Exception:
    wind_warning_img = None
try:
    asteroid_img = load_asteroid_image(ASTEROID_IMAGE)
except Exception:
    asteroid_img = None
try:
    black_hole_img = load_black_hole_image(BLACK_HOLE_IMAGE)
except Exception:
    black_hole_img = None
try:
    finish_flag_img = load_finish_flag_image(FINISH_FLAG_IMAGE)
except Exception:
    finish_flag_img = None

current_pipe_variants = try_load_pipe_variants(current_level)
current_birds = try_load_bird_frames(current_level)
bird_index = 0
bird_img = current_birds[bird_index]
bird_rect = bird_img.get_rect(center=(BIRD_START_X, BIRD_START_Y))
bird_movement = 0

bird_flap = pygame.USEREVENT
create_pipe = pygame.USEREVENT + 1
current_pipe_spawn_interval = get_level_spawn_interval(current_level)
pygame.time.set_timer(bird_flap, 200)
pygame.time.set_timer(create_pipe, current_pipe_spawn_interval)

pipes = []
last_pipe_gap_center = None
sky_pipe_pattern_index = 0
floor_x = 0
game_over = False
game_started = False
pending_level = None
transition_timer = 0
score_tracker = {"score": get_start_score(), "high_score": 0}
score_font = pygame.font.Font("freesansbold.ttf", 27)
prompt_font = pygame.font.Font("freesansbold.ttf", 24)
over_rect = over_img.get_rect(midtop=(WIDTH // 2, GAME_OVER_TOP))

reset_effect_state()
try_play_music(current_level)

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
            if level_intro_pending:
                level_intro_pending = False
                bird_movement = FLAP_STRENGTH
            elif not game_started:
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

        if (
            event.type == create_pipe
            and game_started
            and not game_over
            and not level_intro_pending
            and transition_timer == 0
            and pending_level is None
            and current_level != 10
        ):
            new_pipe = create_pipes()
            if not pipes or all(
                abs(new_pipe["bottom"].centerx - p["bottom"].centerx) > PIPE_WIDTH
                for p in pipes
                if isinstance(p, dict)
            ):
                pipes.append(new_pipe)

    if transition_timer > 0:
        transition_timer -= 1
        if transition_timer == LEVEL_TRANSITION_FRAMES // 2 and pending_level is not None:
            transition_to_level(pending_level)
        if transition_timer == 0:
            pending_level = None
            level_intro_pending = True
            bird_movement = 0

    screen.blit(back_img, (0, 0))

    shake_x, shake_y = (0, 0)
    if game_started and not game_over and transition_timer == 0 and not level_intro_pending:
        shake_x, shake_y = apply_level_effects_pre_pipes()

    if shake_x or shake_y:
        view_surf = screen.copy()
        screen.blit(view_surf, (shake_x, shake_y))

    if game_started and not game_over and transition_timer == 0 and not level_intro_pending:
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

        if (
            current_level == MAX_LEVEL
            and score_tracker["score"] >= FINAL_CLEAR_SCORE
            and not happy_ending_played
        ):
            happy_ending_played = True
            play_ending_music()

            ending_result = play_happy_ending_video()

            if ending_result == "quit":
                running = False
            else:
                credits_result = play_credits_video()
                running = False

            try:
                if pygame.mixer.get_init():
                    pygame.mixer.music.stop()
            except pygame.error:
                pass

            continue

        if should_level_up():
            start_level_transition(min(current_level + 1, MAX_LEVEL))

        if current_level == 3:
            draw_heat_waves()

        update_score()
        draw_score("game_on")

        if bird_rect.top <= -20 or bird_rect.bottom >= FLOOR_Y:
            game_over = True
            bird_rect.bottom = min(bird_rect.bottom, FLOOR_Y)
    elif game_started and not game_over:
        screen.blit(bird_img, bird_rect)
        if current_level != 10:
            draw_existing_pipes()
        draw_score("game_on")

        if level_intro_pending:
            draw_level_intro_screen()
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