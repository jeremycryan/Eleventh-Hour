import pygame
from primitives import Pose

class Battery:

    def __init__(self, capacity, position=(0, 0)):
        self.surf = pygame.image.load("images/battery.png")
        self.glow = pygame.image.load("images/glow.png")
        self.position = Pose(position)

    def update(self, dt, events):
        pass

    def draw(self, screen, offset=(0, 0)):

        x = offset[0] - self.glow.get_width()//2 + self.position.x
        y = offset[1] - self.glow.get_height()//2 + self.position.y
        screen.blit(self.glow, (x, y), special_flags=pygame.BLEND_ADD)