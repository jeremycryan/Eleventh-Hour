import pygame
import constants as c
import sys
import math
from player import Player
from primitives import Pose
from particle import RewindParticle, SunExplosion, SunTint
from enemy import Orb, Scuttle

import random

class Game:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        self.colorblind_mode = True

        self.init()
        self.main()

    def update_display(self):
        pygame.display.flip()

    def get_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        dt = self.clock.tick(90)/1000
        return events, dt

    def spawn_scuttle(self, left=True):
        y = c.WINDOW_HEIGHT * 0.73
        if not left:
            self.enemies.append(Scuttle(self, (c.WINDOW_WIDTH + 200, y), (-1, 0)))
        else:
            self.enemies.append(Scuttle(self, (-200, y), (1, 0)))

    def spawn_orb(self, left=True):
        if left:
            self.enemies.append(Orb(self, (-50, -random.random() * 200 - 50), direction=(1, 0)))
        else:
            self.enemies.append(Orb(self, (c.WINDOW_WIDTH + 50, -random.random() * 200 - 50), direction=(-1, 0)))

    def init(self):
        self.day = 1
        self.xpos = 0
        self.speed = 500

        self.horizon = c.GAME_HEIGHT * 0.6
        self.floor = c.GAME_HEIGHT - 140
        self.game_time = 0

        self.player = Player(self)
        self.player.position = Pose((c.GAME_WIDTH//2, c.GAME_HEIGHT//2 - 100))

        self.particles = []
        self.enemies = []
        self.spawn_scuttle(True)
        self.spawn_scuttle(False)
        self.spawn_orb(False)
        self.spawn_orb(True)

        self.background = pygame.image.load("images/bakground.png")
        self.background_reflection = pygame.transform.flip(self.background, 0, 1)
        self.background_buildings = pygame.image.load("images/background_buildings.png")
        self.background_buildings.set_colorkey((255, 255, 255))
        self.bb_reflection = pygame.transform.flip(self.background_buildings, 0, 1)
        self.bb_reflection.set_colorkey((255, 255, 255))
        self.water_shade = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT - self.horizon))
        self.water_shade.fill((0, 0, 0))
        self.foreground_buildings = pygame.image.load("images/foreground_buildings.png")
        self.foreground_buildings.set_colorkey((255, 255, 255))
        self.sun = pygame.image.load("images/sun.png")
        self.train = pygame.image.load("images/train.png")

        self.blue = pygame.image.load("images/blue.png")
        self.blue = pygame.transform.scale(self.blue, (c.GAME_WIDTH, c.GAME_HEIGHT))
        self.blue_color = self.blue.get_at((0, 0))

        self.clock = pygame.time.Clock()
        self.fps_font = pygame.font.SysFont("monospace", 12, bold=False)
        self.fpss = [0]

        self.lightener = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT))
        self.lightener.fill((255, 255, 255))
        self.lightener.set_alpha(30)
        self.day_when_rewind = 1

        self.rewinding = False

        self.shake_amp = 0
        self.shake_direction = Pose((1, 0))
        self.since_shake = 0

        self.kunai_ui = pygame.image.load("images/kunai_ui.png")

    def get_offset(self):

        if self.shake_direction.magnitude() <1:
            return (0, 0)
        return (self.shake_direction * (1/self.shake_direction.magnitude()) * self.shake_amp * math.cos(self.since_shake*20)).get_position()

    def update_background(self, dt, events):
        self.since_shake += dt
        self.shake_amp *= 0.01**dt
        self.shake_amp = max(0, self.shake_amp - 5*dt)

        self.xpos += self.speed * dt
        self.game_time += dt - dt*0.8*self.rewinding
        if not self.rewinding:
            self.day -= (1/30)*dt
        else:
            pace = (1 - self.day_when_rewind)/3
            self.day += pace*dt
        if self.rewinding and self.day >= 1:
            self.stop_rewinding()
        if self.day < 0:
            self.day = 0

        lightness = self.day
        bc = tuple([max(0, int(item * lightness)) for item in self.blue_color])
        self.blue.fill(bc)

        if self.rewinding and self.speed > 100:
            self.speed = max(self.speed - 2000 * dt, 50)
        if not self.rewinding:
            self.speed = min(self.speed + 2000 * dt, 500)

    def update_fps(self, dt, events):
        self.fpss.append(1/dt)
        self.fpss = self.fpss[-100:]

    def draw_fps(self, surface):
        fps = int(round(sum(self.fpss)/len(self.fpss), 0))

        color = (0, 0, 0)
        if self.day < 0.2:
            color = (255, 255, 255)

        label = self.fps_font.render("FPS: MIN   AVG   MAX", 0, color)

        maxfps = max(self.fpss)
        minfps = min(self.fpss)
        text = f"{int(minfps)} |  {fps} |  {int(maxfps)}"
        surf = self.fps_font.render(text, 0, color)
        surface.blit(label, (c.GAME_WIDTH - label.get_width() - 10, 10))
        surface.blit(surf, (c.GAME_WIDTH - surf.get_width() - 10, 10 + label.get_height()))

    def draw_background(self, surf, offset=(0, 0)):
        bgh = self.background.get_height()
        margin = max(0, bgh - c.GAME_HEIGHT)
        bgy = -margin * self.day
        ba = pygame.Rect((0, -bgy, c.GAME_WIDTH, self.horizon))
        surf.blit(self.background, (0, 0), area=ba)
        bra = pygame.Rect((0, margin * (1 - self.day) + (c.GAME_HEIGHT - self.horizon)/2, c.GAME_WIDTH, c.GAME_HEIGHT - self.horizon))
        surf.blit(self.background_reflection, (0, self.horizon), area=bra)



        sun_peak_height = self.sun.get_height() * 1.5
        sx = c.GAME_WIDTH//2 - self.sun.get_width()//2 + offset[0]
        sy = int(self.horizon - sun_peak_height * self.day + offset[1])
        sa = (0, 0, self.sun.get_width(), int(sun_peak_height * self.day))
        surf.blit(self.sun, (sx, sy), area=sa)

        bbw = self.background_buildings.get_width()
        bbh = self.background_buildings.get_height()
        bbx = int((-self.xpos * 0.1) % bbw - bbw + offset[0])
        bby = int(self.horizon + offset[1])
        while bbx < c.GAME_WIDTH:
            surf.blit(self.background_buildings, (bbx, bby - bbh))
            surf.blit(self.bb_reflection, (bbx, bby))
            bbx += bbw

        self.water_shade.set_alpha(60 + 20 * self.day)
        surf.blit(self.water_shade, (0, self.horizon + offset[1]))

        fbw = self.foreground_buildings.get_width()
        fbh = self.foreground_buildings.get_height()
        fbx = int((-self.xpos * 0.7) % fbw - fbw + offset[0])
        fby = int(c.GAME_HEIGHT + offset[1] - fbh + 30)
        while fbx < c.GAME_WIDTH:
            surf.blit(self.foreground_buildings, (fbx, fby))
            fbx += fbw

        surf.blit(self.blue, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

        train_center_x = c.GAME_WIDTH//2
        train_spacing = 5
        train_width = self.train.get_width()
        train_start_x = train_center_x - self.train.get_width()//2 + offset[0] - train_spacing - train_width

        if self.colorblind_mode:
            surf.blit((self.lightener), (0, 0))

        for number in range(3):
            xo, yo = self.get_train_offset(number)
            train_x = int(train_start_x + number * train_spacing + number * train_width + xo)
            train_y = int(self.floor - 5 + yo + offset[1])
            surf.blit(self.train, (train_x, train_y), special_flags=pygame.BLEND_MULT)

    def get_train_number(self, x):
        train_center_x = c.GAME_WIDTH // 2
        train_width = self.train.get_width()
        if x < train_center_x - train_width//2 - 38:
            return 0
        elif x < train_center_x + train_width//2 - 35:
            return 1
        else:
            return 2

    def get_train_offset(self, number):
        xo = -math.sin(self.game_time * 10 + number * 10) * 1.5
        yo = math.cos(self.game_time * 10 + number * 10) * 1.5
        return xo, yo

    def start_rewind(self):
        self.rewinding = True
        self.player.start_tractor_beam()
        self.day_when_rewind = self.day
        if self.day_when_rewind == 1:
            self.day_when_rewind = 0.999
        for i in range(1000):
            self.particles.append(RewindParticle(self))
        self.particles.append(SunTint(duration=3, alpha=100))
        for enemy in self.enemies:
            if not enemy.destroyed:
                enemy.destroy()

    def stop_rewinding(self):
        self.rewinding = False
        self.day = 1
        self.player.end_tractor_beam()
        self.particles.append(SunExplosion(self))

    def get_train_offset_from_x(self, x):
        return self.get_train_offset(self.get_train_number(x))

    def draw_hud(self, surf, offset=(0, 0)):
        x = c.GAME_WIDTH//2 - self.player.ammo * self.kunai_ui.get_width()//2
        y = c.GAME_HEIGHT - 50
        for i in range(self.player.ammo):
            surf.blit(self.kunai_ui, (x, y))
            x += 20



    def main(self):
        self.clock.tick(60)

        while True:
            events, dt = self.get_events()
            self.update_background(dt, events)
            self.update_fps(dt, events)
            self.player.update(dt, events)
            keep_particles = []
            for particle in self.particles:
                particle.update(dt, events)
                if not particle.destroyed:
                    keep_particles.append(particle)
            self.particles = keep_particles
            for enemy in self.enemies[:]:
                enemy.update(dt, events)

            offset = self.get_offset()


            self.draw_background(self.screen, offset)
            self.draw_hud(self.screen)
            for enemy in self.enemies:
                enemy.draw(self.screen, offset)
            for particle in self.particles[:]:
                particle.draw(self.screen, offset)
            self.player.draw(self.screen, offset)
            self.draw_fps(self.screen)

            self.update_display()

    def shake(self, direction=None, amt=15):
        if amt < self.shake_amp:
            return
        else:
            self.shake_amp = amt
        if direction and Pose(direction).magnitude() > 0:
            self.shake_direction = Pose(direction)
        else:
            self.shake_direction = Pose((1, 1))
        self.since_shake = 0




if __name__=="__main__":
    Game()