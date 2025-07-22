import pgzrun
import math
import random
from pygame import Rect, mouse
import os

WIDTH, HEIGHT = 800, 600
TITLE = "Dungeon Explorer"
CELL_SIZE = 32
GRID_WIDTH = WIDTH // CELL_SIZE
GRID_HEIGHT = HEIGHT // CELL_SIZE

game_state = "menu"
music_enabled = True
sound_enabled = True
audio_available = True

EXIT_FOUND, GAME_WON, SCORE, MAX_SCORE = False, False, 0, 1000
EXIT_X = EXIT_Y = 0
VISITED_CELLS = set()
CURRENT_ROUND = 1
ENEMIES_PER_ROUND = 5

keys_pressed = set()
SPRITE_DRAW_OFFSET_X = SPRITE_DRAW_OFFSET_Y = -32

def check_audio_files():
    global audio_available
    sound_files = ['click', 'step', 'hit']
    sounds_dir = 'sounds'
    music_dir = 'music'
    if not os.path.exists(sounds_dir):
        audio_available = False
        return
    for sound_name in sound_files:
        sound_path = os.path.join(sounds_dir, sound_name + '.wav')
        if not os.path.exists(sound_path):
            audio_available = False
            return
    music_path = os.path.join(music_dir, 'background_music.mp3')
    if not os.path.exists(music_path):
        if os.path.exists(os.path.join(sounds_dir, 'background_music.mp3')):
            if not os.path.exists(music_dir):
                os.makedirs(music_dir)
            import shutil
            shutil.copy(os.path.join(sounds_dir, 'background_music.mp3'), music_path)
        else:
            audio_available = False
            return
    audio_available = True

def initialize_audio():
    global audio_available
    try:
        test_sounds = ['click', 'step', 'hit']
        for sound_name in test_sounds:
            if not hasattr(sounds, sound_name):
                audio_available = False
    except Exception:
        audio_available = False

def safe_play_sound(sound_name):
    if audio_available and sound_enabled:
        try:
            if hasattr(sounds, sound_name):
                getattr(sounds, sound_name).play()
        except Exception:
            pass

def safe_play_music(music_name):
    if audio_available and music_enabled:
        try:
            music.play(music_name)
        except Exception:
            pass

def safe_stop_music():
    if audio_available:
        try:
            music.stop()
        except Exception:
            pass

def ensure_music_playing():
    if audio_available and music_enabled:
        try:
            if not music.is_playing():
                music.play('background_music')
        except Exception:
            pass

class SpriteAnimation:
    def __init__(self, frames, frame_duration=0.2):
        self.frames = frames
        self.frame_duration = frame_duration
        self.current_frame = 0
        self.frame_timer = 0
    def update(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
    def get_current_frame(self):
        return self.frames[self.current_frame]

class Character:
    def __init__(self, x, y, idle_frames, walk_frames):
        self.grid_x = x
        self.grid_y = y
        self.pixel_x = x * CELL_SIZE
        self.pixel_y = y * CELL_SIZE
        self.target_x = self.pixel_x
        self.target_y = self.pixel_y
        self.moving = False
        self.move_speed = 120
        self.idle_animation = SpriteAnimation(idle_frames, 0.5)
        self.walk_animation = SpriteAnimation(walk_frames, 0.15)
        self.current_animation = self.idle_animation
    def update(self, dt):
        if self.moving:
            dx = self.target_x - self.pixel_x
            dy = self.target_y - self.pixel_y
            distance = math.sqrt(dx * dx + dy * dy)
            if distance < 2:
                self.pixel_x = self.target_x
                self.pixel_y = self.target_y
                self.moving = False
                self.current_animation = self.idle_animation
            else:
                move_distance = self.move_speed * dt
                self.pixel_x += (dx / distance) * move_distance
                self.pixel_y += (dy / distance) * move_distance
        self.current_animation.update(dt)
    def move_to(self, grid_x, grid_y):
        if not self.moving and self.is_valid_position(grid_x, grid_y):
            self.grid_x = grid_x
            self.grid_y = grid_y
            self.target_x = grid_x * CELL_SIZE
            self.target_y = grid_y * CELL_SIZE
            self.moving = True
            self.current_animation = self.walk_animation
            return True
        return False
    def is_valid_position(self, x, y):
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT and dungeon_map[y][x] in (0, 2)
    def draw(self):
        current_frame = self.current_animation.get_current_frame()
        sprite_size = 32
        screen.blit(current_frame, (self.pixel_x + SPRITE_DRAW_OFFSET_X, self.pixel_y + SPRITE_DRAW_OFFSET_Y))

class Player(Character):
    def __init__(self, x, y):
        idle_frames = ['player_idle1', 'player_idle2', 'player_idle3', 'player_idle4', 'player_idle5', 'player_idle6']
        walk_frames = ['player_walk1', 'player_walk2', 'player_walk3', 'player_walk4', 'player_walk5', 'player_walk6', 'player_walk7', 'player_walk8']
        super().__init__(x, y, idle_frames, walk_frames)
        self.health = 100

class Enemy(Character):
    def __init__(self, x, y, territory_center, territory_radius):
        idle_frames = ['enemy_idle1', 'enemy_idle2', 'enemy_idle3', 'enemy_idle4', 'enemy_idle5', 'enemy_idle6']
        walk_frames = ['enemy_walk1', 'enemy_walk2', 'enemy_walk3', 'enemy_walk4', 'enemy_walk5', 'enemy_walk6', 'enemy_walk7', 'enemy_walk8']
        super().__init__(x, y, idle_frames, walk_frames)
        self.territory_center = territory_center
        self.territory_radius = territory_radius
        self.move_timer = 0
        self.move_interval = random.uniform(1.0, 3.0)
    def update(self, dt):
        super().update(dt)
        if not self.moving:
            self.move_timer += dt
            if self.move_timer >= self.move_interval:
                self.move_timer = 0
                self.move_interval = random.uniform(1.0, 3.0)
                self.try_random_move()
    def try_random_move(self):
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            new_x = self.grid_x + dx
            new_y = self.grid_y + dy
            distance_from_center = math.sqrt((new_x - self.territory_center[0]) ** 2 + (new_y - self.territory_center[1]) ** 2)
            if distance_from_center <= self.territory_radius:
                if self.move_to(new_x, new_y):
                    break

class Button:
    def __init__(self, x, y, width, height, text, action):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.action = action
        self.hovered = False
    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)
    def draw(self):
        color = (100, 150, 200) if self.hovered else (70, 120, 170)
        screen.draw.filled_rect(self.rect, color)
        screen.draw.rect(self.rect, (255, 255, 255))
        screen.draw.text(self.text, center=self.rect.center, fontsize=24, color=(255, 255, 255))
    def handle_click(self, pos):
        if self.rect.collidepoint(pos):
            self.action()
            return True
        return False

def generate_dungeon():
    global EXIT_X, EXIT_Y
    dungeon = [[1 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    for _ in range(15):
        room_width = random.randint(4, 8)
        room_height = random.randint(4, 6)
        room_x = random.randint(2, GRID_WIDTH - room_width - 2)
        room_y = random.randint(2, GRID_HEIGHT - room_height - 2)
        for y in range(room_y, room_y + room_height):
            for x in range(room_x, room_x + room_width):
                dungeon[y][x] = 0
    for _ in range(30):
        corridor_x = random.randint(2, GRID_WIDTH - 3)
        corridor_y = random.randint(2, GRID_HEIGHT - 3)
        if random.choice([True, False]):
            length = random.randint(3, 10)
            for i in range(length):
                if corridor_x + i < GRID_WIDTH - 2:
                    dungeon[corridor_y][corridor_x + i] = 0
        else:
            length = random.randint(3, 8)
            for i in range(length):
                if corridor_y + i < GRID_HEIGHT - 2:
                    dungeon[corridor_y + i][corridor_x] = 0
    while True:
        EXIT_X = random.randint(5, GRID_WIDTH - 6)
        EXIT_Y = random.randint(5, GRID_HEIGHT - 6)
        if dungeon[EXIT_Y][EXIT_X] == 0:
            dungeon[EXIT_Y][EXIT_X] = 2
            break
    for _ in range(20):
        x = random.randint(1, GRID_WIDTH - 2)
        y = random.randint(1, GRID_HEIGHT - 2)
        if dungeon[y][x] == 1:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT:
                        dungeon[y + dy][x + dx] = 0
    return dungeon

def find_empty_position():
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if dungeon_map[y][x] == 0:
            return x, y

def start_game():
    global game_state, player, enemies, dungeon_map, EXIT_FOUND, GAME_WON, SCORE, VISITED_CELLS, CURRENT_ROUND, ENEMIES_PER_ROUND
    game_state = "instructions"
    EXIT_FOUND = False
    GAME_WON = False
    SCORE = 0
    VISITED_CELLS.clear()
    CURRENT_ROUND = 1
    ENEMIES_PER_ROUND = 5
    dungeon_map = generate_dungeon()
    player_x, player_y = find_empty_position()
    player = Player(player_x, player_y)
    VISITED_CELLS.add((player_x, player_y))
    enemies = []
    for _ in range(ENEMIES_PER_ROUND):
        enemy_x, enemy_y = find_empty_position()
        territory_center = (enemy_x, enemy_y)
        territory_radius = random.randint(2, 4)
        enemies.append(Enemy(enemy_x, enemy_y, territory_center, territory_radius))

def toggle_music():
    global music_enabled
    music_enabled = not music_enabled
    if music_enabled:
        safe_play_music('background_music')
    else:
        safe_stop_music()

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled

def exit_game():
    quit()

def back_to_menu():
    global game_state
    game_state = "menu"
    safe_stop_music()

def start_playing():
    global game_state
    game_state = "playing"
    safe_play_music('background_music')

def start_new_round():
    global game_state, player, enemies, dungeon_map, EXIT_FOUND, GAME_WON, VISITED_CELLS, CURRENT_ROUND, ENEMIES_PER_ROUND
    CURRENT_ROUND += 1
    ENEMIES_PER_ROUND = min(5 + CURRENT_ROUND, 15)
    EXIT_FOUND = False
    GAME_WON = False
    VISITED_CELLS.clear()
    dungeon_map = generate_dungeon()
    player_x, player_y = find_empty_position()
    player = Player(player_x, player_y)
    VISITED_CELLS.add((player_x, player_y))
    enemies = []
    for _ in range(ENEMIES_PER_ROUND):
        enemy_x, enemy_y = find_empty_position()
        territory_center = (enemy_x, enemy_y)
        territory_radius = random.randint(2, 4)
        enemies.append(Enemy(enemy_x, enemy_y, territory_center, territory_radius))
    safe_play_sound('click')
    game_state = "playing"

buttons = [
    Button(WIDTH // 2 - 100, 250, 200, 50, "Start Game", start_game),
    Button(WIDTH // 2 - 100, 320, 200, 50, f"Music: {'ON' if music_enabled else 'OFF'}", toggle_music),
    Button(WIDTH // 2 - 100, 390, 200, 50, f"Sound: {'ON' if sound_enabled else 'OFF'}", toggle_sound),
    Button(WIDTH // 2 - 100, 460, 200, 50, "Exit", exit_game)
]
game_button = Button(WIDTH - 120, 10, 100, 40, "Menu", back_to_menu)
continue_button = Button(WIDTH // 2 - 75, 400, 150, 50, "Continue", start_playing)
player = None
enemies = []
dungeon_map = []

def update(dt):
    global buttons, EXIT_FOUND, GAME_WON, SCORE, VISITED_CELLS, keys_pressed, game_state
    if game_state == "playing":
        ensure_music_playing()
    if game_state == "menu":
        mouse_pos = mouse.get_pos()
        for button in buttons:
            button.update(mouse_pos)
        buttons[1].text = f"Music: {'ON' if music_enabled else 'OFF'}"
        buttons[2].text = f"Sound: {'ON' if sound_enabled else 'OFF'}"
    elif game_state == "instructions":
        mouse_pos = mouse.get_pos()
        continue_button.update(mouse_pos)
    elif game_state == "playing":
        if player:
            player.update(dt)
            if not player.moving and keys_pressed:
                moved = False
                if keys.UP in keys_pressed or keys.W in keys_pressed:
                    moved = player.move_to(player.grid_x, player.grid_y - 1)
                elif keys.DOWN in keys_pressed or keys.S in keys_pressed:
                    moved = player.move_to(player.grid_x, player.grid_y + 1)
                elif keys.LEFT in keys_pressed or keys.A in keys_pressed:
                    moved = player.move_to(player.grid_x - 1, player.grid_y)
                elif keys.RIGHT in keys_pressed or keys.D in keys_pressed:
                    moved = player.move_to(player.grid_x + 1, player.grid_y)
                if moved:
                    safe_play_sound('step')
            if not player.moving and dungeon_map[player.grid_y][player.grid_x] == 2 and not GAME_WON:
                EXIT_FOUND = True
                GAME_WON = True
                game_state = "round_complete"
                SCORE += 100
                safe_play_sound('click')
            current_cell = (player.grid_x, player.grid_y)
            if not player.moving and current_cell not in VISITED_CELLS and dungeon_map[player.grid_y][player.grid_x] == 0:
                VISITED_CELLS.add(current_cell)
                SCORE += 10
        for enemy in enemies:
            enemy.update(dt)
        mouse_pos = mouse.get_pos()
        game_button.update(mouse_pos)
        if player:
            for enemy in enemies:
                if (abs(player.grid_x - enemy.grid_x) == 0 and 
                    abs(player.grid_y - enemy.grid_y) == 0 and
                    not player.moving and not enemy.moving):
                    player.health -= 10
                    safe_play_sound('hit')
    elif game_state == "round_complete":
        pass

def draw():
    screen.clear()
    if game_state == "menu":
        for y in range(HEIGHT):
            color_intensity = int(30 + (y / HEIGHT) * 20)
            screen.draw.filled_rect(Rect(0, y, WIDTH, 1), (color_intensity, color_intensity, color_intensity + 20))
        screen.draw.text("DUNGEON EXPLORER", center=(WIDTH // 2 + 2, 148), fontsize=48, color=(100, 100, 150))
        screen.draw.text("DUNGEON EXPLORER", center=(WIDTH // 2, 150), fontsize=48, color=(255, 255, 255))
        screen.draw.text("Find the Golden Exit to Win!", center=(WIDTH // 2, 200), fontsize=24, color=(255, 215, 0))
        audio_status = "Audio: READY" if audio_available else "Audio: NOT AVAILABLE"
        audio_color = (100, 255, 100) if audio_available else (255, 100, 100)
        screen.draw.text(audio_status, center=(WIDTH // 2, 100), fontsize=16, color=audio_color)
        for button in buttons:
            button.draw()
    elif game_state == "instructions":
        for y in range(HEIGHT):
            color_intensity = int(20 + (y / HEIGHT) * 15)
            screen.draw.filled_rect(Rect(0, y, WIDTH, 1), (color_intensity, color_intensity + 10, color_intensity + 20))
        screen.draw.text("HOW TO PLAY", center=(WIDTH // 2, 80), fontsize=36, color=(255, 255, 255))
        instructions = [
            "🎮 Use ARROW KEYS or WASD to move your character",
            "🏃‍♂️ Navigate through the dungeon avoiding enemies",
            "🔴 Red borders show enemy patrol territories - stay away!",
            "💔 If you touch an enemy, you will take damage",
            "🏆 Find the GOLDEN EXIT to complete the round!",
            "🗺️  Explore the procedurally generated dungeon",
            "📊 Collect points by exploring new areas",
            "🔄 Complete rounds to face more enemies",
            "🔙 Use the Menu button to return to main menu"
        ]
        for i, instruction in enumerate(instructions):
            screen.draw.text(instruction, center=(WIDTH // 2, 150 + i * 35), fontsize=18, color=(200, 200, 200))
        continue_button.draw()
    elif game_state == "playing" or game_state == "round_complete":
        screen.fill((15, 15, 25))
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                cell_type = dungeon_map[y][x]
                if cell_type == 1:
                    screen.draw.filled_rect(
                        Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                        (80, 60, 40)
                    )
                elif cell_type == 2:
                    screen.draw.filled_rect(
                        Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                        (255, 215, 0)
                    )
                    screen.draw.filled_rect(
                        Rect(x * CELL_SIZE + 2, y * CELL_SIZE + 2, CELL_SIZE - 4, CELL_SIZE - 4),
                        (255, 255, 100)
                    )
                else:
                    screen.draw.filled_rect(
                        Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE),
                        (50, 50, 60)
                    )
        if player:
            player.draw()
        for enemy in enemies:
            enemy.draw()
            territory_color = (150, 50, 50, 100)
            for dx in range(-enemy.territory_radius, enemy.territory_radius + 1):
                for dy in range(-enemy.territory_radius, enemy.territory_radius + 1):
                    tx = enemy.territory_center[0] + dx
                    ty = enemy.territory_center[1] + dy
                    if (0 <= tx < GRID_WIDTH and 0 <= ty < GRID_HEIGHT and 
                        dx * dx + dy * dy <= enemy.territory_radius * enemy.territory_radius and
                        dungeon_map[ty][tx] == 0):
                        if dx * dx + dy * dy >= (enemy.territory_radius - 0.5) * (enemy.territory_radius - 0.5):
                            screen.draw.filled_rect(
                                Rect(tx * CELL_SIZE + 1, ty * CELL_SIZE + 1, CELL_SIZE - 2, CELL_SIZE - 2),
                                (150, 50, 50)
                            )
        ui_panel = Rect(0, HEIGHT - 60, WIDTH, 60)
        screen.draw.filled_rect(ui_panel, (20, 20, 30))
        screen.draw.rect(ui_panel, (100, 100, 150))
        if player:
            health_color = (255, 100, 100) if player.health < 30 else (100, 255, 100) if player.health > 70 else (255, 255, 100)
            screen.draw.text(f"Health: {player.health}", (20, HEIGHT - 50), fontsize=20, color=health_color)
            screen.draw.text(f"Score: {SCORE}", (200, HEIGHT - 50), fontsize=20, color=(255, 215, 0))
            screen.draw.text(f"Round: {CURRENT_ROUND}", (350, HEIGHT - 50), fontsize=20, color=(100, 200, 255))
            screen.draw.text(f"Exit: ({EXIT_X}, {EXIT_Y})", (500, HEIGHT - 50), fontsize=16, color=(200, 200, 200))
        game_button.draw()
        if player and player.health <= 0:
            overlay = Rect(0, 0, WIDTH, HEIGHT)
            screen.draw.filled_rect(overlay, (0, 0, 0, 150))
            screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 2 - 50), fontsize=48, color=(255, 50, 50))
            screen.draw.text("Press SPACE to restart", center=(WIDTH // 2, HEIGHT // 2 + 20), fontsize=24, color=(255, 255, 255))
        if game_state == "round_complete":
            overlay = Rect(0, 0, WIDTH, HEIGHT)
            screen.draw.filled_rect(overlay, (0, 0, 0, 150))
            screen.draw.text("ROUND COMPLETE!", center=(WIDTH // 2, HEIGHT // 2 - 80), fontsize=48, color=(255, 215, 0))
            screen.draw.text(f"Round {CURRENT_ROUND} Score: {SCORE}", center=(WIDTH // 2, HEIGHT // 2 - 30), fontsize=32, color=(255, 255, 255))
            screen.draw.text(f"Next Round: {CURRENT_ROUND + 1} enemies", center=(WIDTH // 2, HEIGHT // 2 + 10), fontsize=24, color=(100, 200, 255))
            screen.draw.text("Press SPACE for next round", center=(WIDTH // 2, HEIGHT // 2 + 50), fontsize=24, color=(255, 255, 255))

def on_mouse_down(pos):
    if game_state == "menu":
        for button in buttons:
            if button.handle_click(pos):
                safe_play_sound('click')
                break
    elif game_state == "instructions":
        if continue_button.handle_click(pos):
            safe_play_sound('click')
    elif game_state == "playing":
        if game_button.handle_click(pos):
            safe_play_sound('click')

def on_key_down(key):
    global GAME_WON, game_state, keys_pressed
    if game_state == "playing" and player and player.health > 0:
        keys_pressed.add(key)
        if not player.moving:
            moved = False
            if key == keys.UP or key == keys.W:
                moved = player.move_to(player.grid_x, player.grid_y - 1)
            elif key == keys.DOWN or key == keys.S:
                moved = player.move_to(player.grid_x, player.grid_y + 1)
            elif key == keys.LEFT or key == keys.A:
                moved = player.move_to(player.grid_x - 1, player.grid_y)
            elif key == keys.RIGHT or key == keys.D:
                moved = player.move_to(player.grid_x + 1, player.grid_y)
            if moved:
                safe_play_sound('step')
    elif game_state == "playing" and player and player.health <= 0 and key == keys.SPACE:
        start_game()
    elif game_state == "round_complete" and key == keys.SPACE:
        start_new_round()

def on_key_up(key):
    global keys_pressed
    if game_state == "playing":
        keys_pressed.discard(key)

check_audio_files()
initialize_audio()
pgzrun.go()