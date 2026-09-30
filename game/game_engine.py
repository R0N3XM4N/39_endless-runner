import pygame
import math
import struct
import io
from .player import Player
from .obstacle import Obstacle

WHITE = (255, 255, 255)
BROWN = (120, 80, 40)
DARK_GREEN = (30, 100, 30)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

DIFFICULTIES = {
    'easy':   {'speed': 4,  'spawn_interval': 90},
    'medium': {'speed': 6,  'spawn_interval': 70},
    'hard':   {'speed': 9,  'spawn_interval': 50},
}

class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ground_y = height - 40

        self.player = Player(80, self.ground_y)

        self.speed = 6
        self.speed_increase_per_frame = 0.003
        self.speed_cap = self.player.width

        self.spawn_interval = 70
        self._spawn_timer = 0
        self.obstacles = []

        self.distance = 0
        self.score = 0
        self.font = pygame.font.SysFont("Arial", 30)
        self.big_font = pygame.font.SysFont("Arial", 48)

        self.game_over = False
        self.state = 'playing'

        self.sounds = self._make_sounds()

    def _make_sounds(self):
        sample_rate = 44100

        def tone(freq, dur, vol=0.2):
            n = int(sample_rate * dur)
            raw = b''
            for i in range(n):
                val = int(vol * 32767 * math.sin(2 * math.pi * freq * i / sample_rate))
                raw += struct.pack('<h', max(-32768, min(32767, val)))
            header = struct.pack('<4sI4s4sIHHIIHH',
                b'RIFF', 36 + len(raw), b'WAVE', b'fmt ', 16, 1, 1,
                sample_rate, sample_rate * 2, 2, 16)
            wav = header + b'data' + struct.pack('<I', len(raw)) + raw
            return pygame.mixer.Sound(io.BytesIO(wav))

        return {
            'jump': tone(440, 0.1),
            'score': tone(660, 0.12),
            'gameover': tone(220, 0.4),
        }

    def _reset(self, diff='medium'):
        d = DIFFICULTIES[diff]
        self.speed = d['speed']
        self.speed_increase_per_frame = 0.003
        self.speed_cap = self.player.width
        self.spawn_interval = d['spawn_interval']
        self._spawn_timer = 0
        self.obstacles = []
        self.player = Player(80, self.ground_y)
        self.distance = 0
        self.score = 0
        self.game_over = False
        self.state = 'playing'

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.state == 'playing':
                if event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w):
                    self.player.jump()
                    self.sounds['jump'].play()
            elif self.state == 'game_over':
                self.state = 'menu'
            elif self.state == 'menu':
                if event.key == pygame.K_e:
                    self._reset('easy')
                elif event.key == pygame.K_m:
                    self._reset('medium')
                elif event.key == pygame.K_h:
                    self._reset('hard')
                elif event.key == pygame.K_q:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_input(self):
        pass

    def update(self):
        if self.state != 'playing':
            return

        self.speed += self.speed_increase_per_frame
        self.speed = min(self.speed, self.speed_cap)

        self.player.update()

        self._spawn_timer += 1
        if self._spawn_timer >= self.spawn_interval:
            self._spawn_timer = 0
            self.obstacles.append(Obstacle(self.width, self.ground_y, self.speed))

        for obstacle in self.obstacles:
            obstacle.move()
            obstacle.speed = self.speed

        for obstacle in self.obstacles:
            if obstacle.rect().colliderect(self.player.rect()):
                self.game_over = True
                self.state = 'game_over'
                self.sounds['gameover'].play()
                return

        for obstacle in self.obstacles:
            if not obstacle.scored and obstacle.x + obstacle.width < self.player.x:
                obstacle.scored = True
                self.score += 1
                self.sounds['score'].play()

        self.obstacles = [o for o in self.obstacles if not o.off_screen()]
        self.distance += self.speed

    def render(self, screen):
        pygame.draw.line(screen, BROWN, (0, self.ground_y), (self.width, self.ground_y), 4)
        pygame.draw.rect(screen, WHITE, self.player.rect())
        for obstacle in self.obstacles:
            pygame.draw.rect(screen, DARK_GREEN, obstacle.rect())

        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        if self.state == 'game_over':
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            go_text = self.big_font.render("Game Over!", True, RED)
            sc_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            cont_text = self.font.render("Press any key", True, WHITE)
            screen.blit(go_text, (self.width // 2 - go_text.get_width() // 2, self.height // 2 - 60))
            screen.blit(sc_text, (self.width // 2 - sc_text.get_width() // 2, self.height // 2))
            screen.blit(cont_text, (self.width // 2 - cont_text.get_width() // 2, self.height // 2 + 50))

        elif self.state == 'menu':
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 160))
            screen.blit(overlay, (0, 0))
            title = self.big_font.render("Play Again?", True, WHITE)
            easy = self.font.render("E - Easy", True, WHITE)
            med = self.font.render("M - Medium", True, WHITE)
            hard = self.font.render("H - Hard", True, WHITE)
            quit_t = self.font.render("Q - Quit", True, WHITE)
            for i, t in enumerate([title, easy, med, hard, quit_t]):
                screen.blit(t, (self.width // 2 - t.get_width() // 2, self.height // 2 - 60 + i * 40))
