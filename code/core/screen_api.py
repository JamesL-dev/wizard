import pygame
import os
import math
import random

from core.game_state import GameStateController

class ScreenAPI:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption("Wizard Pinball Marquee")

        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.YELLOW = (241, 179, 0)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)

        # Get absolute path to the pinball/ root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # Construct path to the logo
        logo_path = os.path.join(project_root, "assets", "images", "UI_Main_full_color_stacked_RGB.png")
        # logo_path = "UI_Main_full_color_stacked_RGB.png"

        if not os.path.exists(logo_path):
            raise FileNotFoundError(f"Logo file not found: {logo_path}")
        self.logo = pygame.image.load(logo_path)
        self.logo = pygame.transform.scale(self.logo, (300, 300))

        self.font = pygame.font.Font(None, 100)
        self.stats_font = pygame.font.Font(None, 80)
        self.press_start_font = pygame.font.Font(None, 60)

        self.fixed_stars = [(random.randint(50, self.WIDTH - 50), random.randint(100, self.HEIGHT - 100)) for _ in range(15)]
        self.flashing_orbs = [(random.randint(100, self.WIDTH - 100), random.randint(150, self.HEIGHT - 150), random.randint(30, 60)) for _ in range(5)]


        self.high_scores = [("Gary", 10000), ("Tim", 8500), ("James", 7200)]

    def update(self, state: str, score: int = 0, ball: int = 0):
        if state == "attract":
            if (pygame.time.get_ticks() // 5000) % 2 == 0:
                self.draw_attract()
            else:
                self.draw_high_scores()
        elif state == "launch":
            self.draw_launch(ball)
        elif state == "play":
            self.draw_play(score)
        elif state == "game_over":
            self.draw_game_over(score)
        elif state == "high_scores":
            self.draw_high_scores()

    def draw_attract(self):
        self.screen.fill(self.BLACK)
        for star in self.fixed_stars:
            pygame.draw.circle(self.screen, self.WHITE, star, 2)
        for orb in self.flashing_orbs:
            alpha = (math.sin(pygame.time.get_ticks() / 1000) + 1) / 2
            color = (int(self.YELLOW[0] * alpha), int(self.YELLOW[1] * alpha), int(self.YELLOW[2] * alpha))
            pygame.draw.circle(self.screen, color, (orb[0], orb[1]), orb[2])

        title = self.font.render("Wizard Pinball", True, self.YELLOW)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, 80)))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT // 2))

        if pygame.time.get_ticks() % 1000 < 500:
            press_start_text = self.press_start_font.render("PRESS START", True, self.WHITE)
            self.screen.blit(press_start_text, press_start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50)))

        pygame.display.flip()

    def draw_launch(self, ball: int = 0):
        self.screen.fill(self.BLACK)
        launch_text = self.font.render(f"Ball: {ball}", True, self.YELLOW)
        self.screen.blit(launch_text, launch_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
        pygame.display.flip()

    def draw_play(self, score):
        self.screen.fill(self.BLACK)
        play_text = self.font.render("PLAYING", True, self.YELLOW)
        score_text = self.font.render(f"Score: {score}", True, self.WHITE)
        self.screen.blit(play_text, play_text.get_rect(center=(self.WIDTH // 2, 150)))
        self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
        pygame.display.flip()

    def draw_game_over(self, score):
        self.screen.fill(self.BLACK)
        over_text = self.font.render("GAME OVER", True, self.RED)
        score_text = self.font.render(f"Final Score: {score}", True, self.WHITE)
        self.screen.blit(over_text, over_text.get_rect(center=(self.WIDTH // 2, 150)))
        self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
        pygame.display.flip()

    def draw_high_scores(self):
        self.screen.fill(self.BLACK)
        stats_text = self.stats_font.render("High Scores", True, self.WHITE)
        self.screen.blit(stats_text, stats_text.get_rect(center=(self.WIDTH // 2, 150)))
        for i, (name, score) in enumerate(self.high_scores):
            entry = self.stats_font.render(f"{i+1}. {name} - {score}", True, self.WHITE)
            self.screen.blit(entry, (self.WIDTH // 2 - 150, 250 + i * 80))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))

        if pygame.time.get_ticks() % 1000 < 500:
            press_start_text = self.press_start_font.render("PRESS START", True, self.WHITE)
            self.screen.blit(press_start_text, press_start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50)))

        pygame.display.flip()

if __name__ == "__main__":
    import time

    screen_api = ScreenAPI()
    demo_states = ["attract", "launch", "play", "game_over", "high_scores"]
    score = 1000
    current = 0

    running = True
    last_switch = time.time()
    switch_delay = 3

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False

        now = time.time()
        if now - last_switch > switch_delay:
            current = (current + 1) % len(demo_states)
            last_switch = now
            if demo_states[current] == "play":
                score += 100

        screen_api.update(demo_states[current], score if demo_states[current] == "play" or demo_states[current] == "game_over" else 0)
        pygame.time.Clock().tick(30)

    pygame.quit()
