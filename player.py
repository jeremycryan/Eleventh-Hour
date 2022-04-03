from primitives import GameObject, Pose
import pygame
from projectile import Kunai
import constants as c

class Player(GameObject):

    def __init__(self, game):
        self.position = Pose((0, 0))
        self.velocity = Pose((0, 0))
        self.recoil_velocity = Pose((0, 0))
        self.game = game
        self.jumps = 2
        self.grounded = False
        self.projectiles = []
        self.ammo = 3
        self.beaming = False
        self.beam_target = Pose((c.GAME_WIDTH//2, c.GAME_HEIGHT//2 - 150))

    def update(self, dt, events):
        for projectile in self.projectiles[:]:
            projectile.update(dt, events)
            if (projectile.position - Pose((c.WINDOW_WIDTH//2, c.WINDOW_HEIGHT//2))).magnitude() > c.WINDOW_WIDTH*3:
                self.projectiles.remove(projectile)
            if (projectile.pickup or projectile.gravity) and (projectile.position - self.position).magnitude() < 30:
                self.projectiles.remove(projectile)
                self.ammo += 1

        if self.beaming:
            self.velocity = (self.beam_target - self.position)*1.5
            self.position += self.velocity * dt
            return

        gravity = 3000
        speed = 800

        self.recoil_velocity *= 0.0001**dt

        pressed = pygame.key.get_pressed()
        left = pressed[pygame.K_a]
        right = pressed[pygame.K_d]
        up = pressed[pygame.K_w]
        down = pressed[pygame.K_s]
        control_velocity = Pose((speed * (right - left), 1200 * down))
        self.velocity += Pose((0, 1000*-up)) * dt

        mpos = pygame.mouse.get_pos()
        relmpos = Pose(mpos) * (c.GAME_WIDTH/c.WINDOW_WIDTH) - self.position

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.try_jump()
                if event.key == pygame.K_e:
                    if not self.game.rewinding:
                        self.game.start_rewind()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.shoot(relmpos)


        self.velocity += Pose((0, gravity)) * dt

        if self.position.y > self.game.floor - 20:
            if self.velocity.y + control_velocity.y + self.recoil_velocity.y > 0:
                self.land()

        if self.grounded:
            self.velocity -= self.velocity
            control_velocity.y = 0
            self.position.y = self.game.floor - 20

        self.position += self.velocity * dt + control_velocity * dt + self.recoil_velocity * dt

        if self.position.x < 0 or self.position.x > c.WINDOW_WIDTH:
            self.position.x = max(0, min(c.WINDOW_WIDTH, self.position.x))
            self.recoil_velocity.x = 0

    def land(self):
        self.jumps = 2
        self.grounded = True

    def try_jump(self):
        if self.jumps > 0:
            self.jump()

    def jump(self):
        self.grounded = False
        self.jumps -= 1
        jump = 1000
        self.velocity = Pose((0, -jump))

    def draw(self, surf, offset=(0, 0)):
        position = self.position + Pose(offset)
        pygame.draw.circle(surf, (0, 0, 0), position.get_position(), 25)
        for projectile in self.projectiles:
            projectile.draw(surf, offset)

    def start_tractor_beam(self):
        self.beaming = True
        self.grounded = False
        self.recoil_velocity *= 0

    def end_tractor_beam(self):
        self.beaming = False
        self.recoil_velocity*= 0
        self.jumps = 1
        self.grounded = False
        self.velocity = Pose((0, -500))

    def shoot(self, velocity):
        if not self.ammo:
            return
        self.ammo -= 1
        velocity = velocity * (1/velocity.magnitude()) * 4000
        self.recoil_velocity -= velocity * 0.3
        self.projectiles.append(Kunai(self.game, velocity=velocity.get_position(), position=self.position.get_position()))