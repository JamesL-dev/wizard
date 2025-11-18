import pygame
import os
import math
import random
from PIL import Image, ImageOps

from core.game_state import GameStateController

class ScreenAPI:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = pygame.display.Info().current_w, pygame.display.Info().current_h
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.FULLSCREEN)
        # self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.NOFRAME)
        pygame.display.set_caption("Wizard Pinball")
        
        # Hide the mouse cursor
        pygame.mouse.set_visible(False)

        # Initialize colors
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
        
        # Attract mode cycle
        self.attract_index = 0
        self.last_attract_switch = pygame.time.get_ticks()
        self.attract_delay = 2000  # 5 seconds per image
    
        # Load attract images
        self.attract_images = []
        image_dir = os.path.join(project_root, "assets", "images", "attract")
        # print(f"[ScreenAPI] Loading attract images from {image_dir}")
        if os.path.exists(image_dir):
            for fname in sorted(os.listdir(image_dir)):
                # print(f"[ScreenAPI] Found file: {fname}")
                if fname.lower().endswith((".png", ".jpg", ".jpeg")):
                    path = os.path.join(image_dir, fname)
                    try:
                        pil_img = Image.open(path)
                        pil_img = ImageOps.exif_transpose(pil_img)  # Handle EXIF orientation
                        
                        pil_img = pil_img.convert("RGB")  # Ensure RGB format
                        mode = "RGB"
                        size = pil_img.size
                        data = pil_img.tobytes()
                        
                        img_surface = pygame.image.fromstring(data, size, mode)
                        # img = pygame.image.load(path).convert()
                        # img = pygame.transform.scale(img, (self.WIDTH, self.HEIGHT))
                        self.attract_images.append(img_surface)
                    except Exception as e:
                        print(f"Failed to load {fname}: {e}")

        # Construct dynamic attract cycle
        self.attract_cycle = []
        self.attract_cycle.append("main")  # Start with main attract mode
        for i in range(len(self.attract_images)):
            if i % 2 == 0:
                self.attract_cycle.append("main")
                self.attract_cycle.append(i)
            else:
                self.attract_cycle.append("high_scores")
                self.attract_cycle.append(i)
            # self.attract_cycle.append("high_scores")
        # Ensure we wrap around nicely
        # if len(self.attract_images) % 2 == 0:
        #     self.attract_cycle.append("main")
        
        print(f"[ScreenAPI] Attract cycle: {self.attract_cycle}")


        # self.high_scores = [("Gary", 10000), ("Tim", 8500), ("James", 7200)]

    def update(self, state: str, score: int = 0, ball: int = 0, ball_launch: int = 0, high_scores: list = [], last_score: int = 0):
        if state == "attract":
            now = pygame.time.get_ticks()
            if now - self.last_attract_switch > self.attract_delay:
                print(f"[ScreenAPI] Time since last switch: {now - self.last_attract_switch} ms")
                self.attract_index = (self.attract_index + 1) % len(self.attract_cycle)
                self.last_attract_switch = now
                
            mode = self.attract_cycle[self.attract_index]
            # print(f"[ScreenAPI] Attract mode: {mode} (index {self.attract_index})")
            if mode == "main":
                self.draw_attract(last_score=last_score)
            elif mode == "high_scores":
                self.draw_high_scores(high_scores=high_scores)
            elif isinstance(mode, int):  # It's an image index
                if mode < len(self.attract_images):
                    img = self.attract_images[mode]
                    img_rect = img.get_rect()

                    # Get aspect ratios
                    screen_ratio = self.WIDTH / self.HEIGHT
                    img_ratio = img_rect.width / img_rect.height

                    # Scale image to fit screen
                    if img_ratio > screen_ratio:
                        # Image is wider relative to screen
                        scale_width = self.WIDTH
                        scale_height = int(self.WIDTH / img_ratio)
                    else:
                        # Image is taller relative to screen
                        scale_height = self.HEIGHT
                        scale_width = int(self.HEIGHT * img_ratio)

                    # Scale and center
                    scaled_img = pygame.transform.smoothscale(img, (scale_width, scale_height))
                    x = (self.WIDTH - scale_width) // 2
                    y = (self.HEIGHT - scale_height) // 2
                    self.screen.fill(self.BLACK)  # Optional: black bars around the image
                    self.screen.blit(scaled_img, (x, y))
                    # Flashing "PRESS START"
                    if pygame.time.get_ticks() % 1000 < 500:
                        press_start_text = self.press_start_font.render("PRESS START", True, self.YELLOW)
                        self.screen.blit(press_start_text, press_start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50)))

                    
                    pygame.display.flip()


            # if (pygame.time.get_ticks() // 5000) % 2 == 0:
            #     self.draw_attract(last_score=last_score)
            # else:
            #     self.draw_high_scores(high_scores=high_scores)
        # elif state == "launch":
        #     self.draw_launch(ball)
        elif state == "play":
            if ball_launch:
                self.draw_play(score, ball)
            else:
                self.draw_launch(ball)
        elif state == "game_over":
            self.draw_game_over(last_score)
        # elif state == "high_scores":
        #     self.draw_high_scores()

    def draw_attract(self, last_score: int = 0):
        self.screen.fill(self.BLACK)

        # Draw stars and flashing orbs
        for star in self.fixed_stars:
            pygame.draw.circle(self.screen, self.WHITE, star, 2)
        for orb in self.flashing_orbs:
            alpha = (math.sin(pygame.time.get_ticks() / 1000) + 1) / 2
            color = (
                int(self.YELLOW[0] * alpha),
                int(self.YELLOW[1] * alpha),
                int(self.YELLOW[2] * alpha)
            )
            pygame.draw.circle(self.screen, color, (orb[0], orb[1]), orb[2])

        # Game title
        title = self.font.render("Wizard Pinball", True, self.YELLOW)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, 80)))

        # Last score display
        if last_score > 0:
            score_font = pygame.font.Font(None, 48)
            score_text = score_font.render(f"Last Score: {last_score}", True, self.WHITE)
            self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, 140)))

        # Logo
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT // 2))

        # Flashing "PRESS START"
        if pygame.time.get_ticks() % 1000 < 500:
            press_start_text = self.press_start_font.render("PRESS START", True, self.YELLOW)
            self.screen.blit(press_start_text, press_start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50)))

        pygame.display.flip()


    def draw_launch(self, ball: int = 0):
        self.screen.fill(self.BLACK)

        # Centered ball launch info
        launch_text = self.font.render(f"Ball: {ball+1}", True, self.YELLOW)
        self.screen.blit(launch_text, launch_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))

        # Draw logo
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))

        # Flashing "LAUNCH BALL" text above the center ball count
        blink_interval = 500  # ms
        ticks = pygame.time.get_ticks()
        if (ticks // blink_interval) % 2 == 0:
            launch_font = pygame.font.Font(None, 96)
            launch_msg = launch_font.render("LAUNCH BALL", True, self.YELLOW)
            launch_msg_rect = launch_msg.get_rect(
                center=(self.WIDTH // 2, self.HEIGHT // 2 - 80)
            )
            self.screen.blit(launch_msg, launch_msg_rect)

        # Draw Vandal Gold ball tracker box in top-right corner
        # box_width, box_height = 140, 60
        # margin = 20
        # box_rect = pygame.Rect(self.WIDTH - box_width - margin, margin, box_width, box_height)
        # pygame.draw.rect(self.screen, self.YELLOW, box_rect, border_radius=10)

        # # Render ball number text in black for contrast
        # ball_font = pygame.font.Font(None, 36)
        # ball_text = ball_font.render(f"Ball {ball}", True, self.BLACK)
        # text_rect = ball_text.get_rect(center=box_rect.center)
        # self.screen.blit(ball_text, text_rect)

        pygame.display.flip()


    # def draw_launch(self, ball: int = 0):
    #     self.screen.fill(self.BLACK)
    #     launch_text = self.font.render(f"Ball: {ball}", True, self.YELLOW)
    #     self.screen.blit(launch_text, launch_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
    #     self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
    #     pygame.display.flip()

    def draw_play(self, score: int, ball: int):
        self.screen.fill(self.BLACK)

        # Draw centered score
        score_text = self.font.render(f"Score: {score}", True, self.WHITE)
        # score_text = self.font.render(f"Score: {score}", True, self.WHITE)
        # self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, 80)))
        self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))

        # Draw Vandal Gold ball tracker box in top-right corner
        box_width, box_height = 140, 60
        margin = 20
        box_rect = pygame.Rect(self.WIDTH - box_width - margin, margin, box_width, box_height)
        pygame.draw.rect(self.screen, self.YELLOW, box_rect, border_radius=10)

        # Ball number text in black for contrast
        ball_font = pygame.font.Font(None, 36)
        ball_text = ball_font.render(f"Ball {ball+1}", True, self.BLACK)
        text_rect = ball_text.get_rect(center=box_rect.center)
        self.screen.blit(ball_text, text_rect)
        
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))

        pygame.display.flip()


    # def draw_play(self, score):
    #     self.screen.fill(self.BLACK)
    #     play_text = self.font.render("PLAYING", True, self.YELLOW)
    #     score_text = self.font.render(f"Score: {score}", True, self.WHITE)
    #     self.screen.blit(play_text, play_text.get_rect(center=(self.WIDTH // 2, 150)))
    #     self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
    #     self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
    #     pygame.display.flip()

    def draw_game_over(self, score):
        self.screen.fill(self.BLACK)
        over_text = self.font.render("GAME OVER", True, self.RED)
        score_text = self.font.render(f"Final Score: {score}", True, self.WHITE)
        self.screen.blit(over_text, over_text.get_rect(center=(self.WIDTH // 2, 150)))
        self.screen.blit(score_text, score_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))
        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))
        pygame.display.flip()

    def draw_high_scores(self, high_scores: list):
        self.screen.fill(self.BLACK)
        stats_text = self.stats_font.render("High Scores", True, self.WHITE)
        self.screen.blit(stats_text, stats_text.get_rect(center=(self.WIDTH // 2, 150)))
        for i, entry in enumerate(high_scores):
            score_text = self.stats_font.render(
                f"{i+1}. {entry['name']} - {entry['score']}", True, self.WHITE
            )
            self.screen.blit(score_text, (self.WIDTH // 2 - 200, 250 + i * 80))

        self.screen.blit(self.logo, (self.WIDTH // 2 - 150, self.HEIGHT - 400))

        if pygame.time.get_ticks() % 1000 < 500:
            press_start_text = self.press_start_font.render("PRESS START", True, self.YELLOW)
            self.screen.blit(press_start_text, press_start_text.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2)))

        pygame.display.flip()
        
        
    def get_player_name(self, score: int) -> str:
        name = ""
        prompt_font = pygame.font.Font(None, 64)
        entry_font = pygame.font.Font(None, 100)
        max_chars = 3

        while True:
            self.screen.fill(self.BLACK)

            prompt = prompt_font.render(f"New High Score: {score}", True, self.YELLOW)
            prompt_rect = prompt.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 80))
            self.screen.blit(prompt, prompt_rect)

            entry = entry_font.render(name, True, self.WHITE)
            entry_rect = entry.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(entry, entry_rect)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "AAA"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and len(name) > 0:
                        return name
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    elif len(name) < max_chars and event.unicode.isalpha():
                        name += event.unicode.upper()


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
