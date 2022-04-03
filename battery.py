import pygame
from primitives import Pose
import random
import math

class Battery:

    def __init__(self, game, capacity, position=(0, 0)):
        self.surf = pygame.image.load("images/battery.png")
        self.surf.set_colorkey((0, 0, 0))
        self.glow = pygame.image.load("images/glow.png")
        self.position = Pose(position)
        self.game = game
        self.capacity = capacity

        vm = random.random()**2 * 1500
        va = random.random() * 2*math.pi
        self.velocity = Pose((math.sin(va) * vm, math.cos(va)*vm))
        self.seek_speed = 100


    def update(self, dt, events):
        diff = self.game.player.position - self.position
        self.position += self.velocity*dt
        self.velocity *= 0.005**dt
        self.seek_speed *= 10** dt
        if diff.magnitude() < 50:
            self.game.pickups.remove(self)
            self.game.player.charge += self.capacity
            if self.game.player.charge > 125:
                self.game.player.charge = 125
            if random.random() < 0.2:
                self.game.pickup_battery.play()
        diff *= self.seek_speed/diff.magnitude()
        self.position += diff*dt
        pass

    def draw(self, screen, offset=(0, 0)):

        x = offset[0] - self.glow.get_width()//2 + self.position.x
        y = offset[1] - self.glow.get_height()//2 + self.position.y
        screen.blit(self.glow, (x, y), special_flags=pygame.BLEND_ADD)

        x = offset[0] - self.surf.get_width()//2 + self.position.x
        y = offset[1] - self.surf.get_width()//2 + self.position.y
        screen.blit(self.surf, (x, y), special_flags=pygame.BLEND_ADD)