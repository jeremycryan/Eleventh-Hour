import pygame
from primitives import Pose
import math
import constants as c
import random
from particle import KunaiHitParticle

class Projectile:

    def __init__(self):
        pass

    def update(self, dt, events):
        pass

    def draw(self, surface, offset=(0, 0)):
        pass


class Kunai:

    surf = None
    shadow_surf = None

    def __init__(self, game, position = (0, 0), velocity = (0, 0)):
        self.game = game
        self.velocity = Pose(velocity)
        self.position = Pose(position)
        self.last_position = self.position.copy()
        self.direction = self.velocity * (1/self.velocity.magnitude())
        if not self.surf:
            Kunai.surf = pygame.image.load("images/kunai.png")
            Kunai.surf.set_colorkey((255, 255, 255))
            Kunai.shadow_surf = Kunai.surf.copy()

        self.shadows = []
        self.gravity = False
        self.pickup = False
        self.stuck = False

    def launch(self, velocity):
        self.velocity = velocity.copy()

    def update(self, dt, events):
        self.last_position = self.position.copy()
        self.position += self.velocity * dt
        if self.velocity.magnitude() > 1:
            self.direction = self.velocity * (1/self.velocity.magnitude())

        if not self.pickup and not self.stuck:
            # Make shadows and things
            increment = (self.position - self.last_position)
            dist = increment.magnitude()

            if self.gravity:
                self.velocity.x *= 0.1**dt
                self.velocity += Pose((0, 5000)) * dt

            if dist != 0:
                increment *= 1/increment.magnitude()
                increment *= 10
                traveled = 0
                current = self.last_position.copy()
                while traveled < dist:
                    self.shadows.append([current, 60])
                    current += increment
                    traveled += increment.magnitude()


        for item in self.shadows[:]:
            item[1] -= 1000 * dt
            if item[1] < 0:
                self.shadows.remove(item)

        if (self.position.x > c.WINDOW_WIDTH or self.position.x < 0) and not self.stuck:
            self.position.x = min(c.WINDOW_WIDTH, max(0, self.position.x))
            self.velocity.x *= -0.4 - 0.3*random.random()
            if abs(self.velocity.x) < 1000:
                self.velocity.x *= (1000/abs(self.velocity.x))
            self.velocity *= 0.1 + 0.2 * random.random()
            self.gravity = True
            self.hit_effect()
            self.game.kunai_hit.play()

        if self.position.y < -c.WINDOW_HEIGHT:
            self.velocity.y = 0
            self.position.y = -c.WINDOW_HEIGHT
            self.gravity = True

        if self.position.y > c.WINDOW_HEIGHT * 0.8:
            self.hit_effect(velocity=(self.velocity.x, -abs(self.velocity.y)))
            self.position.y = c.WINDOW_HEIGHT * 0.8
            self.velocity = Pose((0, 0))
            self.pickup = True
            self.game.kunai_hit.play()

    def hit_effect(self, velocity=None):
        for i in range(30):
            if not velocity:
                velocity = self.velocity.get_position()
            self.game.particles.append(KunaiHitParticle(self.position.get_position(), velocity))
        self.game.shake(velocity, 10)

    def hit(self, enemy):
        self.hit_effect((self.position - enemy.position).get_position())
        self.velocity = Pose((0, 0))
        self.stuck = True
        self.game.kunai_hit.play()

    def draw(self, surface, offset=(0, 0)):
        angle = math.atan2(-self.direction.y, self.direction.x)
        surf = pygame.transform.rotate(self.surf, math.degrees(angle))

        for item in self.shadows[:]:
            if item[1] > 0:
                ssurf = surf.copy()
                pos = item[0] + Pose(offset) - Pose((ssurf.get_width()//2, ssurf.get_height()//2))
                ssurf.set_alpha(item[1])
                surface.blit(ssurf, pos.get_position())

        pos = self.position + Pose(offset) - Pose((surf.get_width()//2, surf.get_height()//2))
        if self.pickup:
            pos += Pose(self.game.get_train_offset_from_x(pos.x))
        surface.blit(surf, pos.get_position())
