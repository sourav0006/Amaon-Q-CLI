import pygame
import sys
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = 10
MOVE_SPEED = 5

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gravity Platformer")
clock = pygame.time.Clock()

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, color=BLUE):
        super().__init__()
        self.image = pygame.Surface((30, 50))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.gravity_center = None
        self.gravity_strength = GRAVITY
        self.jump_strength = JUMP_STRENGTH
        self.move_speed = MOVE_SPEED

    def update(self, platforms):
        # Apply gravity towards gravity center if it exists
        if self.gravity_center:
            dx = self.gravity_center[0] - (self.rect.x + self.rect.width/2)
            dy = self.gravity_center[1] - (self.rect.y + self.rect.height/2)
            distance = max(1, math.sqrt(dx*dx + dy*dy))

            # Normalize and apply gravity
            dx /= distance
            dy /= distance
            self.vel_x += dx * self.gravity_strength
            self.vel_y += dy * self.gravity_strength
        else:
            # Default gravity (downward)
            self.vel_y += self.gravity_strength

        # Apply velocity
        self.rect.x += int(self.vel_x)

        # Check for horizontal collisions
        hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_list:
            if self.vel_x > 0:
                self.rect.right = platform.rect.left
            elif self.vel_x < 0:
                self.rect.left = platform.rect.right
            self.vel_x = 0

        # Apply vertical velocity
        self.rect.y += int(self.vel_y)

        # Check for vertical collisions
        self.on_ground = False
        hit_list = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hit_list:
            if self.vel_y > 0:
                self.rect.bottom = platform.rect.top
                self.on_ground = True
            elif self.vel_y < 0:
                self.rect.top = platform.rect.bottom
            self.vel_y = 0

        # Apply friction
        self.vel_x *= 0.9

        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > SCREEN_HEIGHT:
            self.rect.bottom = SCREEN_HEIGHT
            self.on_ground = True

    def jump(self):
        if self.on_ground:
            self.vel_y = -self.jump_strength

    def move_left(self):
        self.vel_x = -self.move_speed

    def move_right(self):
        self.vel_x = self.move_speed

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Planet class (gravity source)
class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color=YELLOW):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (radius, radius), radius)
        self.rect = self.image.get_rect()
        self.rect.x = x - radius
        self.rect.y = y - radius
        self.center = (x, y)

# Star collectible
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, YELLOW, [
            (10, 0), (13, 7), (20, 7), (14, 12),
            (16, 20), (10, 15), (4, 20), (6, 12),
            (0, 7), (7, 7)
        ])
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Game state class
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.planets = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()

        # Create players
        self.player1 = Player(100, 100)
        self.all_sprites.add(self.player1)

        # Create platforms
        ground = Platform(0, SCREEN_HEIGHT - 40, SCREEN_WIDTH, 40)
        platform1 = Platform(100, 400, 200, 20)
        platform2 = Platform(500, 300, 200, 20)
        platform3 = Platform(300, 200, 200, 20)

        self.platforms.add(ground, platform1, platform2, platform3)
        self.all_sprites.add(ground, platform1, platform2, platform3)

        # Create planets (gravity sources)
        planet1 = Planet(400, 300, 50)
        self.planets.add(planet1)
        self.all_sprites.add(planet1)

        # Create stars
        for i in range(5):
            star = Star(100 + i * 150, 100)
            self.stars.add(star)
            self.all_sprites.add(star)

        # Game variables
        self.score = 0
        self.active_planet = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.player1.jump()
                if event.key == K_g:
                    # Toggle gravity center
                    if self.active_planet:
                        self.player1.gravity_center = None
                        self.active_planet = None
                    else:
                        # Find closest planet
                        closest = None
                        min_dist = float('inf')
                        for planet in self.planets:
                            dx = planet.center[0] - (self.player1.rect.x + self.player1.rect.width/2)
                            dy = planet.center[1] - (self.player1.rect.y + self.player1.rect.height/2)
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < min_dist:
                                min_dist = dist
                                closest = planet

                        if closest:
                            self.active_planet = closest
                            self.player1.gravity_center = closest.center

        # Continuous key presses
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.player1.move_left()
        if keys[K_RIGHT]:
            self.player1.move_right()

    def update(self):
        # Update player with platform collisions
        self.player1.update(self.platforms)

        # Check for star collisions
        stars_collected = pygame.sprite.spritecollide(self.player1, self.stars, True)
        self.score += len(stars_collected)

        # Check if all stars are collected
        if len(self.stars) == 0:
            print("Level complete! Score:", self.score)
            self.reset()

    def draw(self):
        screen.fill(BLACK)

        # Draw all sprites
        self.all_sprites.draw(screen)

        # Draw score
        font = pygame.font.SysFont(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Draw active planet indicator
        if self.active_planet:
            pygame.draw.line(
                screen,
                RED,
                (self.player1.rect.centerx, self.player1.rect.centery),
                self.active_planet.center,
                2
            )

        pygame.display.flip()

# Main game loop
def main():
    game = GameState()

    # Game loop
    while True:
        game.handle_events()
        game.update()
        game.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()