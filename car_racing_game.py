import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)

# Road constants
ROAD_WIDTH = 500
ROAD_MARK_WIDTH = 10
LANE_WIDTH = ROAD_WIDTH // 3

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

class PlayerCar:
    def __init__(self):
        self.width = 50
        self.height = 80
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 150
        self.speed = 0
        self.acceleration = 0.2
        self.deceleration = 0.3
        self.max_speed = 10
        self.steering = 0
        self.direction = 0
        self.steering_speed = 0.03

        # Create a car shape instead of just a rectangle
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(self.image, (200, 0, 0), (5, 5, self.width-10, self.height-10), border_radius=8)
        pygame.draw.rect(self.image, (150, 150, 150), (10, 15, self.width-20, 20))  # Windshield
        pygame.draw.rect(self.image, (150, 150, 150), (10, self.height-35, self.width-20, 20))  # Rear window

    def update(self, keys):
        # Handle acceleration
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + self.acceleration, self.max_speed)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - self.deceleration, -self.max_speed/2)
        else:
            # Apply friction when no key is pressed
            if self.speed > 0:
                self.speed = max(self.speed - 0.1, 0)
            elif self.speed < 0:
                self.speed = min(self.speed + 0.1, 0)

        # Handle steering
        if keys[pygame.K_LEFT]:
            self.steering = -self.steering_speed
        elif keys[pygame.K_RIGHT]:
            self.steering = self.steering_speed
        else:
            self.steering = 0

        # Apply steering (more effect at higher speeds)
        steering_factor = abs(self.speed) / self.max_speed
        self.direction += self.steering * steering_factor

        # Update position based on speed and direction
        self.x += math.sin(self.direction) * self.speed

        # Keep player on screen
        road_left = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2
        road_right = SCREEN_WIDTH // 2 + ROAD_WIDTH // 2
        self.x = max(road_left + self.width // 2, min(self.x, road_right - self.width // 2))

    def draw(self, screen):
        rotated_image = pygame.transform.rotate(self.image, -self.direction * 180 / math.pi * 0.5)  # Scale down rotation for better visuals
        new_rect = rotated_image.get_rect(center=(self.x, self.y))
        screen.blit(rotated_image, new_rect.topleft)

class EnemyCar:
    def __init__(self, lane):
        self.width = 50
        self.height = 80
        self.lane = lane
        self.x = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH * lane + LANE_WIDTH // 2
        self.y = -100  # Start above the screen
        self.speed = random.uniform(2, 5)

        # Create a car shape with random color
        car_color = random.choice([(0, 0, 200), (0, 200, 0), (200, 200, 0), (200, 0, 200), (0, 200, 200)])
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, car_color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(self.image, (car_color[0]*0.8, car_color[1]*0.8, car_color[2]*0.8),
                         (5, 5, self.width-10, self.height-10), border_radius=8)
        pygame.draw.rect(self.image, (150, 150, 150), (10, 15, self.width-20, 20))  # Windshield
        pygame.draw.rect(self.image, (150, 150, 150), (10, self.height-35, self.width-20, 20))  # Rear window

    def update(self, player_speed):
        # Move relative to player's speed to create passing effect
        self.y += (self.speed - player_speed)

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))

class PowerUp:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.lane = random.randint(0, 2)
        self.x = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH * self.lane + LANE_WIDTH // 2
        self.y = -100
        self.speed = 3
        self.type = random.choice(["speed", "invincible"])

        # Create power-up shape
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if self.type == "speed":
            pygame.draw.circle(self.image, (255, 215, 0), (self.width//2, self.height//2), self.width//2)
            pygame.draw.polygon(self.image, BLACK, [(10, 15), (20, 5), (20, 15), (30, 5), (20, 25), (20, 15), (10, 25)])
        else:  # invincible
            pygame.draw.circle(self.image, (0, 255, 255), (self.width//2, self.height//2), self.width//2)
            pygame.draw.polygon(self.image, BLACK, [(15, 5), (25, 5), (25, 25), (15, 25)])

    def update(self, player_speed):
        self.y += (self.speed - player_speed)

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))

class Obstacle:
    def __init__(self):
        self.width = 80
        self.height = 80
        self.lane = random.randint(0, 2)
        self.x = SCREEN_WIDTH // 2 - ROAD_WIDTH // 2 + LANE_WIDTH * self.lane + LANE_WIDTH // 2
        self.y = -100  # Start above the screen
        self.speed = 2

        # Create obstacle shape (oil spill or rock)
        self.type = random.choice(["oil", "rock"])
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        if self.type == "oil":
            # Draw oil spill
            pygame.draw.ellipse(self.image, (30, 30, 30), (0, 20, self.width, self.height - 20))
            pygame.draw.ellipse(self.image, (10, 10, 10), (10, 30, self.width - 20, self.height - 40))
            # Add some shine
            pygame.draw.ellipse(self.image, (50, 50, 70), (15, 35, 20, 10))
        else:  # rock
            # Draw rock
            points = []
            center_x, center_y = self.width // 2, self.height // 2
            for i in range(8):
                angle = 2 * math.pi * i / 8
                distance = random.randint(25, 35)
                x = center_x + math.cos(angle) * distance
                y = center_y + math.sin(angle) * distance
                points.append((x, y))

            pygame.draw.polygon(self.image, (100, 100, 100), points)
            pygame.draw.polygon(self.image, (80, 80, 80), points, 3)

    def update(self, player_speed):
        # Move relative to player's speed to create passing effect
        self.y += (self.speed - player_speed)

    def draw(self, screen):
        screen.blit(self.image, (self.x - self.width // 2, self.y - self.height // 2))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(3, 8)
        self.speed_x = random.uniform(-2, 2)
        self.speed_y = random.uniform(-2, 2)
        self.life = random.randint(20, 40)

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Game:
    def __init__(self):
        self.reset()
        self.state = MENU
        self.font = pygame.font.SysFont(None, 36)
        self.big_font = pygame.font.SysFont(None, 72)

        # Background elements
        self.trees = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(20)]
        self.clouds = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT//3), random.uniform(0.5, 1.5))
                      for _ in range(10)]

    def reset(self):
        self.player = PlayerCar()
        self.enemy_cars = []
        self.power_ups = []
        self.obstacles = []
        self.particles = []
        self.road_y = 0
        self.score = 0
        self.distance = 0
        self.game_time = 0
        self.spawn_timer = 0
        self.powerup_timer = 0
        self.powerup_spawn_timer = 0
        self.obstacle_spawn_timer = 0
        self.invincible = False
        self.invincible_timer = 0
        self.speed_boost = False
        self.speed_boost_timer = 0

    def spawn_enemy(self):
        # Determine which lanes are occupied
        occupied_lanes = [car.lane for car in self.enemy_cars if car.y < 200]
        available_lanes = [i for i in range(3) if i not in occupied_lanes]

        if available_lanes:
            lane = random.choice(available_lanes)
            self.enemy_cars.append(EnemyCar(lane))

    def spawn_powerup(self):
        if random.random() < 0.3:  # 30% chance to spawn a power-up
            self.power_ups.append(PowerUp())

    def spawn_obstacle(self):
        if random.random() < 0.4:  # 40% chance to spawn an obstacle
            self.obstacles.append(Obstacle())

    def create_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update_menu(self, keys):
        if keys[pygame.K_RETURN]:
            self.state = PLAYING
            self.reset()

    def update_playing(self, keys):
        # Update player
        old_speed = self.player.speed
        self.player.update(keys)

        # Create exhaust particles
        if self.player.speed > 0 and random.random() < 0.3:
            angle = self.player.direction + math.pi  # Opposite direction
            exhaust_x = self.player.x - math.sin(angle) * self.player.height / 2
            exhaust_y = self.player.y - math.cos(angle) * self.player.height / 2
            self.create_particles(exhaust_x, exhaust_y, (100, 100, 100), 2)

        # Update road position based on player speed
        self.road_y = (self.road_y + self.player.speed) % 100

        # Update background elements
        for i, (x, y) in enumerate(self.trees):
            new_y = (y + self.player.speed) % SCREEN_HEIGHT
            self.trees[i] = (x, new_y)

        for i, (x, y, speed) in enumerate(self.clouds):
            new_x = (x + speed * 0.2) % SCREEN_WIDTH
            new_y = (y + self.player.speed * 0.2) % (SCREEN_HEIGHT // 2)
            self.clouds[i] = (new_x, new_y, speed)

        # Update distance
        self.distance += self.player.speed / 10

        # Update game time
        self.game_time += 1/FPS

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.life <= 0:
                self.particles.remove(particle)

        # Update power-ups
        for powerup in self.power_ups[:]:
            powerup.update(self.player.speed)

            # Check if power-up is collected
            if (abs(powerup.x - self.player.x) < (powerup.width + self.player.width) // 2 and
                abs(powerup.y - self.player.y) < (powerup.height + self.player.height) // 2):
                self.power_ups.remove(powerup)

                if powerup.type == "speed":
                    self.speed_boost = True
                    self.speed_boost_timer = FPS * 5  # 5 seconds
                    self.player.max_speed = 15  # Increase max speed
                elif powerup.type == "invincible":
                    self.invincible = True
                    self.invincible_timer = FPS * 5  # 5 seconds

                self.create_particles(powerup.x, powerup.y, (255, 255, 0), 20)

            # Remove if off screen
            if powerup.y > SCREEN_HEIGHT + 100:
                self.power_ups.remove(powerup)

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.player.speed)

            # Check if obstacle is hit
            if (abs(obstacle.x - self.player.x) < (obstacle.width + self.player.width) // 2 * 0.7 and
                abs(obstacle.y - self.player.y) < (obstacle.height + self.player.height) // 2 * 0.7):
                if not self.invincible:
                    self.create_particles(self.player.x, self.player.y, RED, 30)
                    self.state = GAME_OVER
                    return False
                else:
                    # If invincible, destroy the obstacle
                    self.obstacles.remove(obstacle)
                    self.create_particles(obstacle.x, obstacle.y, (100, 100, 100), 15)
                    continue

            # Remove if off screen
            if obstacle.y > SCREEN_HEIGHT + 100:
                self.obstacles.remove(obstacle)

        # Update enemy cars
        for car in self.enemy_cars[:]:
            car.update(self.player.speed)

            # Check if car is passed
            if car.y > SCREEN_HEIGHT + 100:
                self.enemy_cars.remove(car)
                self.score += 10

            # Check for collision
            if not self.invincible and (
                abs(car.x - self.player.x) < (car.width + self.player.width) // 2 * 0.8 and
                abs(car.y - self.player.y) < (car.height + self.player.height) // 2 * 0.8):
                self.create_particles(self.player.x, self.player.y, RED, 30)
                self.state = GAME_OVER
                return False

        # Update power-up timers
        if self.speed_boost:
            self.speed_boost_timer -= 1
            if self.speed_boost_timer <= 0:
                self.speed_boost = False
                self.player.max_speed = 10  # Reset max speed

        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

        # Spawn new enemy cars
        self.spawn_timer += 1
        spawn_interval = max(FPS * 1.5, FPS * 3 - self.game_time / 10)  # Spawn faster as time goes on
        if self.spawn_timer >= spawn_interval:
            self.spawn_enemy()
            self.spawn_timer = 0

        # Spawn power-ups
        self.powerup_spawn_timer += 1
        if self.powerup_spawn_timer >= FPS * 10:  # Every 10 seconds
            self.spawn_powerup()
            self.powerup_spawn_timer = 0

        # Spawn obstacles
        self.obstacle_spawn_timer += 1
        if self.obstacle_spawn_timer >= FPS * 5:  # Every 5 seconds
            self.spawn_obstacle()
            self.obstacle_spawn_timer = 0

        return True

    def update_game_over(self, keys):
        if keys[pygame.K_RETURN]:
            self.state = MENU

    def update(self, keys):
        if self.state == MENU:
            self.update_menu(keys)
            return True
        elif self.state == PLAYING:
            return self.update_playing(keys)
        elif self.state == GAME_OVER:
            self.update_game_over(keys)
            return True

    def draw_background(self, screen):
        # Draw sky
        screen.fill((135, 206, 235))  # Sky blue

        # Draw clouds
        for x, y, _ in self.clouds:
            pygame.draw.ellipse(screen, WHITE, (x, y, 100, 40))
            pygame.draw.ellipse(screen, WHITE, (x+25, y-15, 70, 30))
            pygame.draw.ellipse(screen, WHITE, (x+60, y+5, 50, 25))

        # Draw grass
        pygame.draw.rect(screen, GREEN, (0, SCREEN_HEIGHT//3, SCREEN_WIDTH, SCREEN_HEIGHT*2//3))

        # Draw trees
        for x, y in self.trees:
            if y > SCREEN_HEIGHT//3:  # Only draw trees on grass
                # Tree trunk
                pygame.draw.rect(screen, (139, 69, 19), (x, y, 10, 30))
                # Tree leaves
                pygame.draw.circle(screen, (34, 139, 34), (x+5, y-15), 25)

    def draw_road(self, screen):
        # Draw road
        pygame.draw.rect(screen, DARK_GRAY, (SCREEN_WIDTH//2 - ROAD_WIDTH//2, 0, ROAD_WIDTH, SCREEN_HEIGHT))

        # Draw road markings
        for i in range(-1, SCREEN_HEIGHT // 50 + 1):
            y = (i * 100 + self.road_y) % SCREEN_HEIGHT
            # Center line
            pygame.draw.rect(screen, YELLOW, (SCREEN_WIDTH//2 - ROAD_MARK_WIDTH//2, y, ROAD_MARK_WIDTH, 50))

            # Lane dividers
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - ROAD_WIDTH//6 - ROAD_MARK_WIDTH//2, y, ROAD_MARK_WIDTH, 50))
            pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 + ROAD_WIDTH//6 - ROAD_MARK_WIDTH//2, y, ROAD_MARK_WIDTH, 50))

        # Draw road edges
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 - ROAD_WIDTH//2 - 5, 0, 5, SCREEN_HEIGHT))
        pygame.draw.rect(screen, WHITE, (SCREEN_WIDTH//2 + ROAD_WIDTH//2, 0, 5, SCREEN_HEIGHT))

    def draw_menu(self, screen):
        self.draw_background(screen)
        self.draw_road(screen)

        # Draw title
        title_text = self.big_font.render("RACING GAME", True, WHITE)
        screen.blit(title_text, (SCREEN_WIDTH//2 - title_text.get_width()//2, SCREEN_HEIGHT//4))

        # Draw instructions
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking effect
            start_text = self.font.render("Press ENTER to Start", True, WHITE)
            screen.blit(start_text, (SCREEN_WIDTH//2 - start_text.get_width()//2, SCREEN_HEIGHT//2))

        # Draw controls
        controls_text = self.font.render("Controls: Arrow Keys", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH//2 - controls_text.get_width()//2, SCREEN_HEIGHT*2//3))

    def draw_playing(self, screen):
        self.draw_background(screen)
        self.draw_road(screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)

        # Draw power-ups
        for powerup in self.power_ups:
            powerup.draw(screen)

        # Draw enemy cars
        for car in self.enemy_cars:
            car.draw(screen)

        # Draw player with special effects if powered up
        if self.invincible:
            if int(pygame.time.get_ticks() / 100) % 2 == 0:  # Blinking effect
                self.player.draw(screen)
        else:
            self.player.draw(screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(screen)

        # Draw UI
        # Speedometer
        speed_text = self.font.render(f"Speed: {int(self.player.speed * 10)} km/h", True, WHITE)
        screen.blit(speed_text, (20, 20))

        # Speed bar
        pygame.draw.rect(screen, BLACK, (20, 60, 200, 20))
        speed_ratio = self.player.speed / self.player.max_speed
        bar_color = GREEN if not self.speed_boost else YELLOW
        pygame.draw.rect(screen, bar_color, (20, 60, int(200 * speed_ratio), 20))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 100))

        # Distance
        distance_text = self.font.render(f"Distance: {int(self.distance)} m", True, WHITE)
        screen.blit(distance_text, (20, 140))

        # Time
        time_text = self.font.render(f"Time: {int(self.game_time)} s", True, WHITE)
        screen.blit(time_text, (20, 180))

        # Power-up indicators
        if self.speed_boost:
            boost_text = self.font.render(f"Speed Boost: {self.speed_boost_timer//FPS + 1}s", True, YELLOW)
            screen.blit(boost_text, (SCREEN_WIDTH - 250, 20))

        if self.invincible:
            invincible_text = self.font.render(f"Invincible: {self.invincible_timer//FPS + 1}s", True, (0, 255, 255))
            screen.blit(invincible_text, (SCREEN_WIDTH - 250, 60))

    def draw_game_over(self, screen):
        self.draw_background(screen)
        self.draw_road(screen)

        # Draw game over text
        game_over_text = self.big_font.render("GAME OVER", True, RED)
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//3))

        # Draw score
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))

        # Draw distance
        distance_text = self.font.render(f"Distance: {int(self.distance)} m", True, WHITE)
        screen.blit(distance_text, (SCREEN_WIDTH//2 - distance_text.get_width()//2, SCREEN_HEIGHT//2 + 40))

        # Draw time
        time_text = self.font.render(f"Time: {int(self.game_time)} s", True, WHITE)
        screen.blit(time_text, (SCREEN_WIDTH//2 - time_text.get_width()//2, SCREEN_HEIGHT//2 + 80))

        # Draw restart instruction
        if int(pygame.time.get_ticks() / 500) % 2 == 0:  # Blinking effect
            restart_text = self.font.render("Press ENTER to Continue", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT*2//3))

    def draw(self, screen):
        if self.state == MENU:
            self.draw_menu(screen)
        elif self.state == PLAYING:
            self.draw_playing(screen)
        elif self.state == GAME_OVER:
            self.draw_game_over(screen)

def main():
    # Set up the display
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Racing Game")
    clock = pygame.time.Clock()

    game = Game()
    running = True

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Get keyboard state
        keys = pygame.key.get_pressed()

        # Update game state
        if not game.update(keys):
            pass  # Game over is handled within the game class

        # Draw everything
        game.draw(screen)

        # Update display
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()