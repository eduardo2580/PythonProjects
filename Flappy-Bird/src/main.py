import pygame
import random
import sys
import os
import json
import math
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("Flappy Bird - Ultimate Edition")

# Game constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 400
GRAVITY = 0.25
INITIAL_GAME_SPEED = 3
FLAP_STRENGTH = -6
MAX_FALL_SPEED = 6
OBSTACLE_GAP = 180
OBSTACLE_SPACING = 350
PARTICLE_COUNT = 50
STAR_COUNT = 100

# Power-up constants
POWERUP_SPAWN_CHANCE = 0.02
POWERUP_DURATION = 300  # frames
SHIELD_DURATION = 180
SLOW_TIME_DURATION = 240

# Difficulty settings
DIFFICULTY_LEVELS = {
    'easy': {'gap': 220, 'speed_mult': 0.7, 'name': 'Easy'},
    'normal': {'gap': 180, 'speed_mult': 1.0, 'name': 'Normal'},
    'hard': {'gap': 140, 'speed_mult': 1.2, 'name': 'Hard'},
    'extreme': {'gap': 120, 'speed_mult': 1.4, 'name': 'Extreme'}
}

# Colors
SKY_BLUE = (135, 206, 235)
NIGHT_SKY = (25, 25, 112)
SUNSET_SKY = (255, 94, 77)
CLOUD_WHITE = (255, 255, 255)
GRASS_GREEN = (34, 139, 34)
BROWN = (139, 69, 19)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
BRONZE = (205, 127, 50)
BLUE = (0, 100, 255)
GREEN = (0, 255, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)

# Particle colors
PARTICLE_COLORS = [(255, 255, 255), (255, 255, 0), (255, 200, 0), (255, 150, 0)]

# Font setup
SCORE_FONT = pygame.font.SysFont('arial', 28, bold=True)
MENU_FONT = pygame.font.SysFont('arial', 24, bold=True)
GAME_OVER_FONT = pygame.font.SysFont('arial', 36, bold=True)
SMALL_FONT = pygame.font.SysFont('arial', 18, bold=True)
TINY_FONT = pygame.font.SysFont('arial', 14, bold=True)


class SoundManager:
    """Manages all game sounds"""
    def __init__(self):
        self.sounds = {}
        self.music_volume = 0.3
        self.sfx_volume = 0.5
        self.muted = False
        
    def create_sound(self, frequency, duration=0.1):
        """Create a simple sound effect"""
        sample_rate = 22050
        frames = int(duration * sample_rate)
        arr = []
        for i in range(frames):
            wave = 4096 * math.sin(frequency * 2 * math.pi * i / sample_rate)
            arr.append([int(wave), int(wave)])
        sound = pygame.sndarray.make_sound(pygame.array.array('i', arr))
        return sound
    
    def load_sounds(self):
        """Load or create all game sounds"""
        try:
            # Create simple sound effects
            self.sounds['flap'] = self.create_sound(200, 0.1)
            self.sounds['score'] = self.create_sound(800, 0.2)
            self.sounds['hit'] = self.create_sound(100, 0.3)
            self.sounds['powerup'] = self.create_sound(600, 0.15)
            self.sounds['shield'] = self.create_sound(400, 0.2)
        except:
            # If sound creation fails, use empty sounds
            for sound_name in ['flap', 'score', 'hit', 'powerup', 'shield']:
                self.sounds[sound_name] = None
    
    def play_sound(self, sound_name):
        """Play a sound effect"""
        if not self.muted and sound_name in self.sounds and self.sounds[sound_name]:
            self.sounds[sound_name].set_volume(self.sfx_volume)
            self.sounds[sound_name].play()
    
    def toggle_mute(self):
        """Toggle sound on/off"""
        self.muted = not self.muted


class HighScoreManager:
    """Manages high scores"""
    def __init__(self):
        self.scores_file = "data/highscores.json"
        self.high_scores = self.load_scores()
    
    def load_scores(self):
        """Load high scores from file"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def save_scores(self):
        """Save high scores to file"""
        try:
            os.makedirs("data", exist_ok=True)
            with open(self.scores_file, 'w') as f:
                json.dump(self.high_scores, f)
        except:
            pass
    
    def add_score(self, username, score, difficulty):
        """Add a new score"""
        if username not in self.high_scores:
            self.high_scores[username] = {}
        if difficulty not in self.high_scores[username]:
            self.high_scores[username][difficulty] = 0
        
        if score > self.high_scores[username][difficulty]:
            self.high_scores[username][difficulty] = score
            self.save_scores()
            return True
        return False
    
    def get_best_score(self, username, difficulty):
        """Get best score for user and difficulty"""
        if username in self.high_scores and difficulty in self.high_scores[username]:
            return self.high_scores[username][difficulty]
        return 0
    
    def get_leaderboard(self, difficulty, limit=5):
        """Get top scores for difficulty"""
        scores = []
        for username, user_scores in self.high_scores.items():
            if difficulty in user_scores:
                scores.append((username, user_scores[difficulty]))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]


class Particle:
    """Particle effect for visual enhancement"""
    def __init__(self, x, y, color=None):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = random.randint(30, 60)
        self.max_life = self.life
        self.color = color or random.choice(PARTICLE_COLORS)
        self.size = random.randint(2, 5)
    
    def update(self):
        """Update particle position and life"""
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # gravity
        self.life -= 1
        return self.life > 0
    
    def draw(self, screen):
        """Draw the particle"""
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            color = (*self.color, alpha)
            current_size = max(1, int(self.size * (self.life / self.max_life)))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), current_size)


class Star:
    """Background star for night mode"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.brightness = random.randint(100, 255)
        self.twinkle_speed = random.uniform(0.02, 0.1)
        self.twinkle_phase = random.uniform(0, 2 * math.pi)
    
    def update(self):
        """Update star twinkling"""
        self.twinkle_phase += self.twinkle_speed
        
    def draw(self, screen):
        """Draw the star"""
        brightness = int(self.brightness * (0.5 + 0.5 * math.sin(self.twinkle_phase)))
        color = (brightness, brightness, brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 1)


class PowerUp:
    """Power-up items for enhanced gameplay"""
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.type = power_type
        self.width = 30
        self.height = 30
        self.collected = False
        self.bob_offset = 0
        self.bob_speed = 0.1
        
        # Power-up types and their properties
        self.types = {
            'shield': {'color': BLUE, 'symbol': 'S'},
            'slow_time': {'color': PURPLE, 'symbol': 'T'},
            'double_score': {'color': GOLD, 'symbol': '2X'},
            'small_bird': {'color': GREEN, 'symbol': 'S'}
        }
    
    def update(self):
        """Update power-up animation"""
        self.bob_offset += self.bob_speed
        self.y += math.sin(self.bob_offset) * 0.5
    
    def move(self, speed):
        """Move power-up with game speed"""
        self.x -= speed
    
    def draw(self, screen):
        """Draw the power-up"""
        if not self.collected:
            # Draw glowing effect
            for i in range(3, 0, -1):
                glow_color = (*self.types[self.type]['color'], 50 * i)
                pygame.draw.circle(screen, self.types[self.type]['color'], 
                                 (int(self.x), int(self.y)), self.width//2 + i*2)
            
            # Draw main circle
            pygame.draw.circle(screen, self.types[self.type]['color'], 
                             (int(self.x), int(self.y)), self.width//2)
            pygame.draw.circle(screen, WHITE, 
                             (int(self.x), int(self.y)), self.width//2, 2)
            
            # Draw symbol
            symbol_text = SMALL_FONT.render(self.types[self.type]['symbol'], True, WHITE)
            symbol_rect = symbol_text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(symbol_text, symbol_rect)
    
    def get_rect(self):
        """Get collision rectangle"""
        return pygame.Rect(self.x - self.width//2, self.y - self.height//2, 
                          self.width, self.height)


def calculate_speed(score, difficulty='normal'):
    """Calculate game speed based on player's score and difficulty"""
    base_speed = INITIAL_GAME_SPEED * DIFFICULTY_LEVELS[difficulty]['speed_mult']
    return base_speed + (score // 10) * 0.3  # Slower progression


def get_time_of_day():
    """Get current time of day for dynamic backgrounds"""
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return 'morning'
    elif 12 <= hour < 18:
        return 'day'
    elif 18 <= hour < 21:
        return 'sunset'
    else:
        return 'night'


def get_background_color():
    """Get background color based on time of day"""
    time_of_day = get_time_of_day()
    colors = {
        'morning': (135, 206, 250),  # Light sky blue
        'day': SKY_BLUE,
        'sunset': SUNSET_SKY,
        'night': NIGHT_SKY
    }
    return colors.get(time_of_day, SKY_BLUE)


def darken_color(color, amount=20):
    """Safely darken a color by ensuring values stay in valid range"""
    return (
        max(0, color[0] - amount),
        max(0, color[1] - amount),
        max(0, color[2] - amount)
    )


class Player:
    """Enhanced player character class"""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.angle = 0
        self.velocity = 0
        self.height = self.y
        self.time = 0
        self.animation_count = 0
        self.animation_timer = 0
        # Enhanced sprite properties
        self.radius = 15
        self.original_radius = 15
        self.color = ORANGE
        self.wing_phase = 0
        self.wing_timer = 0
        self.trail = []  # Trail effect
        self.max_trail_length = 10
        
        # Power-up effects
        self.has_shield = False
        self.shield_time = 0
        self.is_small = False
        self.small_time = 0
        self.invulnerable = False
        self.invulnerable_time = 0

    def flap(self, sound_manager=None):
        """Make the player character flap its wings"""
        self.velocity = FLAP_STRENGTH
        self.time = 0
        self.wing_phase = 2  # Wings fully extended
        if sound_manager:
            sound_manager.play_sound('flap')
        
        # Add to trail
        self.trail.append((self.x, self.y))
        if len(self.trail) > self.max_trail_length:
            self.trail.pop(0)

    def update_powerups(self):
        """Update power-up effects"""
        # Shield effect
        if self.has_shield:
            self.shield_time -= 1
            if self.shield_time <= 0:
                self.has_shield = False
        
        # Small bird effect
        if self.is_small:
            self.small_time -= 1
            self.radius = self.original_radius * 0.7
            if self.small_time <= 0:
                self.is_small = False
                self.radius = self.original_radius
        
        # Invulnerability after hit
        if self.invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False

    def apply_powerup(self, powerup_type):
        """Apply power-up effect"""
        if powerup_type == 'shield':
            self.has_shield = True
            self.shield_time = SHIELD_DURATION
        elif powerup_type == 'small_bird':
            self.is_small = True
            self.small_time = POWERUP_DURATION

    def move(self):
        """Update player position based on physics"""
        self.time += 1
        
        # Apply gravity
        self.velocity += GRAVITY
        
        # Limit fall speed
        if self.velocity > MAX_FALL_SPEED:
            self.velocity = MAX_FALL_SPEED
        
        # Update position
        self.y += self.velocity

        # Handle rotation based on movement
        if self.velocity < 0:
            self.angle = 25
        else:
            if self.angle > -90:
                self.angle -= 3

        # Wing animation
        self.wing_timer += 1
        if self.wing_timer >= 5:
            self.wing_timer = 0
            self.wing_phase = max(0, self.wing_phase - 1)
        
        # Update power-ups
        self.update_powerups()
        
        # Update trail (fade old positions)
        self.trail = [(x, y) for x, y in self.trail[-self.max_trail_length:]]

    def draw(self, screen):
        """Draw the enhanced player character"""
        # Draw trail effect
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)) * 0.3)
            trail_radius = max(1, int(self.radius * (i / len(self.trail))))
            trail_color = (*self.color, alpha)
            if alpha > 0:
                pygame.draw.circle(screen, self.color, (int(trail_x), int(trail_y)), trail_radius)
        
        # Draw shield effect
        if self.has_shield:
            shield_radius = self.radius + 8
            shield_alpha = int(100 + 50 * math.sin(self.shield_time * 0.2))
            shield_color = (*BLUE, shield_alpha)
            for i in range(3):
                pygame.draw.circle(screen, BLUE, (self.x, int(self.y)), shield_radius - i, 2)
        
        # Flash effect when invulnerable
        if self.invulnerable and self.invulnerable_time % 10 < 5:
            return  # Skip drawing to create flash effect
        
        # Draw body (circle)
        pygame.draw.circle(screen, self.color, (self.x, int(self.y)), self.radius)
        
        # Add a subtle gradient effect
        highlight_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, highlight_color, (self.x - 3, int(self.y) - 3), self.radius // 3)

        # Draw eye
        eye_size = max(2, self.radius // 4)
        pygame.draw.circle(screen, BLACK, (self.x + 5, int(self.y) - 5), eye_size)
        pygame.draw.circle(screen, WHITE, (self.x + 6, int(self.y) - 6), eye_size // 2)

        # Draw beak
        beak_size = self.radius
        beak_points = [(self.x + beak_size, int(self.y)), 
                       (self.x + beak_size + 10, int(self.y) - 5), 
                       (self.x + beak_size + 10, int(self.y) + 5)]
        pygame.draw.polygon(screen, (255, 140, 0), beak_points)

        # Draw wings based on wing phase and angle
        wing_y_offset = 0
        if self.wing_phase == 2:  # Fully extended
            wing_y_offset = -10
        elif self.wing_phase == 1:  # Mid-flap
            wing_y_offset = -5

        # Adjust wing position based on angle
        wing_rotation = min(20, max(-20, int(self.angle)))

        # Draw the wing with enhanced graphics
        wing_points = [
            (self.x - 5, int(self.y)),
            (self.x - 15, int(self.y + wing_y_offset + wing_rotation)),
            (self.x - 5, int(self.y + 5))
        ]
        pygame.draw.polygon(screen, (220, 120, 0), wing_points)
        pygame.draw.polygon(screen, (180, 100, 0), wing_points, 2)

    def get_mask(self):
        """Return a simple rectangular collision mask"""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2)


class Obstacle:
    """Enhanced obstacle that the player must avoid"""

    def __init__(self, x, gap_size=OBSTACLE_GAP):
        self.x = x
        self.gap_height = 0
        self.top_height = 0
        self.bottom_y = 0
        self.width = 80
        self.passed = False
        self.gap_size = gap_size
        self.set_height()
        self.color = BROWN
        self.dark_color = darken_color(BROWN)
        self.highlight_color = tuple(min(255, c + 30) for c in BROWN)
        
        # Special obstacle types
        self.is_moving = random.random() < 0.05  # Reduced chance to 5%
        self.move_direction = 1 if random.random() < 0.5 else -1
        self.move_speed = 0.5  # Slower movement
        self.original_gap_height = self.gap_height

    def set_height(self):
        """Randomly set the height of the obstacle"""
        # Calculate safe margins based on screen size
        margin = min(50, SCREEN_HEIGHT // 8)  # Dynamic margin, max 50px
        min_height = margin + self.gap_size // 2
        max_height = SCREEN_HEIGHT - margin - self.gap_size // 2
        
        # Ensure we have a valid range
        if min_height >= max_height:
            # Fallback to center if margins are too large
            self.gap_height = SCREEN_HEIGHT // 2
        else:
            self.gap_height = random.randrange(min_height, max_height)
        
        self.top_height = self.gap_height - self.gap_size // 2
        self.bottom_y = self.gap_height + self.gap_size // 2

    def update(self):
        """Update obstacle (for moving obstacles)"""
        if self.is_moving:
            self.gap_height += self.move_direction * self.move_speed
            
            # Calculate dynamic boundaries
            margin = min(50, SCREEN_HEIGHT // 8)
            min_boundary = margin + self.gap_size // 2
            max_boundary = SCREEN_HEIGHT - margin - self.gap_size // 2
            
            # Bounce off boundaries
            if self.gap_height <= min_boundary or self.gap_height >= max_boundary:
                self.move_direction *= -1
            
            self.top_height = self.gap_height - self.gap_size // 2
            self.bottom_y = self.gap_height + self.gap_size // 2

    def move(self, speed):
        """Move the obstacle to the left"""
        self.x -= speed
        self.update()

    def draw(self, screen):
        """Draw the enhanced top and bottom parts of the obstacle"""
        # Draw top obstacle with enhanced graphics
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.top_height))
        # Add highlight
        pygame.draw.rect(screen, self.highlight_color, (self.x + 5, 0, 10, self.top_height))
        # Add detail
        pygame.draw.rect(screen, self.dark_color,
                         (self.x, max(0, self.top_height - 30), self.width, 30))
        # Add pipe cap
        cap_height = 20
        pygame.draw.rect(screen, self.dark_color, 
                        (self.x - 5, self.top_height - cap_height, self.width + 10, cap_height))

        # Draw bottom obstacle
        pygame.draw.rect(screen, self.color, (self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
        # Add highlight
        pygame.draw.rect(screen, self.highlight_color, (self.x + 5, self.bottom_y, 10, SCREEN_HEIGHT - self.bottom_y))
        # Add detail
        pygame.draw.rect(screen, self.dark_color,
                         (self.x, self.bottom_y, self.width, 30))
        # Add pipe cap
        pygame.draw.rect(screen, self.dark_color, 
                        (self.x - 5, self.bottom_y, self.width + 10, cap_height))
        
        # Add moving indicator for moving obstacles
        if self.is_moving:
            pygame.draw.circle(screen, RED, (self.x + self.width//2, int(self.gap_height)), 5)

    def collide(self, player):
        """Check if player collides with the obstacle"""
        if player.has_shield or player.invulnerable:
            return False
            
        player_rect = player.get_mask()

        # Create rects for top and bottom obstacles
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y)

        # Check for collision
        if player_rect.colliderect(top_rect) or player_rect.colliderect(bottom_rect):
            return True
        return False


class Ground:
    """Moving ground at the bottom of the screen"""

    def __init__(self, y):
        self.y = y
        self.height = SCREEN_HEIGHT - y
        self.x1 = 0
        self.x2 = SCREEN_WIDTH
        self.color = GRASS_GREEN
        self.dark_color = darken_color(GRASS_GREEN)

    def move(self, speed):
        """Move the ground to create scrolling effect"""
        self.x1 -= speed
        self.x2 -= speed

        if self.x1 + SCREEN_WIDTH <= 0:
            self.x1 = self.x2 + SCREEN_WIDTH
        if self.x2 + SCREEN_WIDTH <= 0:
            self.x2 = self.x1 + SCREEN_WIDTH

    def draw(self, screen):
        """Draw the ground"""
        pygame.draw.rect(screen, self.color, (self.x1, self.y, SCREEN_WIDTH, self.height))
        pygame.draw.rect(screen, self.color, (self.x2, self.y, SCREEN_WIDTH, self.height))

        # Add some detail to the ground
        for x in range(int(self.x1), int(self.x1 + SCREEN_WIDTH), 30):
            pygame.draw.line(screen, self.dark_color,
                             (x, self.y), (x, self.y + 5), 2)
        for x in range(int(self.x2), int(self.x2 + SCREEN_WIDTH), 30):
            pygame.draw.line(screen, self.dark_color,
                             (x, self.y), (x, self.y + 5), 2)


class Cloud:
    """Background cloud decoration"""

    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(0, 300)
        self.y = random.randint(30, min(150, SCREEN_HEIGHT // 3))  # Adaptive cloud height
        self.size = random.randint(40, 80)
        self.speed = random.uniform(1, 3)

    def move(self):
        """Move the cloud across the screen"""
        self.x -= self.speed

    def draw(self, screen):
        """Draw the cloud"""
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x - self.size * 0.5), int(self.y)), self.size * 0.8)
        pygame.draw.circle(screen, CLOUD_WHITE, (int(self.x + self.size * 0.5), int(self.y)), self.size * 0.8)

    def is_offscreen(self):
        """Check if cloud has moved off the screen"""
        return self.x < -self.size * 2


def draw_game_screen(screen, player, obstacles, ground, score, clouds, particles, stars, 
                    powerups, current_difficulty, time_multiplier=1.0, double_score_time=0):
    """Draw the enhanced main game screen with all elements"""
    # Draw dynamic background
    bg_color = get_background_color()
    screen.fill(bg_color)
    
    # Draw stars for night mode
    if get_time_of_day() == 'night':
        for star in stars:
            star.draw(screen)
    
    # Draw clouds
    for cloud in clouds:
        cloud.draw(screen)
    
    # Draw particles
    for particle in particles:
        particle.draw(screen)
    
    # Draw power-ups
    for powerup in powerups:
        powerup.draw(screen)
    
    # Draw player
    player.draw(screen)

    # Draw obstacles
    for obstacle in obstacles:
        obstacle.draw(screen)

    # Draw ground
    ground.draw(screen)

    # Draw UI elements
    draw_ui(screen, score, current_difficulty, time_multiplier, double_score_time, player)

    pygame.display.update()


def draw_ui(screen, score, difficulty, time_multiplier, double_score_time, player):
    """Draw the user interface elements"""
    # Draw score with enhanced styling
    score_color = GOLD if double_score_time > 0 else WHITE
    score_text = SCORE_FONT.render(f"Score: {score}", 1, score_color)
    score_outline = SCORE_FONT.render(f"Score: {score}", 1, BLACK)
    screen.blit(score_outline, (SCREEN_WIDTH - 10 - score_text.get_width() + 2, 12))
    screen.blit(score_text, (SCREEN_WIDTH - 10 - score_text.get_width(), 10))
    
    # Draw difficulty
    diff_text = SMALL_FONT.render(f"Difficulty: {DIFFICULTY_LEVELS[difficulty]['name']}", 1, WHITE)
    diff_outline = SMALL_FONT.render(f"Difficulty: {DIFFICULTY_LEVELS[difficulty]['name']}", 1, BLACK)
    screen.blit(diff_outline, (12, 12))
    screen.blit(diff_text, (10, 10))
    
    # Draw time multiplier indicator
    if time_multiplier != 1.0:
        time_text = SMALL_FONT.render(f"Time: {time_multiplier:.1f}x", 1, PURPLE)
        screen.blit(time_text, (10, 40))
    
    # Draw active power-up indicators
    ui_y = 70
    if player.has_shield:
        shield_text = TINY_FONT.render(f"Shield: {player.shield_time//60 + 1}s", 1, BLUE)
        screen.blit(shield_text, (10, ui_y))
        ui_y += 20
    
    if player.is_small:
        small_text = TINY_FONT.render(f"Small: {player.small_time//60 + 1}s", 1, GREEN)
        screen.blit(small_text, (10, ui_y))
        ui_y += 20
    
    if double_score_time > 0:
        double_text = TINY_FONT.render(f"2X Score: {double_score_time//60 + 1}s", 1, GOLD)
        screen.blit(double_text, (10, ui_y))
    
    # Draw controls hint
    controls_text = TINY_FONT.render("SPACE: Flap | M: Mute | ESC: Pause", 1, WHITE)
    controls_outline = TINY_FONT.render("SPACE: Flap | M: Mute | ESC: Pause", 1, BLACK)
    screen.blit(controls_outline, (11, SCREEN_HEIGHT - 21))
    screen.blit(controls_text, (10, SCREEN_HEIGHT - 22))


def username_screen(screen, sound_manager, high_score_manager):
    """Display the enhanced username input screen with difficulty selection"""
    input_box = pygame.Rect(SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 - 60, 240, 40)
    button_box = pygame.Rect(SCREEN_WIDTH // 2 - 60, SCREEN_HEIGHT // 2, 120, 40)
    
    # Difficulty selection buttons - smaller and repositioned
    diff_buttons = {}
    diff_y_start = SCREEN_HEIGHT // 2 + 60
    for i, (key, diff) in enumerate(DIFFICULTY_LEVELS.items()):
        x = SCREEN_WIDTH // 2 - 140 + i * 70
        diff_buttons[key] = pygame.Rect(x, diff_y_start, 65, 30)
    
    # Leaderboard button - smaller
    leaderboard_button = pygame.Rect(SCREEN_WIDTH - 90, 10, 80, 30)
    show_leaderboard = False
    
    active_color = (52, 152, 219)  # Blue
    inactive_color = (41, 128, 185)  # Darker blue
    box_color = inactive_color
    active = False
    username = ''
    selected_difficulty = 'normal'
    clock = pygame.time.Clock()

    # Create some clouds for the background
    clouds = [Cloud() for _ in range(5)]
    stars = [Star() for _ in range(STAR_COUNT//2)]
    particles = []

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = True
                    box_color = active_color
                elif button_box.collidepoint(event.pos) and username.strip():
                    return username.strip(), selected_difficulty
                elif leaderboard_button.collidepoint(event.pos):
                    show_leaderboard = not show_leaderboard
                else:
                    # Check difficulty buttons
                    clicked_diff = False
                    for diff_key, diff_rect in diff_buttons.items():
                        if diff_rect.collidepoint(event.pos):
                            selected_difficulty = diff_key
                            sound_manager.play_sound('score')
                            clicked_diff = True
                            break
                    
                    # Only deactivate input if we didn't click a difficulty button
                    if not clicked_diff:
                        active = False
                        box_color = inactive_color
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN and username.strip():
                        return username.strip(), selected_difficulty
                    elif event.key == pygame.K_BACKSPACE:
                        username = username[:-1]
                    elif event.key == pygame.K_ESCAPE:
                        active = False
                        box_color = inactive_color
                    elif event.key == pygame.K_TAB:
                        # Tab to start button if username is not empty
                        if username.strip():
                            return username.strip(), selected_difficulty
                    else:
                        if len(username) < 15 and event.unicode.isprintable():
                            username += event.unicode
                elif event.key == pygame.K_m:
                    sound_manager.toggle_mute()
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    # Auto-focus input if not focused and no username yet
                    if not username.strip():
                        active = True
                        box_color = active_color

        # Draw dynamic background
        bg_color = get_background_color()
        screen.fill(bg_color)

        # Draw stars for night mode
        if get_time_of_day() == 'night':
            for star in stars:
                star.update()
                star.draw(screen)

        # Update and draw clouds
        for cloud in clouds:
            cloud.move()
            cloud.draw(screen)
            if cloud.is_offscreen():
                clouds.remove(cloud)
                clouds.append(Cloud())

        # Add random particles
        if random.random() < 0.05:
            particles.append(Particle(random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + 10))
        
        # Update particles
        particles = [p for p in particles if p.update()]
        for particle in particles:
            particle.draw(screen)

        # Draw title with enhanced styling - smaller
        title_text = SCORE_FONT.render("Flappy Bird", 1, GOLD)
        title_shadow = SCORE_FONT.render("Flappy Bird", 1, BLACK)
        screen.blit(title_shadow, (SCREEN_WIDTH // 2 - title_text.get_width() // 2 + 2, 22))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 20))
        
        subtitle_text = SMALL_FONT.render("Ultimate Edition", 1, WHITE)
        subtitle_shadow = SMALL_FONT.render("Ultimate Edition", 1, BLACK)
        screen.blit(subtitle_shadow, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2 + 1, 61))
        screen.blit(subtitle_text, (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, 60))

        # Drawing player character as mascot with animation - smaller position
        player_demo = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 120)
        player_demo.wing_phase = 2 if (pygame.time.get_ticks() // 200) % 2 else 0
        player_demo.draw(screen)

        # Draw instruction - adjusted position
        label_text = "Enter username:"
        label_shadow = SMALL_FONT.render(label_text, True, BLACK)
        label_surface = SMALL_FONT.render(label_text, True, WHITE)
        label_rect = label_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 85))
        screen.blit(label_shadow, (label_rect.x + 1, label_rect.y + 1))
        screen.blit(label_surface, label_rect)

        # Draw input box
        pygame.draw.rect(screen, box_color, input_box, 0, border_radius=5)
        pygame.draw.rect(screen, BLACK, input_box, 2, border_radius=5)

        # Draw input text or placeholder
        if username:
            txt_shadow = SMALL_FONT.render(username, True, BLACK)
            txt_surface = SMALL_FONT.render(username, True, WHITE)
            text_rect = txt_surface.get_rect()
            text_rect.centery = input_box.centery
            text_rect.x = input_box.x + 10  # Left-align with padding
            screen.blit(txt_shadow, (text_rect.x + 1, text_rect.y + 1))
            screen.blit(txt_surface, text_rect)
        elif not active:
            # Show placeholder text when not active and no username
            placeholder_text = SMALL_FONT.render("Click to enter name...", True, (150, 150, 150))
            placeholder_rect = placeholder_text.get_rect()
            placeholder_rect.centery = input_box.centery
            placeholder_rect.x = input_box.x + 10
            screen.blit(placeholder_text, placeholder_rect)
        
        # Draw cursor when active
        if active and pygame.time.get_ticks() % 1000 < 500:
            cursor_x = input_box.x + 10 + SMALL_FONT.size(username)[0]
            pygame.draw.line(screen, WHITE, (cursor_x, input_box.y + 8), (cursor_x, input_box.bottom - 8), 2)

        # Draw start button
        start_enabled = len(username.strip()) > 0
        start_color = active_color if start_enabled else (100, 100, 100)
        pygame.draw.rect(screen, start_color, button_box, 0, border_radius=5)
        pygame.draw.rect(screen, BLACK, button_box, 2, border_radius=5)

        # Draw button text
        button_text = SMALL_FONT.render("Start", True, WHITE)
        button_rect = button_text.get_rect(center=button_box.center)
        screen.blit(button_text, button_rect)

        # Draw difficulty selection - smaller
        diff_label = TINY_FONT.render("Difficulty:", True, WHITE)
        diff_label_shadow = TINY_FONT.render("Difficulty:", True, BLACK)
        diff_label_rect = diff_label.get_rect(center=(SCREEN_WIDTH // 2, diff_y_start - 15))
        screen.blit(diff_label_shadow, (diff_label_rect.x + 1, diff_label_rect.y + 1))
        screen.blit(diff_label, diff_label_rect)
        
        for diff_key, diff_rect in diff_buttons.items():
            color = GOLD if diff_key == selected_difficulty else inactive_color
            pygame.draw.rect(screen, color, diff_rect, 0, border_radius=3)
            pygame.draw.rect(screen, BLACK, diff_rect, 1, border_radius=3)
            
            diff_text = TINY_FONT.render(DIFFICULTY_LEVELS[diff_key]['name'], True, WHITE)
            diff_text_rect = diff_text.get_rect(center=diff_rect.center)
            screen.blit(diff_text, diff_text_rect)

        # Draw leaderboard button
        pygame.draw.rect(screen, inactive_color, leaderboard_button, 0, border_radius=3)
        pygame.draw.rect(screen, BLACK, leaderboard_button, 1, border_radius=3)
        leaderboard_text = TINY_FONT.render("Scores", True, WHITE)
        leaderboard_rect = leaderboard_text.get_rect(center=leaderboard_button.center)
        screen.blit(leaderboard_text, leaderboard_rect)

        # Show leaderboard if requested
        if show_leaderboard:
            draw_leaderboard(screen, high_score_manager, selected_difficulty)

        # Draw game instructions - bottom
        instruction_text = "SPACE: Flap | M: Mute | ESC: Pause"
        instruction_surface = TINY_FONT.render(instruction_text, True, WHITE)
        instruction_rect = instruction_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        screen.blit(instruction_surface, instruction_rect)

        pygame.display.flip()
        clock.tick(30)


def draw_leaderboard(screen, high_score_manager, difficulty):
    """Draw the leaderboard overlay"""
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.fill(BLACK)
    overlay.set_alpha(180)
    screen.blit(overlay, (0, 0))
    
    # Draw leaderboard box - adaptive size for smaller screen
    board_width = min(400, SCREEN_WIDTH - 40)
    board_height = min(300, SCREEN_HEIGHT - 80)
    board_rect = pygame.Rect(SCREEN_WIDTH // 2 - board_width // 2, 
                            SCREEN_HEIGHT // 2 - board_height // 2, 
                            board_width, board_height)
    pygame.draw.rect(screen, (41, 128, 185), board_rect, 0, border_radius=10)
    pygame.draw.rect(screen, WHITE, board_rect, 3, border_radius=10)
    
    # Title
    title_text = MENU_FONT.render(f"Top Scores - {DIFFICULTY_LEVELS[difficulty]['name']}", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, board_rect.y + 30))
    screen.blit(title_text, title_rect)
    
    # Get and display scores
    leaderboard = high_score_manager.get_leaderboard(difficulty)
    if leaderboard:
        for i, (username, score) in enumerate(leaderboard):
            color = GOLD if i == 0 else SILVER if i == 1 else BRONZE if i == 2 else WHITE
            score_text = SMALL_FONT.render(f"{i+1}. {username}: {score}", True, color)
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, board_rect.y + 70 + i * 30))
            screen.blit(score_text, score_rect)
    else:
        no_scores_text = SMALL_FONT.render("No scores yet!", True, WHITE)
        no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH // 2, board_rect.y + 100))
        screen.blit(no_scores_text, no_scores_rect)


def main():
    """Enhanced main game function with all new features"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Initialize game systems
    sound_manager = SoundManager()
    sound_manager.load_sounds()
    high_score_manager = HighScoreManager()
    
    username, difficulty = username_screen(screen, sound_manager, high_score_manager)

    while True:
        # Initialize game objects
        player = Player(150, SCREEN_HEIGHT // 2)  # Center player on screen
        ground = Ground(SCREEN_HEIGHT - 70)  # Ground at bottom with 70px height
        gap_size = DIFFICULTY_LEVELS[difficulty]['gap']
        obstacles = [Obstacle(SCREEN_WIDTH, gap_size)]
        clouds = [Cloud() for _ in range(8)]
        stars = [Star() for _ in range(STAR_COUNT)]
        particles = []
        powerups = []
        
        # Game state variables
        score = 0
        clock = pygame.time.Clock()
        running = True
        game_over = False
        paused = False
        
        # Enhanced game features
        time_multiplier = 1.0
        slow_time_remaining = 0
        double_score_time = 0
        last_powerup_spawn = 0
        combo_multiplier = 1
        
        # Performance tracking
        best_score = high_score_manager.get_best_score(username, difficulty)

        while running:
            clock.tick(60)  # 60 FPS for smoother gameplay
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE and not game_over and not paused:
                        player.flap(sound_manager)
                    elif event.key == pygame.K_r and game_over:
                        # Restart game
                        game_over = False
                        player = Player(150, SCREEN_HEIGHT // 2)  # Center player on screen
                        obstacles = [Obstacle(SCREEN_WIDTH, gap_size)]
                        powerups = []
                        particles = []
                        score = 0
                        time_multiplier = 1.0
                        slow_time_remaining = 0
                        double_score_time = 0
                        combo_multiplier = 1
                    elif event.key == pygame.K_t and game_over:
                        return  # Return to username screen
                    elif event.key == pygame.K_m:
                        sound_manager.toggle_mute()
                    elif event.key == pygame.K_ESCAPE:
                        paused = not paused

            # Skip game updates if paused
            if paused:
                # Draw pause overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))
                
                pause_text = GAME_OVER_FONT.render("PAUSED", 1, WHITE)
                pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                screen.blit(pause_text, pause_rect)
                
                continue_text = MENU_FONT.render("Press ESC to continue", 1, WHITE)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
                screen.blit(continue_text, continue_rect)
                
                pygame.display.update()
                continue

            current_speed = calculate_speed(score, difficulty) * time_multiplier

            # Update game objects if game is not over
            if not game_over:
                player.move()
                ground.move(current_speed)

                # Update background elements
                for star in stars:
                    star.update()
                
                for cloud in clouds:
                    cloud.move()
                    if cloud.is_offscreen():
                        clouds.remove(cloud)
                        clouds.append(Cloud())

                # Update particles
                particles = [p for p in particles if p.update()]
                
                # Update power-ups
                for powerup in powerups[:]:
                    powerup.update()
                    powerup.move(current_speed)
                    
                    # Check collision with player
                    if not powerup.collected and powerup.get_rect().colliderect(player.get_mask()):
                        powerup.collected = True
                        sound_manager.play_sound('powerup')
                        
                        # Apply power-up effect
                        if powerup.type == 'shield':
                            player.apply_powerup('shield')
                        elif powerup.type == 'slow_time':
                            slow_time_remaining = SLOW_TIME_DURATION
                        elif powerup.type == 'double_score':
                            double_score_time = POWERUP_DURATION
                        elif powerup.type == 'small_bird':
                            player.apply_powerup('small_bird')
                        
                        # Add particle effect
                        for _ in range(10):
                            particles.append(Particle(powerup.x, powerup.y))
                        
                        powerups.remove(powerup)
                    
                    # Remove off-screen power-ups
                    elif powerup.x < -50:
                        powerups.remove(powerup)

                # Update time effects
                if slow_time_remaining > 0:
                    slow_time_remaining -= 1
                    time_multiplier = 0.5
                else:
                    time_multiplier = 1.0
                
                if double_score_time > 0:
                    double_score_time -= 1

                # Spawn power-ups
                if random.random() < POWERUP_SPAWN_CHANCE and len(powerups) < 2:
                    powerup_types = ['shield', 'slow_time', 'double_score', 'small_bird']
                    powerup_type = random.choice(powerup_types)
                    powerup_y = random.randint(50, SCREEN_HEIGHT - 120)  # Adaptive powerup height
                    powerups.append(PowerUp(SCREEN_WIDTH + 50, powerup_y, powerup_type))

                # Manage obstacles
                add_obstacle = False
                obstacles_to_remove = []

                for obstacle in obstacles:
                    # Check collision
                    if obstacle.collide(player):
                        if player.has_shield:
                            # Shield absorbs hit
                            player.has_shield = False
                            player.shield_time = 0
                            player.invulnerable = True
                            player.invulnerable_time = 60
                            sound_manager.play_sound('shield')
                            
                            # Add particles
                            for _ in range(20):
                                particles.append(Particle(player.x, player.y, BLUE))
                        else:
                            game_over = True
                            sound_manager.play_sound('hit')
                            
                            # Add explosion particles
                            for _ in range(30):
                                particles.append(Particle(player.x, player.y, RED))

                    # Check if obstacle is passed
                    if not obstacle.passed and player.x > obstacle.x + obstacle.width:
                        obstacle.passed = True
                        add_obstacle = True
                        
                        # Calculate score with multipliers
                        score_gain = 1
                        if double_score_time > 0:
                            score_gain *= 2
                        score_gain *= combo_multiplier
                        
                        score += score_gain
                        combo_multiplier = min(5, combo_multiplier + 0.1)
                        
                        sound_manager.play_sound('score')
                        
                        # Add score particles
                        for _ in range(5):
                            particles.append(Particle(player.x, player.y, GOLD))

                    obstacle.move(current_speed)

                    if obstacle.x + obstacle.width < 0:
                        obstacles_to_remove.append(obstacle)

                # Add new obstacle if needed
                if add_obstacle:
                    new_gap_size = gap_size
                    # Occasionally make smaller gaps for extra challenge
                    if score > 10 and random.random() < 0.2:
                        new_gap_size = max(120, gap_size - 30)
                    
                    new_x = max(SCREEN_WIDTH, obstacles[-1].x + OBSTACLE_SPACING)
                    obstacles.append(Obstacle(new_x, new_gap_size))

                # Remove offscreen obstacles
                for obstacle in obstacles_to_remove:
                    obstacles.remove(obstacle)

                # Check for ground/ceiling collision
                if player.y + player.radius > ground.y or player.y - player.radius < 0:
                    if not player.has_shield:
                        game_over = True
                        sound_manager.play_sound('hit')
                    else:
                        # Bounce off with shield
                        player.velocity = FLAP_STRENGTH
                        player.has_shield = False
                        player.invulnerable = True
                        player.invulnerable_time = 60

                # Reset combo on no recent score
                if len([o for o in obstacles if not o.passed and o.x > player.x]) > 2:
                    combo_multiplier = max(1, combo_multiplier - 0.02)

            # Draw the enhanced game screen
            draw_game_screen(screen, player, obstacles, ground, score, clouds, particles, 
                           stars, powerups, difficulty, time_multiplier, double_score_time)

            # Show game over screen if game is over
            if game_over:
                # Check for new high score
                is_new_high_score = high_score_manager.add_score(username, score, difficulty)
                
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.fill(BLACK)
                overlay.set_alpha(128)
                screen.blit(overlay, (0, 0))

                # Game over text
                game_over_text = GAME_OVER_FONT.render("GAME OVER", 1, RED)
                screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2,
                                             SCREEN_HEIGHT // 2 - 150))

                # Show new high score message
                if is_new_high_score:
                    new_high_text = MENU_FONT.render("NEW HIGH SCORE!", 1, GOLD)
                    screen.blit(new_high_text, (SCREEN_WIDTH // 2 - new_high_text.get_width() // 2,
                                               SCREEN_HEIGHT // 2 - 100))

                # Show final score and best score
                final_score_text = MENU_FONT.render(f"Score: {score}", 1, WHITE)
                screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2,
                                             SCREEN_HEIGHT // 2 - 50))
                
                best_text = SMALL_FONT.render(f"Best: {max(best_score, score)}", 1, GOLD)
                screen.blit(best_text, (SCREEN_WIDTH // 2 - best_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 - 20))

                # Difficulty and player info
                info_text = SMALL_FONT.render(f"Player: {username} | Difficulty: {DIFFICULTY_LEVELS[difficulty]['name']}", 1, WHITE)
                screen.blit(info_text, (SCREEN_WIDTH // 2 - info_text.get_width() // 2,
                                      SCREEN_HEIGHT // 2 + 20))

                # Restart instructions
                restart_text = MENU_FONT.render("Press R to restart", 1, WHITE)
                screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2,
                                         SCREEN_HEIGHT // 2 + 80))

                # Switch player instructions
                switch_text = MENU_FONT.render("Press T to change player/difficulty", 1, WHITE)
                screen.blit(switch_text, (SCREEN_WIDTH // 2 - switch_text.get_width() // 2,
                                        SCREEN_HEIGHT // 2 + 120))

                pygame.display.update()


if __name__ == "__main__":
    # Create a data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)

    # Main game loop
    while True:
        main()