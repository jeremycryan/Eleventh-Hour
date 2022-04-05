from primitives import Pose
import random
import math
import pygame
import constants as c


class Particle:

    def __init__(self, position=(0, 0), velocity=(0, 0), duration=1):
        self.position = Pose(position)
        self.velocity = Pose(velocity)
        self.destroyed = False
        self.duration = duration
        self.age = 0

    def update(self, dt, events):
        if self.destroyed:
            return
        self.position += self.velocity * dt
        self.age += dt
        if self.age > self.duration:
            self.destroy()

    def draw(self):
        if self.destroyed:
            return

    def through(self):
        return self.age/self.duration

    def destroy(self):
        self.destroyed = True


class KunaiHitParticle(Particle):

    def __init__(self, position, velocity=None, duration=0.3, color=(255, 255, 255)):
        self.color = color
        velocity_mag = random.random()**2 * 700 + 300
        if not velocity:
            velocity_angle = random.random() * 2 * math.pi
        else:
            velocity_angle = math.atan2(velocity[0], velocity[1]) + random.choice((-1, 1))*random.random()**4*math.pi/2
        velocity_x = math.sin(velocity_angle) * velocity_mag
        velocity_y = math.cos(velocity_angle) * velocity_mag
        velocity = velocity_x, velocity_y
        super().__init__(position=position, velocity=velocity, duration=duration)
        self.age += random.random() * 0.3

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity *= 0.005**dt

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return
        corners = [[3, 0], [0, -0.5], [-1, 0], [0, 0.5]]

        angle = math.atan2(self.velocity.y, self.velocity.x)

        scale = 15 * (1 - self.through())
        for corner in corners:
            original_angle = math.atan2(corner[1], corner[0])
            new_angle = angle - original_angle
            mag = math.sqrt(corner[0]**2 + corner[1]**2)
            mag *= scale
            corner[0] = math.cos(new_angle) * mag
            corner[1] = math.sin(new_angle) * mag
            corner[0] += self.position.x
            corner[1] += self.position.y

        pygame.draw.polygon(surf, self.color, corners)


        pass


class RewindParticle(Particle):

    surf = None

    def __init__(self, game, duration = 3):
        self.game = game
        if not self.surf:
            self.surf = pygame.Surface((40, 6))
            self.surf.fill((0, 0, 0))
            pygame.draw.ellipse(self.surf, (100, 255, 255), self.surf.get_rect())
            self.surf.set_colorkey((0, 0, 0))

        self.angle = random.random() * math.pi * 2
        self.distance = random.random() * c.GAME_WIDTH//2 + 100
        self.start_distance = self.distance
        super().__init__(duration=duration)

    def update(self, dt, events):
        if self.destroyed:
            return
        self.angle -= 300 * dt / self.distance * (self.through()) * 5
        self.distance -= 0 * dt * self.through()
        super().update(dt, events)


    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return
        margin = 10
        if self.position.x < -margin or self.position.x > c.GAME_WIDTH + margin:
            if self.position.y < - margin or self.position.y > c.GAME_HEIGHT + margin:
                return
        surf_to_draw = self.surf.copy()
        darken_alpha = 200 + 55 * (1 - self.through()) #((1 - self.through()**2)) * 100 + 155
        dark = pygame.Surface(surf_to_draw.get_size())
        dark.fill((0, 0, 0))
        dark.set_alpha(darken_alpha)
        surf_to_draw.blit(dark, (0, 0))
        surf_to_draw = pygame.transform.rotate(surf_to_draw, math.degrees(-self.angle + math.pi/2))
        x = offset[0] + c.WINDOW_WIDTH//2 + math.cos(self.angle) * self.distance - surf_to_draw.get_width()//2
        y = offset[1] + c.WINDOW_HEIGHT//2 - 150 + math.sin(self.angle) * self.distance - surf_to_draw.get_height()//2
        y += (1 - self.game.day) * 300
        surf.blit(surf_to_draw, (x, y), special_flags=pygame.BLEND_ADD)

        pass


class SunExplosion(Particle):

    def __init__(self, game, duration = 0.7, color = (255, 255, 255)):
        super().__init__(duration=duration)
        self.color = color
        self.light = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT))
        self.light.fill(color)
        self.game = game
        self.game.shake(amt=30)

    def update(self, dt, events):
        super().update(dt, events)

    def destroy(self):
        super().destroy()

    def draw(self, surface, offset=(0, 0)):
        if self.through() < 0.5:
            max_rad = math.sqrt(c.WINDOW_WIDTH**2 + c.WINDOW_HEIGHT**2) * 0.75
            min_rad = 110
            rad = min_rad + (max_rad - min_rad) * math.sqrt(self.through())*2
            pygame.draw.circle(surface, self.color, (c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2 - 150), rad)
        else:
            self.light.set_alpha(255 - (255 * 2 * (self.through() - 0.5)))
            surface.blit(self.light, (0, 0))

class SunExplosionLong(Particle):

    def __init__(self, game, duration = 10, color = (255, 255, 255), callback=None):
        super().__init__(duration=duration)
        self.color = color
        self.light = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT))
        self.light.fill(color)
        self.dark = pygame.Surface(self.light.get_size())
        self.dark.fill((0, 0, 0))
        self.game = game
        self.game.shake(amt=30)
        self.callback = callback

    def update(self, dt, events):
        super().update(dt, events)

    def destroy(self):
        self.callback()

    def draw(self, surface, offset=(0, 0)):
        if self.through() < 0.1:
            max_rad = math.sqrt(c.WINDOW_WIDTH**2 + c.WINDOW_HEIGHT**2) * 0.75
            min_rad = 110
            rad = min_rad + (max_rad - min_rad) * math.sqrt(self.through())*10
            pygame.draw.circle(surface, self.color, (c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2 - 150), rad)
        else:
            self.light.set_alpha(255 - (255 * 1.1111 * (self.through() - 0.1)))
            surface.blit(self.dark, (0, 0))
            surface.blit(self.light, (0, 0))

class SunTint(Particle):

    def __init__(self, duration = 0.7, alpha = 255):
        super().__init__(duration=duration)
        self.light = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT))
        self.light.fill((255, 255, 255))
        self.start_alpha = alpha

    def update(self, dt, events):
        super().update(dt, events)

    def draw(self, surface, offset=(0, 0)):
        self.light.set_alpha(self.through() * self.start_alpha)
        surface.blit(self.light, (0, 0))


class BigBoom(Particle):

    surf = None
    def __init__(self, position, velocity=None, duration=0.3):
        super().__init__(position=position, duration=duration)
        if not self.surf:
            self.surf = pygame.Surface((400, 400))
            self.surf.fill((0, 0, 0))
            pygame.draw.ellipse(self.surf, (255, 255, 255), self.surf.get_rect())
            self.surf.set_colorkey((0, 0, 0))
        self.starting_scale = 0.1
        self.scale = self.starting_scale
        self.alpha = 255

    def update(self, dt, events):
        self.scale = self.starting_scale + (1 - self.starting_scale) * self.through()**0.5
        self.alpha = 255 - 255*self.through()
        super().update(dt, events)

    def draw(self, surf, offset=(0, 0)):
        my_surf = pygame.transform.scale(self.surf, (int(self.surf.get_width()*self.scale), int(self.surf.get_height()*self.scale) ))
        my_surf.set_alpha(self.alpha)
        x = self.position.x + offset[0] - my_surf.get_width()//2
        y = self.position.y + offset[1] - my_surf.get_height()//2
        surf.blit(my_surf, (x, y))


class BoomParticle(Particle):
    def __init__(self, position, velocity=None, duration=1.5):
        velocity_mag = random.random()**4 * 700
        if not velocity:
            velocity_angle = random.random() * 2 * math.pi
        else:
            velocity_angle = math.atan2(velocity[0], velocity[1]) + random.choice((-1, 1))*(random.random()**4)*math.pi/2
        velocity_x = math.sin(velocity_angle) * velocity_mag
        velocity_y = math.cos(velocity_angle) * velocity_mag
        velocity = velocity_x, velocity_y
        super().__init__(position=position, velocity=velocity, duration=duration)
        self.age += random.random() * 1

    def update(self, dt, events):
        super().update(dt, events)
        if self.velocity.x > -500:
            self.velocity.x -= 1200*dt
        self.velocity.y *= 0.1**dt

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return

        scale = (1 - self.through())
        radius = 20

        x, y = (self.position + Pose(offset)).get_position()
        pygame.draw.circle(surf, (255, 255, 255), (x, y), radius*scale)


        pass


class Laser(Particle):

    def __init__(self, position, direction):
        super().__init__(position, duration=0.5)
        self.direction = Pose(direction)
        self.height = 100

    def draw(self, surface, offset=(0, 0)):
        vh = self.height * (1 - self.through())**3
        x0 = 0
        if self.direction.x > 0:
            width = (c.GAME_WIDTH - self.position.x - offset[0])
            x0 = self.position.x
        else:
            width = (self.position.x + offset[0])
        y0 = self.position.y + offset[1] - vh//2

        rect = x0, y0, width, vh
        pygame.draw.rect(surface, (255, 255, 255), rect)


class LaserGuide(Particle):

    def __init__(self, position, direction):
        super().__init__(position, duration=1)
        self.direction = Pose(direction)
        self.height = 3

    def draw(self, surface, offset=(0, 0)):
        vh = self.height
        x0 = 0
        if self.direction.x > 0:
            width = (c.GAME_WIDTH - self.position.x - offset[0])
            x0 = self.position.x
        else:
            width = (self.position.x + offset[0])
        y0 = self.position.y + offset[1] - vh//2

        rect = x0, y0, width, vh
        if self.age % 0.1 < 0.05:
            pygame.draw.rect(surface, (255, 0, 0), rect)
        else:
            pygame.draw.rect(surface, (255, 150, 150), rect)


class LaserBoomParticle(Particle):
    def __init__(self, position, direction=(1, 0), velocity=None, duration=1.5):
        velocity_mag = random.random()**2 * 800
        if not velocity:
            velocity_angle = random.random() * 2 * math.pi
        else:
            velocity_angle = math.atan2(velocity[0], velocity[1]) + random.choice((-1, 1))*(random.random()**4)*math.pi/2
        velocity_x = math.sin(velocity_angle) * velocity_mag
        velocity_y = math.cos(velocity_angle) * velocity_mag
        velocity = velocity_x, velocity_y
        super().__init__(position=position, velocity=velocity, duration=duration)
        self.age += random.random() * 0.25
        self.velocity.x = abs(self.velocity.x) * (1 + random.random()*500/(abs(self.velocity.y) + 1))
        if direction[0] < 1:
            self.velocity.x *= -1

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity *= 0.01**dt

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return

        scale = (1 - self.through())**2
        radius = 25

        x, y = (self.position + Pose(offset)).get_position()
        pygame.draw.circle(surf, (255, 255, 255), (x, y), radius*scale)


        pass


class WarningParticle(Particle):

    surf = None
    def __init__(self, position=(0, 0)):
        super().__init__(position, duration = 1.5)
        if not self.surf:
            WarningParticle.surf = pygame.image.load("images/warning.png")
            WarningParticle.surf.set_colorkey((0, 0, 0))

    def update(self, dt, events):
        super().update(dt, events)

    def draw(self, surf, offset=(0, 0)):
        x = self.position.x + offset[0] - self.surf.get_width()//2
        y = self.position.y + offset[1] - self.surf.get_height()//2
        if self.through() %0.2 < 0.1:
            surf.blit(self.surf, (x, y), special_flags=pygame.BLEND_ADD)