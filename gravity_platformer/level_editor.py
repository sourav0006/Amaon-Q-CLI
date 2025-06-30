import pygame
import sys
import json
import os
from pygame.locals import *

# Initialize pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
GRAY = (128, 128, 128)

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Gravity Platformer - Level Editor")
clock = pygame.time.Clock()

class LevelEditor:
    def __init__(self):
        self.platforms = []
        self.planets = []
        self.stars = []
        self.current_tool = "platform"  # platform, planet, star, select, delete
        self.selected_object = None
        self.dragging = False
        self.start_pos = None
        self.grid_size = 20
        self.show_grid = True
        self.current_level = "level1"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == KEYDOWN:
                if event.key == K_1:
                    self.current_tool = "platform"
                elif event.key == K_2:
                    self.current_tool = "planet"
                elif event.key == K_3:
                    self.current_tool = "star"
                elif event.key == K_4:
                    self.current_tool = "select"
                elif event.key == K_5:
                    self.current_tool = "delete"
                elif event.key == K_g:
                    self.show_grid = not self.show_grid
                elif event.key == K_s:
                    self.save_level()
                elif event.key == K_l:
                    self.load_level()
                elif event.key == K_n:
                    self.new_level()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()

                    if self.current_tool == "platform":
                        self.start_pos = self.snap_to_grid(mouse_pos)
                        self.dragging = True
                    elif self.current_tool == "planet":
                        pos = self.snap_to_grid(mouse_pos)
                        self.planets.append({"x": pos[0], "y": pos[1], "radius": 30})
                    elif self.current_tool == "star":
                        pos = self.snap_to_grid(mouse_pos)
                        self.stars.append({"x": pos[0], "y": pos[1]})
                    elif self.current_tool == "select":
                        self.selected_object = self.get_object_at_pos(mouse_pos)
                        if self.selected_object:
                            self.dragging = True
                    elif self.current_tool == "delete":
                        obj = self.get_object_at_pos(mouse_pos)
                        if obj:
                            if "width" in obj:  # Platform
                                self.platforms.remove(obj)
                            elif "radius" in obj:  # Planet
                                self.planets.remove(obj)
                            else:  # Star
                                self.stars.remove(obj)

            if event.type == MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    if self.current_tool == "platform" and self.dragging:
                        end_pos = self.snap_to_grid(pygame.mouse.get_pos())
                        width = abs(end_pos[0] - self.start_pos[0])
                        height = abs(end_pos[1] - self.start_pos[1])

                        if width > 0 and height > 0:
                            x = min(self.start_pos[0], end_pos[0])
                            y = min(self.start_pos[1], end_pos[1])
                            self.platforms.append({"x": x, "y": y, "width": width, "height": height})

                    self.dragging = False

            if event.type == MOUSEMOTION and self.dragging:
                mouse_pos = self.snap_to_grid(pygame.mouse.get_pos())

                if self.current_tool == "select" and self.selected_object:
                    if "width" in self.selected_object:  # Platform
                        self.selected_object["x"] = mouse_pos[0]
                        self.selected_object["y"] = mouse_pos[1]
                    elif "radius" in self.selected_object:  # Planet
                        self.selected_object["x"] = mouse_pos[0]
                        self.selected_object["y"] = mouse_pos[1]
                    else:  # Star
                        self.selected_object["x"] = mouse_pos[0]
                        self.selected_object["y"] = mouse_pos[1]

    def snap_to_grid(self, pos):
        if self.show_grid:
            return (
                round(pos[0] / self.grid_size) * self.grid_size,
                round(pos[1] / self.grid_size) * self.grid_size
            )
        return pos

    def get_object_at_pos(self, pos):
        # Check platforms
        for platform in self.platforms:
            if (platform["x"] <= pos[0] <= platform["x"] + platform["width"] and
                platform["y"] <= pos[1] <= platform["y"] + platform["height"]):
                return platform

        # Check planets
        for planet in self.planets:
            dx = pos[0] - planet["x"]
            dy = pos[1] - planet["y"]
            if (dx*dx + dy*dy) <= planet["radius"]*planet["radius"]:
                return planet

        # Check stars
        for star in self.stars:
            if abs(pos[0] - star["x"]) < 20 and abs(pos[1] - star["y"]) < 20:
                return star

        return None

    def save_level(self):
        level_data = {
            "platforms": self.platforms,
            "planets": self.planets,
            "stars": self.stars
        }

        os.makedirs("levels", exist_ok=True)
        with open(f"levels/{self.current_level}.json", "w") as f:
            json.dump(level_data, f)
        print(f"Level saved as {self.current_level}.json")

    def load_level(self):
        try:
            with open(f"levels/{self.current_level}.json", "r") as f:
                level_data = json.load(f)
                self.platforms = level_data.get("platforms", [])
                self.planets = level_data.get("planets", [])
                self.stars = level_data.get("stars", [])
            print(f"Level {self.current_level}.json loaded")
        except FileNotFoundError:
            print(f"Level {self.current_level}.json not found")

    def new_level(self):
        self.platforms = []
        self.planets = []
        self.stars = []
        print("New level created")

    def draw(self):
        screen.fill(BLACK)

        # Draw grid
        if self.show_grid:
            for x in range(0, SCREEN_WIDTH, self.grid_size):
                pygame.draw.line(screen, GRAY, (x, 0), (x, SCREEN_HEIGHT), 1)
            for y in range(0, SCREEN_HEIGHT, self.grid_size):
                pygame.draw.line(screen, GRAY, (0, y), (SCREEN_WIDTH, y), 1)

        # Draw platforms
        for platform in self.platforms:
            color = GREEN if platform != self.selected_object else WHITE
            pygame.draw.rect(screen, color, (platform["x"], platform["y"], platform["width"], platform["height"]))

        # Draw planets
        for planet in self.planets:
            color = YELLOW if planet != self.selected_object else WHITE
            pygame.draw.circle(screen, color, (planet["x"], planet["y"]), planet["radius"])

        # Draw stars
        for star in self.stars:
            color = PURPLE if star != self.selected_object else WHITE
            pygame.draw.polygon(screen, color, [
                (star["x"], star["y"] - 10),
                (star["x"] + 3, star["y"] - 3),
                (star["x"] + 10, star["y"] - 3),
                (star["x"] + 4, star["y"] + 2),
                (star["x"] + 6, star["y"] + 10),
                (star["x"], star["y"] + 5),
                (star["x"] - 6, star["y"] + 10),
                (star["x"] - 4, star["y"] + 2),
                (star["x"] - 10, star["y"] - 3),
                (star["x"] - 3, star["y"] - 3)
            ])

        # Draw current tool indicator
        font = pygame.font.SysFont(None, 24)
        tool_text = font.render(f"Tool: {self.current_tool}", True, WHITE)
        screen.blit(tool_text, (10, 10))

        # Draw help text
        help_text = font.render("1-5: Change tools | G: Toggle grid | S: Save | L: Load | N: New", True, WHITE)
        screen.blit(help_text, (10, SCREEN_HEIGHT - 30))

        # Draw preview for platform creation
        if self.current_tool == "platform" and self.dragging:
            end_pos = self.snap_to_grid(pygame.mouse.get_pos())
            width = end_pos[0] - self.start_pos[0]
            height = end_pos[1] - self.start_pos[1]
            pygame.draw.rect(screen, WHITE, (
                self.start_pos[0],
                self.start_pos[1],
                width,
                height
            ), 1)

        pygame.display.flip()

# Main function
def main():
    editor = LevelEditor()

    # Main loop
    while True:
        editor.handle_events()
        editor.draw()
        clock.tick(FPS)

if __name__ == "__main__":
    main()