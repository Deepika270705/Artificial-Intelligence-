
import random
import math
# pyrefly: ignore [missing-import]
import pygame


pygame.init()

# =========================
# SCREEN SETTINGS
# =========================
WIDTH = 1280
HEIGHT = 720
FPS = 60

WORLD_WIDTH = 3000
WORLD_HEIGHT = 2000

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Lost Island Survival - Pro Edition")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 32)
big_font = pygame.font.Font(None, 90)

# =========================
# COLORS (HSL and premium palettes)
# =========================
OCEAN = (24, 49, 79)       # Deep ocean turquoise/navy
SAND = (242, 218, 172)     # Soft tropical beach sand
GRASS = (58, 125, 68)      # Rich emerald green
WHITE = (255, 255, 255)
RED = (239, 68, 68)        # Vibrant red
BROWN = (139, 94, 60)      # Wood brown
GRAY = (120, 120, 125)     # Stone grey
GREEN = (34, 139, 34)      # Foliage green
YELLOW = (253, 224, 71)    # Golden yellow

# =========================
# BOAT SETTINGS
# =========================
boat_x = 2800.0
boat_y = 1800.0

# =========================
# GAME STATE & RESET
# =========================
running = True
game_over = False
win = False

# Global state variables
player_x = 300.0
player_y = 300.0
player_vx = 0.0
player_vy = 0.0

MAX_SPEED = 6
ACCELERATION = 0.55
FRICTION = 0.84

health = 100.0
hunger = 100.0
wood = 0
stone = 0
food = 0
score = 0

camera_x = 0.0
camera_y = 0.0
CAMERA_SMOOTHNESS = 0.08

snake_x = 1000.0
snake_y = 700.0
snake_speed = 2.2
snake_trail = []  # Keeps history of last positions for slithering tail

trees = []
rocks = []
foods = []
particles = []

# Cached Sprite Surfaces
tree_sprite = None
rock_sprite = None
food_sprite = None
boat_sprite = None

def init_sprites():
    global tree_sprite, rock_sprite, food_sprite, boat_sprite
    
    # 1. Tree Sprite (80x80)
    tree_sprite = pygame.Surface((80, 80), pygame.SRCALPHA)
    # Trunk (centered at x=40)
    pygame.draw.rect(tree_sprite, BROWN, (40 - 6, 40, 12, 35))
    # Foliage (centered at x=40, y=35)
    pygame.draw.circle(tree_sprite, GREEN, (40, 35), 28)
    # Highlight
    pygame.draw.circle(tree_sprite, (48, 169, 48), (32, 28), 9)
    
    # 2. Rock Sprite (50x50)
    rock_sprite = pygame.Surface((50, 50), pygame.SRCALPHA)
    # Body (centered at 25, 25)
    pygame.draw.circle(rock_sprite, GRAY, (25, 25), 20)
    # Highlight
    pygame.draw.circle(rock_sprite, (160, 160, 165), (19, 19), 7)
    
    # 3. Food Sprite (30x30)
    food_sprite = pygame.Surface((30, 30), pygame.SRCALPHA)
    # Berry (centered at 15, 15)
    pygame.draw.circle(food_sprite, RED, (15, 15), 10)
    # Stem
    pygame.draw.circle(food_sprite, (40, 160, 40), (19, 9), 4)
    # Highlight
    pygame.draw.circle(food_sprite, (255, 130, 130), (12, 12), 3)

    # 4. Boat Sprite (140x140)
    boat_sprite = pygame.Surface((140, 140), pygame.SRCALPHA)
    bx, by = 70, 70
    # Wooden raft deck
    pygame.draw.polygon(boat_sprite, (101, 67, 33), [
        (bx - 35, by + 12),
        (bx + 35, by + 12),
        (bx + 50, by - 12),
        (bx - 50, by - 12)
    ])
    # Detail lines
    pygame.draw.line(boat_sprite, (70, 45, 20), (bx - 40, by - 4), (bx + 40, by - 4), 2)
    pygame.draw.line(boat_sprite, (70, 45, 20), (bx - 45, by + 4), (bx + 45, by + 4), 2)
    # Mast
    pygame.draw.line(boat_sprite, (45, 45, 45), (int(bx), int(by - 12)), (int(bx), int(by - 62)), 4)
    # Cream sail
    pygame.draw.polygon(boat_sprite, (244, 241, 230), [
        (bx, by - 58),
        (bx + 28, by - 35),
        (bx, by - 18)
    ])
    # Small red flag
    pygame.draw.polygon(boat_sprite, RED, [
        (bx, by - 62),
        (bx - 12, by - 57),
        (bx, by - 52)
    ])

def init_particles():
    global particles
    particles = []
    for _ in range(40):
        particles.append({
            'x': random.uniform(0, WORLD_WIDTH),
            'y': random.uniform(0, WORLD_HEIGHT),
            'speed_x': random.uniform(-1.2, -0.4), # Drifts left
            'speed_y': random.uniform(-0.3, 0.3),   # Up/down drift
            'size': random.uniform(3, 6),
            'sin_speed': random.uniform(0.01, 0.03),
            'sin_phase': random.uniform(0, 2 * math.pi)
        })

def reset_game():
    global player_x, player_y, player_vx, player_vy
    global health, hunger, wood, stone, food, score
    global camera_x, camera_y
    global snake_x, snake_y, snake_trail
    global trees, rocks, foods
    global game_over, win

    player_x = 300.0
    player_y = 300.0
    player_vx = 0.0
    player_vy = 0.0

    health = 100.0
    hunger = 100.0
    wood = 0
    stone = 0
    food = 0
    score = 0

    camera_x = player_x - WIDTH // 2
    camera_y = player_y - HEIGHT // 2

    snake_x = 1000.0
    snake_y = 700.0
    snake_trail = []

    # Items spawn only on the grassy island center to avoid floating in ocean/sand
    trees = [
        [random.randint(250, WORLD_WIDTH - 250),
         random.randint(250, WORLD_HEIGHT - 250)]
        for _ in range(50)
    ]

    rocks = [
        [random.randint(250, WORLD_WIDTH - 250),
         random.randint(250, WORLD_HEIGHT - 250)]
        for _ in range(30)
    ]

    foods = [
        [random.randint(250, WORLD_WIDTH - 250),
         random.randint(250, WORLD_HEIGHT - 250)]
        for _ in range(40)
    ]

    init_particles()
    game_over = False
    win = False

init_sprites()
reset_game()

# =========================
# MAIN LOOP
# =========================
while running:

    dt = clock.tick(FPS)

    # ---------------------
    # EVENTS
    # ---------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            # RESTART GAME WHEN GAME OVER OR WIN
            if game_over or win:
                if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    reset_game()

            # COLLECT ITEMS
            if not game_over and not win:
                if event.key == pygame.K_e:

                    for tree in trees[:]:
                        if math.dist((player_x, player_y), tree) < 60:
                            trees.remove(tree)
                            wood += 1
                            score += 5
                            break

                    for rock in rocks[:]:
                        if math.dist((player_x, player_y), rock) < 60:
                            rocks.remove(rock)
                            stone += 1
                            score += 5
                            break

                    for item in foods[:]:
                        if math.dist((player_x, player_y), item) < 50:
                            foods.remove(item)
                            food += 1
                            hunger = min(100.0, hunger + 20.0)
                            score += 10
                            break

                # ESCAPE (Near escape boat only)
                if event.key == pygame.K_r:
                    if math.dist((player_x, player_y), (boat_x, boat_y)) < 120:
                        if wood >= 20 and stone >= 15:
                            win = True

    # ---------------------
    # GAME UPDATE
    # ---------------------
    if not game_over and not win:

        keys = pygame.key.get_pressed()

        move_x = 0
        move_y = 0

        # WASD and Arrow keys support
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            move_x -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            move_x += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            move_y -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            move_y += 1

        if move_x != 0 and move_y != 0:
            move_x *= 0.7071
            move_y *= 0.7071

        player_vx += move_x * ACCELERATION
        player_vy += move_y * ACCELERATION

        player_vx *= FRICTION
        player_vy *= FRICTION

        speed = math.sqrt(player_vx**2 + player_vy**2)

        if speed > MAX_SPEED:
            player_vx = player_vx / speed * MAX_SPEED
            player_vy = player_vy / speed * MAX_SPEED

        player_x += player_vx
        player_y += player_vy

        # Prevent player from leaving world borders
        player_x = max(25, min(WORLD_WIDTH - 25, player_x))
        player_y = max(25, min(WORLD_HEIGHT - 25, player_y))

        # Hunger depletion
        hunger = max(0.0, hunger - 0.02)

        if hunger <= 0:
            health -= 0.03

        health = max(0.0, health)

        if health <= 0:
            game_over = True

        # ---------------------
        # SNAKE AI (Active updates only)
        # ---------------------
        dx = player_x - snake_x
        dy = player_y - snake_y

        distance = math.sqrt(dx * dx + dy * dy)

        if distance < 500 and distance > 0:
            snake_x += dx / distance * snake_speed
            snake_y += dy / distance * snake_speed

        if distance < 35:
            health = max(0.0, health - 0.05)
            if health <= 0:
                game_over = True

        # Snake trail history for slithering effect
        snake_trail.append((snake_x, snake_y))
        if len(snake_trail) > 8:
            snake_trail.pop(0)

        # ---------------------
        # AMBIENT WIND PARTICLES UPDATE
        # ---------------------
        for p in particles:
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            
            # Gentle sinusoidal bobbing
            p['y'] += math.sin(pygame.time.get_ticks() * p['sin_speed'] + p['sin_phase']) * 0.25
            
            # Reset offscreen/boundary particles
            if p['x'] < 0:
                p['x'] = WORLD_WIDTH
                p['y'] = random.uniform(0, WORLD_HEIGHT)
            if p['y'] < 0 or p['y'] > WORLD_HEIGHT:
                p['y'] = random.uniform(0, WORLD_HEIGHT)

    # ---------------------
    # CAMERA (Continues running smoothly for scrolling effect)
    # ---------------------
    target_x = player_x - WIDTH // 2
    target_y = player_y - HEIGHT // 2

    target_x = max(0, min(WORLD_WIDTH - WIDTH, target_x))
    target_y = max(0, min(WORLD_HEIGHT - HEIGHT, target_y))

    camera_x += (target_x - camera_x) * CAMERA_SMOOTHNESS
    camera_y += (target_y - camera_y) * CAMERA_SMOOTHNESS

    # ---------------------
    # DAY/NIGHT & ATMOSPHERE CALCULATION
    # ---------------------
    # Smooth day/night loop (approx 40 second period)
    cycle_time = pygame.time.get_ticks() / 6000.0  
    day_intensity = (math.sin(cycle_time) + 1.0) / 2.0  # Range 0.0 (midnight) to 1.0 (noon)
    night_alpha = int((1.0 - day_intensity) * 175)      # Maximum night shadow alpha 175

    # ---------------------
    # DRAW
    # ---------------------
    # 1. Fill base ocean color
    screen.fill(OCEAN)

    # 2. Draw Shoreline Wave Foam (Animated)
    wave_pulse = math.sin(pygame.time.get_ticks() / 350.0) * 4.0
    wave_rect = (
        int(50 - wave_pulse - camera_x),
        int(50 - wave_pulse - camera_y),
        int(WORLD_WIDTH - 100 + wave_pulse * 2),
        int(WORLD_HEIGHT - 100 + wave_pulse * 2)
    )
    wave_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    pygame.draw.rect(wave_surf, (230, 245, 255, 130), wave_rect, width=4, border_radius=18)
    screen.blit(wave_surf, (0, 0))

    # 3. Draw Sandy Shore boundary
    pygame.draw.rect(
        screen,
        SAND,
        (50 - camera_x,
         50 - camera_y,
         WORLD_WIDTH - 100,
         WORLD_HEIGHT - 100)
    )

    # 4. Draw Grass Island center
    pygame.draw.rect(
        screen,
        GRASS,
        (150 - camera_x,
         150 - camera_y,
         WORLD_WIDTH - 300,
         WORLD_HEIGHT - 300)
    )

    # 5. Draw Escape Raft (Pre-rendered sprite, culled)
    if (camera_x - 140 <= boat_x <= camera_x + WIDTH + 140 and 
        camera_y - 140 <= boat_y <= camera_y + HEIGHT + 140):
        screen.blit(boat_sprite, (int(boat_x - camera_x - 70), int(boat_y - camera_y - 70)))

    # 6. Draw TREES (Culled & Blitted from Cache)
    for t in trees:
        tx, ty = t[0], t[1]
        if camera_x - 50 <= tx <= camera_x + WIDTH + 50 and camera_y - 50 <= ty <= camera_y + HEIGHT + 50:
            screen.blit(tree_sprite, (int(tx - camera_x - 40), int(ty - camera_y - 40)))

    # 7. Draw ROCKS (Culled & Blitted from Cache)
    for r in rocks:
        rx, ry = r[0], r[1]
        if camera_x - 40 <= rx <= camera_x + WIDTH + 40 and camera_y - 40 <= ry <= camera_y + HEIGHT + 40:
            screen.blit(rock_sprite, (int(rx - camera_x - 25), int(ry - camera_y - 25)))

    # 8. Draw FOOD (Culled & Blitted from Cache)
    for f in foods:
        fx, fy = f[0], f[1]
        if camera_x - 30 <= fx <= camera_x + WIDTH + 30 and camera_y - 30 <= fy <= camera_y + HEIGHT + 30:
            screen.blit(food_sprite, (int(fx - camera_x - 15), int(fy - camera_y - 15)))

    # 9. Draw SNAKE WITH SLITHERING TAIL
    if len(snake_trail) > 0:
        for idx, pos in enumerate(snake_trail):
            seg_radius = int(8 + (idx / len(snake_trail)) * 10)
            seg_color = (0, 70 + idx * 15, 0)
            pygame.draw.circle(
                screen,
                seg_color,
                (int(pos[0] - camera_x),
                 int(pos[1] - camera_y)),
                seg_radius
            )
    else:
        pygame.draw.circle(
            screen,
            (0, 90, 0),
            (int(snake_x - camera_x),
             int(snake_y - camera_y)),
            18
        )

    # 10. Draw PLAYER
    px = int(player_x - camera_x)
    py = int(player_y - camera_y)
    pygame.draw.circle(screen, (30, 41, 59), (px, py), 26)
    pygame.draw.circle(screen, WHITE, (px, py), 23)
    pygame.draw.circle(screen, (59, 130, 246), (px, py), 12)

    # 11. Draw FLOATING WIND PARTICLES (Leaves/Fireflies)
    for p in particles:
        ptx, pty = p['x'] - camera_x, p['y'] - camera_y
        if -10 <= ptx <= WIDTH + 10 and -10 <= pty <= HEIGHT + 10:
            if day_intensity > 0.5:
                # Soft green leaves
                pygame.draw.circle(screen, (76, 175, 80), (int(ptx), int(pty)), int(p['size']))
            else:
                # Glowing golden fireflies (Blinking)
                blink = (math.sin(pygame.time.get_ticks() * 0.01 + p['sin_phase']) + 1.0) / 2.0
                glow_size = int(p['size'] + blink * 4)
                glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (253, 224, 71, 50), (glow_size, glow_size), glow_size)
                screen.blit(glow_surf, (int(ptx - glow_size), int(pty - glow_size)))
                pygame.draw.circle(screen, WHITE, (int(ptx), int(pty)), int(p['size'] * 0.6))

    # 12. Draw NIGHT AMBIENT DARKNESS & COZY LANTERN GLOWS
    if night_alpha > 0:
        ambient_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ambient_surf.fill((10, 10, 28, night_alpha))
        screen.blit(ambient_surf, (0, 0))
        
        # Golden lantern warm glows
        glow_layer = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # Player Lantern
        pygame.draw.circle(glow_layer, (253, 224, 71, 35), (px, py), 170)
        pygame.draw.circle(glow_layer, (253, 224, 71, 60), (px, py), 110)
        pygame.draw.circle(glow_layer, (253, 224, 71, 95), (px, py), 60)
        
        # Escape Boat Lantern (warm glowing mast light)
        bx_screen = int(boat_x - camera_x)
        by_screen = int(boat_y - camera_y)
        if -200 <= bx_screen <= WIDTH + 200 and -200 <= by_screen <= HEIGHT + 200:
            pygame.draw.circle(glow_layer, (253, 224, 71, 30), (bx_screen, by_screen - 35), 180)
            pygame.draw.circle(glow_layer, (253, 224, 71, 55), (bx_screen, by_screen - 35), 120)
            pygame.draw.circle(glow_layer, (253, 224, 71, 90), (bx_screen, by_screen - 35), 65)
            
        screen.blit(glow_layer, (0, 0))

    # 13. HUD PANEL (Elegant Glassmorphism style card)
    hud_surf = pygame.Surface((310, 360), pygame.SRCALPHA)
    pygame.draw.rect(hud_surf, (15, 23, 42, 210), (0, 0, 310, 360), border_radius=16)
    pygame.draw.rect(hud_surf, (59, 130, 246, 150), (0, 0, 310, 360), width=2, border_radius=16)
    screen.blit(hud_surf, (15, 15))

    hud = [
        ("Health", f"Health : {int(health)}%", (239, 68, 68)),      
        ("Hunger", f"Hunger : {int(hunger)}%", (245, 158, 11)),     
        ("Wood",   f"Wood   : {wood}/20", (180, 130, 80)),         
        ("Stone",  f"Stone  : {stone}/15", (156, 163, 175)),       
        ("Food",   f"Food   : {food}", (244, 63, 94)),            
        ("Score",  f"Score  : {score}", (52, 211, 153)),           
        ("", "", (0, 0, 0)),
        ("Help1", "WASD / Arrows = Move", (209, 213, 219)),
        ("Help2", "E = Collect Items", (209, 213, 219)),
        ("Help3", "R = Escape (near Boat)", (96, 165, 250))
    ]

    y = 35
    for item_type, text, color in hud:
        if text == "":
            y += 10
            continue
        
        # Render visual Health and Hunger bars
        if item_type == "Health":
            pygame.draw.rect(screen, (55, 65, 81), (155, y + 6, 140, 10), border_radius=5)
            fill_w = int((health / 100.0) * 140)
            if fill_w > 0:
                pygame.draw.rect(screen, color, (155, y + 6, fill_w, 10), border_radius=5)
        elif item_type == "Hunger":
            pygame.draw.rect(screen, (55, 65, 81), (155, y + 6, 140, 10), border_radius=5)
            fill_w = int((hunger / 100.0) * 140)
            if fill_w > 0:
                pygame.draw.rect(screen, color, (155, y + 6, fill_w, 10), border_radius=5)

        img = font.render(text, True, color)
        screen.blit(img, (35, y))
        y += 30

    # 14. GPS MINI-MAP PANEL (Top-Right)
    map_w, map_h = 180, 120
    map_x, map_y = WIDTH - map_w - 20, 20  
    
    # Minimap background container (translucent slate glass)
    minimap_bg = pygame.Surface((map_w + 10, map_h + 10), pygame.SRCALPHA)
    pygame.draw.rect(minimap_bg, (15, 23, 42, 220), (0, 0, map_w + 10, map_h + 10), border_radius=12)
    pygame.draw.rect(minimap_bg, (59, 130, 246, 160), (0, 0, map_w + 10, map_h + 10), width=2, border_radius=12)
    screen.blit(minimap_bg, (map_x - 5, map_y - 5))
    
    # Scaling ratios
    scale_x = map_w / WORLD_WIDTH
    scale_y = map_h / WORLD_HEIGHT
    
    # Sandy shore base
    pygame.draw.rect(
        screen,
        (225, 200, 155), 
        (map_x + int(50 * scale_x), map_y + int(50 * scale_y), int((WORLD_WIDTH - 100) * scale_x), int((WORLD_HEIGHT - 100) * scale_y)),
        border_radius=4
    )
    # Grass center island
    pygame.draw.rect(
        screen,
        (46, 100, 54), 
        (map_x + int(150 * scale_x), map_y + int(150 * scale_y), int((WORLD_WIDTH - 300) * scale_x), int((WORLD_HEIGHT - 300) * scale_y)),
        border_radius=4
    )
    
    # Draw resource indicator dots (faded out, sampled for speed)
    for t in trees[::3]:
        mx = map_x + int(t[0] * scale_x)
        my = map_y + int(t[1] * scale_y)
        pygame.draw.circle(screen, (34, 139, 34, 180), (mx, my), 2)
        
    for r in rocks[::3]:
        mx = map_x + int(r[0] * scale_x)
        my = map_y + int(r[1] * scale_y)
        pygame.draw.circle(screen, (100, 100, 100, 180), (mx, my), 2)

    # Draw Escape Boat dot (Shiny Gold)
    bx_map = map_x + int(boat_x * scale_x)
    by_map = map_y + int(boat_y * scale_y)
    pygame.draw.circle(screen, YELLOW, (bx_map, by_map), 4)
    # Pulsing beacon ring on map
    if pygame.time.get_ticks() % 1000 < 500:
        pygame.draw.circle(screen, YELLOW, (bx_map, by_map), 6, width=1)

    # Draw Snake dot (Flashing Red)
    sx_map = map_x + int(snake_x * scale_x)
    sy_map = map_y + int(snake_y * scale_y)
    if pygame.time.get_ticks() % 800 < 400:
        pygame.draw.circle(screen, RED, (sx_map, sy_map), 4)
    else:
        pygame.draw.circle(screen, (150, 0, 0), (sx_map, sy_map), 3)

    # Draw Player dot (Bright White/Blue tracker)
    px_map = map_x + int(player_x * scale_x)
    py_map = map_y + int(player_y * scale_y)
    pygame.draw.circle(screen, WHITE, (px_map, py_map), 4)
    pygame.draw.circle(screen, (59, 130, 246), (px_map, py_map), 2)

    # 15. DYNAMIC PROXIMITY HELPER (Blinking prompts)
    dist_to_boat = math.dist((player_x, player_y), (boat_x, boat_y))
    status_text = ""
    status_color = (255, 255, 255)

    if wood >= 20 and stone >= 15:
        if dist_to_boat < 120:
            status_text = "PRESS R TO ESCAPE!"
            status_color = (52, 211, 153) 
        else:
            status_text = "HEAD TO BOAT (BOTTOM-RIGHT)!"
            status_color = (253, 224, 71) 
    else:
        if dist_to_boat < 150:
            status_text = "NEED 20 WOOD & 15 STONE TO REPAIR!"
            status_color = (239, 68, 68) 

    if status_text != "":
        if pygame.time.get_ticks() % 1000 < 600:
            status_img = font.render(status_text, True, status_color)
            backdrop = pygame.Surface((status_img.get_width() + 30, 40), pygame.SRCALPHA)
            pygame.draw.rect(backdrop, (15, 23, 42, 220), (0, 0, status_img.get_width() + 30, 40), border_radius=8)
            screen.blit(backdrop, (WIDTH // 2 - backdrop.get_width() // 2, HEIGHT - 70))
            screen.blit(status_img, (WIDTH // 2 - status_img.get_width() // 2, HEIGHT - 60))

    # 16. GAME OVER / WIN OVERLAYS
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((30, 10, 10, 195))  
        screen.blit(overlay, (0, 0))

        txt = big_font.render("GAME OVER", True, RED)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 80))

        sub_txt = font.render("You starved or were caught by the island snake!", True, WHITE)
        screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 10))

        restart_txt = font.render("Press SPACE to Restart the Game", True, (200, 200, 200))
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 60))

    if win:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 30, 20, 195))  
        screen.blit(overlay, (0, 0))

        txt = big_font.render("YOU ESCAPED!", True, YELLOW)
        screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 80))

        sub_txt = font.render(f"Successfully repaired the raft and escaped! Final Score: {score}", True, WHITE)
        screen.blit(sub_txt, (WIDTH // 2 - sub_txt.get_width() // 2, HEIGHT // 2 + 10))

        restart_txt = font.render("Press SPACE to Play Again", True, (200, 200, 200))
        screen.blit(restart_txt, (WIDTH // 2 - restart_txt.get_width() // 2, HEIGHT // 2 + 60))

    pygame.display.flip()

pygame.quit()