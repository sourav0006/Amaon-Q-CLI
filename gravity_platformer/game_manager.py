import pygame
import sys
import json
import os
from pygame.locals import *

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2
LEVEL_COMPLETE = 3

class GameManager:
    def __init__(self, screen, clock):
        self.screen = screen
        self.clock = clock
        self.state = MENU
        self.current_level = 1
        self.max_level = self.count_levels()
        self.score = 0
        self.lives = 3

        # Load fonts
        self.title_font = pygame.font.SysFont(None, 64)
        self.menu_font = pygame.font.SysFont(None, 36)
        self.hud_font = pygame.font.SysFont(None, 24)

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.BLUE = (0, 0, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.YELLOW = (255, 255, 0)

    def count_levels(self):
        count = 0
        while os.path.exists(f"levels/level{count+1}.json"):
            count += 1
        return max(1, count)  # At least one level

    def load_level(self, level_num):
        try:
            with open(f"levels/level{level_num}.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            # Create a default level if file doesn't exist
            return {
                "platforms": [
                    {"x": 0, "y": 560, "width": 800, "height": 40},
                    {"x": 100, "y": 400, "width": 200, "height": 20},
                    {"x": 500, "y": 300, "width": 200, "height": 20}
                ],
                "planets": [
                    {"x": 400, "y": 300, "radius": 50}
                ],
                "stars": [
                    {"x": 100, "y": 100},
                    {"x": 250, "y": 100},
                    {"x": 400, "y": 100},
                    {"x": 550, "y": 100},
                    {"x": 700, "y": 100}
                ]
            }

    def draw_menu(self):
        self.screen.fill(self.BLACK)

        # Draw title
        title = self.title_font.render("GRAVITY PLATFORMER", True, self.YELLOW)
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 100))
        self.screen.blit(title, title_rect)

        # Draw menu options
        start_text = self.menu_font.render("Press SPACE to Start", True, self.WHITE)
        start_rect = start_text.get_rect(center=(self.screen.get_width() // 2, 250))
        self.screen.blit(start_text, start_rect)

        editor_text = self.menu_font.render("Press E for Level Editor", True, self.WHITE)
        editor_rect = editor_text.get_rect(center=(self.screen.get_width() // 2, 300))
        self.screen.blit(editor_text, editor_rect)

        quit_text = self.menu_font.render("Press Q to Quit", True, self.WHITE)
        quit_rect = quit_text.get_rect(center=(self.screen.get_width() // 2, 350))
        self.screen.blit(quit_text, quit_rect)

        # Draw controls
        controls_title = self.menu_font.render("Controls:", True, self.GREEN)
        self.screen.blit(controls_title, (50, 420))

        controls = [
            "Arrow Keys: Move",
            "Space: Jump",
            "G: Toggle Gravity Center"
        ]

        for i, control in enumerate(controls):
            control_text = self.hud_font.render(control, True, self.WHITE)
            self.screen.blit(control_text, (70, 460 + i * 30))

        pygame.display.flip()

    def draw_hud(self):
        # Draw score
        score_text = self.hud_font.render(f"Score: {self.score}", True, self.WHITE)
        self.screen.blit(score_text, (10, 10))

        # Draw lives
        lives_text = self.hud_font.render(f"Lives: {self.lives}", True, self.WHITE)
        self.screen.blit(lives_text, (10, 40))

        # Draw level
        level_text = self.hud_font.render(f"Level: {self.current_level}/{self.max_level}", True, self.WHITE)
        self.screen.blit(level_text, (10, 70))

    def draw_game_over(self):
        self.screen.fill(self.BLACK)

        # Draw game over text
        game_over = self.title_font.render("GAME OVER", True, self.RED)
        game_over_rect = game_over.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(game_over, game_over_rect)

        # Draw score
        score_text = self.menu_font.render(f"Final Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, 300))
        self.screen.blit(score_text, score_rect)

        # Draw restart option
        restart_text = self.menu_font.render("Press R to Restart", True, self.WHITE)
        restart_rect = restart_text.get_rect(center=(self.screen.get_width() // 2, 350))
        self.screen.blit(restart_text, restart_rect)

        # Draw menu option
        menu_text = self.menu_font.render("Press M for Menu", True, self.WHITE)
        menu_rect = menu_text.get_rect(center=(self.screen.get_width() // 2, 400))
        self.screen.blit(menu_text, menu_rect)

        pygame.display.flip()

    def draw_level_complete(self):
        self.screen.fill(self.BLACK)

        # Draw level complete text
        complete_text = self.title_font.render("LEVEL COMPLETE!", True, self.GREEN)
        complete_rect = complete_text.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(complete_text, complete_rect)

        # Draw score
        score_text = self.menu_font.render(f"Score: {self.score}", True, self.WHITE)
        score_rect = score_text.get_rect(center=(self.screen.get_width() // 2, 300))
        self.screen.blit(score_text, score_rect)

        # Draw next level option
        if self.current_level < self.max_level:
            next_text = self.menu_font.render("Press N for Next Level", True, self.WHITE)
            next_rect = next_text.get_rect(center=(self.screen.get_width() // 2, 350))
            self.screen.blit(next_text, next_rect)
        else:
            next_text = self.menu_font.render("You completed all levels!", True, self.YELLOW)
            next_rect = next_text.get_rect(center=(self.screen.get_width() // 2, 350))
            self.screen.blit(next_text, next_rect)

        # Draw menu option
        menu_text = self.menu_font.render("Press M for Menu", True, self.WHITE)
        menu_rect = menu_text.get_rect(center=(self.screen.get_width() // 2, 400))
        self.screen.blit(menu_text, menu_rect)

        pygame.display.flip()

    def handle_menu_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    self.state = PLAYING
                    return True  # Signal to start the game
                elif event.key == K_e:
                    # Launch level editor
                    import level_editor
                    level_editor.main()
                elif event.key == K_q:
                    pygame.quit()
                    sys.exit()

        return False  # Continue in menu

    def handle_game_over_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_r:
                    self.lives = 3
                    self.score = 0
                    self.current_level = 1
                    self.state = PLAYING
                    return True  # Signal to restart the game
                elif event.key == K_m:
                    self.state = MENU

        return False  # Stay in game over screen

    def handle_level_complete_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_n and self.current_level < self.max_level:
                    self.current_level += 1
                    self.state = PLAYING
                    return True  # Signal to load next level
                elif event.key == K_m:
                    self.state = MENU

        return False  # Stay in level complete screen

    def run(self):
        while True:
            if self.state == MENU:
                self.draw_menu()
                if self.handle_menu_events():
                    return "start_game", self.current_level

            elif self.state == GAME_OVER:
                self.draw_game_over()
                if self.handle_game_over_events():
                    return "restart_game", self.current_level

            elif self.state == LEVEL_COMPLETE:
                self.draw_level_complete()
                if self.handle_level_complete_events():
                    return "next_level", self.current_level

            self.clock.tick(60)