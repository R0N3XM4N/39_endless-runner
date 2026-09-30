import pygame

class Player:
    def __init__(self, x, ground_y):
        self.x = x
        self.ground_y = ground_y
        self.width = 30
        self.height = 30
        self.y = ground_y - self.height
        self.vy = 0
        self.gravity = 0.6
        self.jump_velocity = -11

    def jump(self):
        if self.y >= self.ground_y - self.height:
            self.vy = self.jump_velocity

    def update(self):
        self.vy += self.gravity
        self.y += self.vy
        if self.y > self.ground_y - self.height:
            self.y = self.ground_y - self.height
            self.vy = 0

    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
