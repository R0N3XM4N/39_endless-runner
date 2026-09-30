import pygame

class Obstacle:
    def __init__(self, x, ground_y, speed):
        self.x = x
        self.ground_y = ground_y
        self.width = 30
        self.height = 30
        self.speed = speed
        self.scored = False

    def move(self):
        self.x -= self.speed

    def rect(self):
        return pygame.Rect(int(self.x), self.ground_y - self.height, self.width, self.height)

    def off_screen(self):
        return self.x + self.width < 0
