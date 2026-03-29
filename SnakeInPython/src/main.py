import pygame
import sys
import random
import os

pygame.init()

# Constants
SW, SH = 650, 650
BLOCK_SIZE = 50
FONT_LARGE = pygame.font.Font(None, 36)  # Smaller font size for better fit
FONT_SMALL = pygame.font.Font(None, 24)  # Even smaller font for instructions

screen = pygame.display.set_mode((SW, SH))
pygame.display.set_caption("Snake!")
clock = pygame.time.Clock()

# File to save high score
SCORE_FILE = "snake_high_score.txt"


def load_high_score():
    """Load high score from file"""
    if os.path.exists(SCORE_FILE):
        try:
            with open(SCORE_FILE, 'r') as file:
                return int(file.read().strip())
        except:
            return 0
    return 0


def save_high_score(score):
    """Save high score to file"""
    try:
        with open(SCORE_FILE, 'w') as file:
            file.write(str(score))
    except:
        print("Failed to save high score")


class Snake:
    def __init__(self):
        self.reset()

    def update(self):
        if self.dead:
            return False

        # Check collisions with body and boundaries
        for square in self.body:
            if self.head.colliderect(square):
                self.dead = True
                return False

        # Check boundary collisions
        if not (0 <= self.head.x < SW and 0 <= self.head.y < SH):
            self.dead = True
            return False

        # Update body
        self.body.insert(0, self.head.copy())
        if self.head.colliderect(apple.rect):
            apple.randomize(self.body + [self.head])
            self.grow = True
            return True  # Return True if apple was eaten
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False
        return False  # Return False if no apple was eaten

    def move(self):
        # Separate movement from update logic
        self.head.x += self.xdir * BLOCK_SIZE
        self.head.y += self.ydir * BLOCK_SIZE

    def reset(self):
        self.x, self.y = BLOCK_SIZE, BLOCK_SIZE
        self.head = pygame.Rect(self.x, self.y, BLOCK_SIZE, BLOCK_SIZE)
        self.body = [pygame.Rect(self.x - BLOCK_SIZE, self.y, BLOCK_SIZE, BLOCK_SIZE)]
        self.xdir = 1
        self.ydir = 0
        self.dead = False
        self.grow = False

    def draw(self, screen):
        # Draw head with a different color
        pygame.draw.rect(screen, "#00FF00", self.head, border_radius=8)  # Head color
        # Draw body segments
        for segment in self.body:
            pygame.draw.rect(screen, "#00CC00", segment, border_radius=5)  # Body color


class Apple:
    def __init__(self, snake_body=None):
        self.rect = pygame.Rect(-BLOCK_SIZE, -BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE)
        if snake_body is None:
            snake_body = []
        self.randomize(snake_body)

    def randomize(self, snake_body):
        while True:
            x = random.randint(0, (SW - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            y = random.randint(0, (SH - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
            self.rect.topleft = (x, y)
            if not any(self.rect.colliderect(seg) for seg in snake_body):
                break

    def draw(self, screen):
        # Draw apple as a red circle
        pygame.draw.circle(screen, "red", self.rect.center, BLOCK_SIZE // 2 - 2)


def reset_game():
    """Reset the game state"""
    global snake, apple, score, game_over, paused
    snake = Snake()
    apple = Apple(snake.body + [snake.head])
    score = 0
    game_over = False
    paused = False


# Game initialization
high_score = load_high_score()
snake = Snake()
apple = Apple(snake.body + [snake.head])
score = 0
game_over = False
paused = False
waiting_for_restart = False  # Flag to prevent auto-restart

# Game instructions
controls_text = [
    "Controls:",
    "Arrow Keys - Move Snake",
    "P - Pause Game",
    "Space - Restart (when game over)"
]

# Constant slower speed
GAME_SPEED = 8  # Reduced constant speed

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # Save high score before exiting
            if score > high_score:
                high_score = score
                save_high_score(high_score)
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_over:
                if event.key == pygame.K_SPACE:
                    reset_game()
                    waiting_for_restart = False
            else:
                if event.key == pygame.K_p:
                    paused = not paused
                elif not paused:
                    if event.key == pygame.K_DOWN and snake.ydir != -1:
                        snake.ydir = 1
                        snake.xdir = 0
                    elif event.key == pygame.K_UP and snake.ydir != 1:
                        snake.ydir = -1
                        snake.xdir = 0
                    elif event.key == pygame.K_RIGHT and snake.xdir != -1:
                        snake.xdir = 1
                        snake.ydir = 0
                    elif event.key == pygame.K_LEFT and snake.xdir != 1:
                        snake.xdir = -1
                        snake.ydir = 0

    # Game logic
    if not game_over and not paused:
        # Move the snake's head first
        snake.move()
        # Then update the body and check for collisions
        if snake.update():  # If apple was eaten
            score += 1

        # Check if snake died
        if snake.dead and not waiting_for_restart:
            game_over = True
            waiting_for_restart = True
            # Update and save high score if needed
            if score > high_score:
                high_score = score
                save_high_score(high_score)

    # Drawing
    screen.fill((20, 20, 20))  # Dark background

    # Draw grid
    for x in range(0, SW, BLOCK_SIZE):
        for y in range(0, SH, BLOCK_SIZE):
            rect = pygame.Rect(x, y, BLOCK_SIZE, BLOCK_SIZE)
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)

    snake.draw(screen)
    apple.draw(screen)

    # Score display with smaller font
    score_text = FONT_LARGE.render(f"Score: {score}", True, "white")
    screen.blit(score_text, (10, 10))
    high_score_text = FONT_LARGE.render(f"High: {high_score}", True, "white")
    screen.blit(high_score_text, (SW - high_score_text.get_width() - 10, 10))

    # Game over display
    if game_over:
        game_over_surface = pygame.Surface((SW // 2, SH // 4))
        game_over_surface.fill((40, 40, 40))
        game_over_surface.set_alpha(200)
        screen.blit(game_over_surface, (SW // 4, SH // 3))

        game_over_text = FONT_LARGE.render("Game Over!", True, "white")
        screen.blit(game_over_text, (SW // 2 - game_over_text.get_width() // 2, SH // 3 + 20))

        restart_text = FONT_LARGE.render("Press SPACE to restart", True, "white")
        screen.blit(restart_text, (SW // 2 - restart_text.get_width() // 2, SH // 3 + 60))

        final_score = FONT_LARGE.render(f"Final Score: {score}", True, "white")
        screen.blit(final_score, (SW // 2 - final_score.get_width() // 2, SH // 3 + 100))

        if score == high_score and score > 0:
            new_high_text = FONT_LARGE.render("New High Score!", True, "yellow")
            screen.blit(new_high_text, (SW // 2 - new_high_text.get_width() // 2, SH // 3 + 140))

    # Pause display
    if paused and not game_over:
        pause_surface = pygame.Surface((SW // 3, SH // 5))
        pause_surface.fill((40, 40, 40))
        pause_surface.set_alpha(200)
        screen.blit(pause_surface, (SW // 3, SH // 3))

        pause_text = FONT_LARGE.render("PAUSED", True, "white")
        screen.blit(pause_text, (SW // 2 - pause_text.get_width() // 2, SH // 3 + 20))

        continue_text = FONT_LARGE.render("Press P to continue", True, "white")
        screen.blit(continue_text, (SW // 2 - continue_text.get_width() // 2, SH // 3 + 60))

    # Draw control instructions at the bottom
    if not game_over:
        for i, text in enumerate(controls_text):
            control_text = FONT_SMALL.render(text, True, (180, 180, 180))
            screen.blit(control_text, (10, SH - 80 + i * 20))

    pygame.display.update()

    # Use constant lower speed instead of dynamic speed
    clock.tick(GAME_SPEED)