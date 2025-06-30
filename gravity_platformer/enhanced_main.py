import pygame
import sys
import math
import os
import json
from pygame.locals import *
import game_manager
import random

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
    def __init__(self, x, y, color=BLUE, player_num=1):
        super().__init__()
        self.image = pygame.Surface((30, 50), pygame.SRCALPHA)
        self.original_image = self.image.copy()

        # Draw player with a more interesting shape
        pygame.draw.rect(self.image, color, (0, 0, 30, 50))
        pygame.draw.circle(self.image, WHITE, (15, 15), 10)  # Head

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
        self.player_num = player_num
        self.facing_right = True
        self.jump_count = 0
        self.max_jumps = 2  # Double jump
        self.health = 100
        self.invincible = False
        self.invincible_timer = 0

        # Animation variables
        self.animation_frame = 0
        self.animation_delay = 5
        self.animation_counter = 0

    def update(self, platforms, planets=None, hazards=None):
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

            # Rotate player to face gravity center
            angle = math.degrees(math.atan2(-dy, -dx))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)
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
                self.jump_count = 0  # Reset jump count when on ground
            elif self.vel_y < 0:
                self.rect.top = platform.rect.bottom
            self.vel_y = 0

        # Check for planet collisions (for gravity switching)
        if planets:
            for planet in planets:
                dx = planet.center[0] - (self.rect.x + self.rect.width/2)
                dy = planet.center[1] - (self.rect.y + self.rect.height/2)
                distance = math.sqrt(dx*dx + dy*dy)

                # If very close to planet, consider on ground
                if distance < planet.radius + 30:
                    self.on_ground = True
                    self.jump_count = 0

        # Check for hazard collisions
        if hazards and not self.invincible:
            if pygame.sprite.spritecollide(self, hazards, False):
                self.health -= 10
                self.invincible = True
                self.invincible_timer = 60  # 1 second of invincibility

        # Update invincibility
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

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
            self.jump_count = 0

        # Update animation
        if abs(self.vel_x) > 1:
            self.animation_counter += 1
            if self.animation_counter >= self.animation_delay:
                self.animation_counter = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0

    def jump(self):
        if self.on_ground or self.jump_count < self.max_jumps:
            self.jump_count += 1
            if self.gravity_center:
                # Jump away from gravity center
                dx = (self.rect.x + self.rect.width/2) - self.gravity_center[0]
                dy = (self.rect.y + self.rect.height/2) - self.gravity_center[1]
                distance = max(1, math.sqrt(dx*dx + dy*dy))
                dx /= distance
                dy /= distance
                self.vel_x += dx * self.jump_strength
                self.vel_y += dy * self.jump_strength
            else:
                self.vel_y = -self.jump_strength

            # Add jump effect
            self.on_ground = False

    def move_left(self):
        self.vel_x = -self.move_speed
        self.facing_right = False

    def move_right(self):
        self.vel_x = self.move_speed
        self.facing_right = True

    def draw_health_bar(self, surface):
        bar_width = 30
        bar_height = 5
        fill = (self.health / 100) * bar_width
        outline_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, bar_height)
        fill_rect = pygame.Rect(self.rect.x, self.rect.y - 10, fill, bar_height)
        pygame.draw.rect(surface, RED, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)

   # Platform class
    class Platform(pygame.sprite.Sprite):
      def __init__(self, x, y, width, height, color=GREEN):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)

    # Add some texture with safer color handling
        darker_color = (
            max(0, color[0]-20),
            max(0, color[1]-20),
            max(0, color[2]-20)
        )

        for i in range(0, width, 10):
            pygame.draw.line(self.image, darker_color, (i, 0), (i, height), 1)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Planet class (gravity source)
class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y, radius, color=YELLOW):
        super().__init__()
        self.radius = radius
        self.image = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)

        # Draw planet with some detail using safer color handling
        pygame.draw.circle(self.image, color, (radius, radius), radius)

        darker_color = (
            max(0, color[0]-30),
            max(0, color[1]-30),
            max(0, color[2]-30)
        )
        pygame.draw.circle(self.image, darker_color, (radius, radius), radius, 2)

        # Add some craters with safer color handling
        darkest_color = (
            max(0, color[0]-50),
            max(0, color[1]-50),
            max(0, color[2]-50)
        )

        import random  # Make sure this is at the top of the file
        for _ in range(5):
            crater_x = random.randint(radius//2, radius*3//2)
            crater_y = random.randint(radius//2, radius*3//2)
            crater_size = random.randint(3, 8)
            pygame.draw.circle(self.image, darkest_color, (crater_x, crater_y), crater_size)

        self.rect = self.image.get_rect()
        self.rect.x = x - radius
        self.rect.y = y - radius
        self.center = (x, y)

# Star collectible
class Star(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)

        # Draw star
        pygame.draw.polygon(self.image, YELLOW, [
            (10, 0), (13, 7), (20, 7), (14, 12),
            (16, 20), (10, 15), (4, 20), (6, 12),
            (0, 7), (7, 7)
        ])

        # Add glow effect
        pygame.draw.polygon(self.image, WHITE, [
            (10, 2), (12, 7), (18, 7), (13, 11),
            (15, 18), (10, 14), (5, 18), (7, 11),
            (2, 7), (8, 7)
        ], 1)

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Animation
        self.original_y = y
        self.float_offset = 0
        self.float_speed = 0.05
        self.rotation = 0
        self.original_image = self.image.copy()

    def update(self):
        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * 5
        self.rect.y = self.original_y + self.float_offset

        # Rotation animation
        self.rotation = (self.rotation + 1) % 360
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.rect.center)

# Hazard class
class Hazard(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)

        # Draw spikes
        spike_width = 10
        num_spikes = width // spike_width
        for i in range(num_spikes):
            pygame.draw.polygon(self.image, RED, [
                (i * spike_width, height),
                ((i + 0.5) * spike_width, 0),
                ((i + 1) * spike_width, height)
            ])

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

# Particle effect
class Particle:
    def __init__(self, x, y, color, velocity, size=3, life=30):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.size = size
        self.life = life
        self.original_life = life

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        # Shrink as life decreases
        self.size = max(1, self.size * (self.life / self.original_life))

    def draw(self, surface):
        alpha = int(255 * (self.life / self.original_life))
        color = (*self.color, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))

# Import needed for random generation
import random

# Game class
class Game:
    def __init__(self):
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.planets = pygame.sprite.Group()
        self.stars = pygame.sprite.Group()
        self.hazards = pygame.sprite.Group()

        # Game variables
        self.score = 0
        self.active_planet = None
        self.particles = []
        self.current_level = 1
        self.game_manager = game_manager.GameManager(screen, clock)

        # Load level
        self.load_level(self.current_level)

    def load_level(self, level_num):
        # Clear existing sprites
        self.all_sprites.empty()
        self.platforms.empty()
        self.planets.empty()
        self.stars.empty()
        self.hazards.empty()

        # Load level data
        level_data = self.game_manager.load_level(level_num)

        # Create player
        self.player = Player(100, 100)
        self.all_sprites.add(self.player)

        # Create platforms
        for platform_data in level_data["platforms"]:
            platform = Platform(
                platform_data["x"],
                platform_data["y"],
                platform_data["width"],
                platform_data["height"]
            )
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        # Create planets
        for planet_data in level_data["planets"]:
            planet = Planet(
                planet_data["x"],
                planet_data["y"],
                planet_data["radius"]
            )
            self.planets.add(planet)
            self.all_sprites.add(planet)

        # Create stars
        for star_data in level_data["stars"]:
            star = Star(star_data["x"], star_data["y"])
            self.stars.add(star)
            self.all_sprites.add(star)

        # Add some hazards
        if "hazards" in level_data:
            for hazard_data in level_data["hazards"]:
                hazard = Hazard(
                    hazard_data["x"],
                    hazard_data["y"],
                    hazard_data["width"],
                    hazard_data["height"]
                )
                self.hazards.add(hazard)
                self.all_sprites.add(hazard)

        # Reset game variables
        self.active_planet = None
        self.player.gravity_center = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.player.jump()
                    self.create_jump_particles()
                if event.key == K_g:
                    # Toggle gravity center
                    if self.active_planet:
                        self.player.gravity_center = None
                        self.active_planet = None
                    else:
                        # Find closest planet
                        closest = None
                        min_dist = float('inf')
                        for planet in self.planets:
                            dx = planet.center[0] - (self.player.rect.x + self.player.rect.width/2)
                            dy = planet.center[1] - (self.player.rect.y + self.player.rect.height/2)
                            dist = math.sqrt(dx*dx + dy*dy)
                            if dist < min_dist:
                                min_dist = dist
                                closest = planet

                        if closest and min_dist < 200:  # Only if within range
                            self.active_planet = closest
                            self.player.gravity_center = closest.center
                            self.create_gravity_switch_particles()
                if event.key == K_ESCAPE:
                    # Return to menu
                    return "menu"

        # Continuous key presses
        keys = pygame.key.get_pressed()
        if keys[K_LEFT]:
            self.player.move_left()
            if self.player.on_ground:
                self.create_movement_particles()
        if keys[K_RIGHT]:
            self.player.move_right()
            if self.player.on_ground:
                self.create_movement_particles()

        return None  # Continue game

    def create_jump_particles(self):
        for _ in range(10):
            velocity = [random.uniform(-2, 2), random.uniform(1, 3)]
            particle = Particle(
                self.player.rect.centerx,
                self.player.rect.bottom,
                WHITE,
                velocity,
                size=random.randint(2, 5),
                life=random.randint(20, 40)
            )
            self.particles.append(particle)

    def create_movement_particles(self):
        if random.random() < 0.3:  # Only create particles sometimes
            direction = -1 if self.player.facing_right else 1
            velocity = [random.uniform(0.5, 2) * direction, random.uniform(-0.5, 0.5)]
            particle = Particle(
                self.player.rect.centerx - (direction * self.player.rect.width/2),
                self.player.rect.bottom - 5,
                (200, 200, 200),
                velocity,
                size=random.randint(1, 3),
                life=random.randint(10, 20)
            )
            self.particles.append(particle)

    def create_gravity_switch_particles(self):
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            particle = Particle(
                self.player.rect.centerx,
                self.player.rect.centery,
                PURPLE,
                velocity,
                size=random.randint(3, 6),
                life=random.randint(30, 60)
            )
            self.particles.append(particle)

    def create_star_collect_particles(self, x, y):
        for _ in range(15):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 4)
            velocity = [math.cos(angle) * speed, math.sin(angle) * speed]
            particle = Particle(
                x, y,
                YELLOW,
                velocity,
                size=random.randint(2, 5),
                life=random.randint(30, 50)
            )
            self.particles.append(particle)

    def update(self):
        # Update player with platform collisions
        self.player.update(self.platforms, self.planets, self.hazards)

        # Update stars
        self.stars.update()

        # Check for star collisions
        stars_collected = pygame.sprite.spritecollide(self.player, self.stars, True)
        for star in stars_collected:
            self.score += 10
            self.create_star_collect_particles(star.rect.centerx, star.rect.centery)

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Check if level is complete (all stars collected)
        if len(self.stars) == 0:
            self.game_manager.score = self.score
            self.game_manager.state = 3  # LEVEL_COMPLETE
            return "level_complete"

        # Check if player died
        if self.player.health <= 0:
            self.game_manager.lives -= 1
            if self.game_manager.lives <= 0:
                self.game_manager.state = 2  # GAME_OVER
                return "game_over"
            else:
                # Respawn player
                self.player.rect.x = 100
                self.player.rect.y = 100
                self.player.health = 100
                self.player.vel_x = 0
                self.player.vel_y = 0

        return None  # Continue game

    def draw(self):
        screen.fill(BLACK)

        # Draw background with parallax effect
        for i in range(50):
            star_x = (i * 20 + pygame.time.get_ticks() // 100) % SCREEN_WIDTH
            star_y = (i * 15) % SCREEN_HEIGHT
            pygame.draw.circle(screen, WHITE, (star_x, star_y), 1)

        # Draw all sprites
        self.all_sprites.draw(screen)

        # Draw player health bar
        self.player.draw_health_bar(screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

        # Draw active planet indicator
        if self.active_planet:
            pygame.draw.line(
                screen,
                RED,
                (self.player.rect.centerx, self.player.rect.centery),
                self.active_planet.center,
                2
            )

        # Draw HUD
        self.game_manager.score = self.score
        self.game_manager.draw_hud()

        pygame.display.flip()

# Main game loop
def main():
    # Create game
    game = Game()

    # Game loop
    running = True
    while running:
        # Check if we should go to menu
        if game.game_manager.state != 1:  # Not PLAYING
            action, level = game.game_manager.run()
            if action == "start_game" or action == "restart_game":
                game.current_level = level
                game.load_level(level)
                game.game_manager.state = 1  # PLAYING
            elif action == "next_level":
                game.current_level = level
                game.load_level(level)
                game.game_manager.state = 1  # PLAYING
        else:
            # Handle events
            result = game.handle_events()
            if result == "menu":
                game.game_manager.state = 0  # MENU
                continue

            # Update game
            result = game.update()
            if result == "level_complete" or result == "game_over":
                continue

            # Draw game
            game.draw()

            # Cap the frame rate
            clock.tick(FPS)

if __name__ == "__main__":
    main()