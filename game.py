import pygame
import constants as c
import sys
import math
from player import Player
from primitives import Pose
from particle import RewindParticle, SunExplosion, SunTint, WarningParticle, BigBoom, SunExplosionLong
from enemy import Orb, Scuttle
from Button import Button

import random

class Game:

    def __init__(self):
        pygame.init()
        self.fullscreen = True
        self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        pygame.display.set_icon(pygame.image.load("images/kunai_ui.png"))
        self.colorblind_mode = True
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Eleventh Hour")

        self.config_menu()
        self.last_distance = None

        self.intro()
        self.directions()

        while True:

            self.init()
            self.main()

    def victory_screen(self, prev_surf):
        shade = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        shade.fill((255, 255, 255))
        alpha = 0
        age = 0
        while alpha < 255:
            events, dt = self.get_events()
            age += dt
            self.screen.fill((0, 0, 0))
            self.screen.blit(prev_surf, (0, 0))

            alpha += 255 * dt
            shade.set_alpha(alpha)
            self.screen.blit(shade, (0, 0))

            self.update_display()

        back = pygame.image.load("images/win.png")
        age = 0
        alpha = 255
        should_Break = False
        etc = pygame.image.load("images/etc_light.png")
        while not should_Break:
            events, dt = self.get_events()
            age += dt
            self.screen.blit(back, (0, 0))
            if age > 3 and age%1 < 0.7:
                self.screen.blit(etc, (c.WINDOW_WIDTH//2 - etc.get_width()//2, c.WINDOW_HEIGHT - etc.get_height()))

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        should_Break = True

            shade.set_alpha(alpha)
            self.screen.blit(shade, (0, 0))
            alpha -= 255 * dt

            self.update_display()
        alpha = 0
        age = 0

        shade.fill((0, 0, 0))

        while alpha < 255:
            events, dt = self.get_events()
            age += dt
            self.screen.fill((0, 0, 0))
            self.screen.blit(back, (0, 0))

            alpha += 255 * dt
            shade.set_alpha(alpha)
            self.screen.blit(shade, (0, 0))

            self.update_display()
        pygame.quit()
        sys.exit()

    def directions(self):
        shade = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))
        shade.fill((0, 0, 0))
        back = pygame.image.load("images/instructions.png")
        age = 0
        alpha = 255
        should_Break = False
        etc = pygame.image.load("images/enter_to_continue.png")
        while not should_Break:
            events, dt = self.get_events()
            age += dt
            self.screen.blit(back, (0, 0))
            if age > 3 and age%1 < 0.7:
                self.screen.blit(etc, (c.WINDOW_WIDTH//2 - etc.get_width()//2, c.WINDOW_HEIGHT - etc.get_height()))

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        should_Break = True

            shade.set_alpha(alpha)
            self.screen.blit(shade, (0, 0))
            alpha -= 255 * dt

            self.update_display()
        alpha = 0
        age = 0

        while alpha < 255:
            events, dt = self.get_events()
            age += dt
            self.screen.fill((0, 0, 0))
            self.screen.blit(back, (0, 0))



            shade.set_alpha(alpha)
            self.screen.blit(shade, (0, 0))
            alpha += 500 * dt

            self.update_display()


    def intro(self):
        section = pygame.Surface((c.WINDOW_WIDTH, c.WINDOW_HEIGHT//3 + 15))
        sections = [
            section.copy() for _ in range(3)
        ]
        for section in sections:
            section.fill((0,0,0))
        age = 0
        alphas = [
            255 + 500,
            255 +2000,
            255 +3500,
        ]
        sections[1] = pygame.transform.scale(sections[1], (c.WINDOW_WIDTH, c.WINDOW_HEIGHT//4))
        back = pygame.image.load("images/intro.png")
        while True:
            events, dt = self.get_events()
            age += dt
            self.screen.blit(back, (0, 0))
            for i, alpha in enumerate(alphas):
                alphas[i] -= 500 * dt
                sections[i].set_alpha(alpha)
            x = 0
            y = 0
            for section in sections:
                if age > 13:
                    section.set_alpha(255 * (age - 13))
            for section in sections:
                self.screen.blit(section, (x, y))
                y += c.WINDOW_HEIGHT//3
                if y > c.WINDOW_HEIGHT//2:
                    y -= 100
            self.update_display()
            if age > 14:
                break




    def toggle_colorblind_mode(self):
        self.colorblind_mode = not self.colorblind_mode

    def toggle_fullscreen_mode(self):
        self.fullscreen = not self.fullscreen

    def start(self):
        self.started = True

    def config_menu(self):
        self.started = False
        self.screen = pygame.display.set_mode((400, 200))
        width = 400
        height = 240
        fullscreen_button = Button(
            pygame.image.load("images/fullscreen_enabled.png"),
            pos=(width//2 + 92, height - 100),
            disabled_surf=pygame.image.load("images/fullscreen_disabled.png"),
            enabled=False,
            pulse=0,
            on_click=self.toggle_fullscreen_mode,
        )
        colorblind_button = Button(
            pygame.image.load("images/contrast_enabled.png"),
            pos=(width//2 - 92, height - 100),
            disabled_surf=pygame.image.load("images/contrast_disabled.png"),
            enabled=False,
            pulse=0,
            on_click=self.toggle_colorblind_mode,
        )
        start_button = Button(
            pygame.image.load("images/start_button.png"),
            pos=(width//2, height - 170),
            on_click=self.start,
            pulse=0,
        )
        while not self.started:
            events, dt = self.get_events()
            self.screen.fill((0, 0, 0))
            colorblind_button.update(dt, events)
            fullscreen_button.update(dt, events)
            start_button.update(dt, events)
            fullscreen_button.enabled = self.fullscreen
            colorblind_button.enabled = self.colorblind_mode
            fullscreen_button.draw(self.screen)
            colorblind_button.draw(self.screen)
            start_button.draw(self.screen)
            self.update_display()

        if self.fullscreen:
            self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT), flags=pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((c.WINDOW_WIDTH, c.WINDOW_HEIGHT))


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
            self.enemies.append(Scuttle(self, (c.WINDOW_WIDTH + 1000, y), (-1, 0)))
            self.particles.append(WarningParticle((c.WINDOW_WIDTH - 50, y)))
        else:
            self.enemies.append(Scuttle(self, (-1000, y), (1, 0)))
            self.particles.append(WarningParticle((50, y)))

    def spawn_orb(self, left=True):
        if left:
            self.enemies.append(Orb(self, (-50, -random.random() * 200 - 50), direction=(1, 0)))
        else:
            self.enemies.append(Orb(self, (c.WINDOW_WIDTH + 50, -random.random() * 200 - 50), direction=(-1, 0)))

    def game_start(self):
        self.game_started = True
        self.start_pos = self.xpos
        pygame.mixer.music.play()

    def init(self):
        self.day = 1
        self.xpos = 0
        self.speed = 500
        self.since_orb = 0

        self.ccs_surf = None

        self.start_pos = 0
        self.alef_14 = pygame.font.Font("fonts/alef.ttf", 14)

        self.shade = pygame.Surface((c.GAME_WIDTH, c.GAME_HEIGHT))
        self.shade.fill((0, 0, 0))
        self.shade_alpha = 255

        self.really_lost = False

        self.game_started = False

        self.music = pygame.mixer.music.load("sounds/music.ogg")

        self.player_hurt = pygame.mixer.Sound("sounds/hurt.wav")
        self.mrew = pygame.mixer.Sound("sounds/mrew.wav")
        self.mrew.set_volume(0.0)

        self.title = pygame.image.load("images/title.png")
        self.title.set_colorkey((255, 0, 0))
        self.title_pos = int(c.WINDOW_HEIGHT * 0.3)

        self.nope_sound = pygame.mixer.Sound("sounds/nope.wav")
        self.nope_sound.set_volume(0.2)
        self.restart_sound = pygame.mixer.Sound("sounds/restart.wav")
        self.restart_sound.set_volume(0.5)
        self.rewind_sound = pygame.mixer.Sound("sounds/rewind.wav")
        self.pickup_battery = pygame.mixer.Sound("sounds/pickup_battery.wav")
        self.pickup_battery.set_volume(0.1)
        self.pickup_kunai = pygame.mixer.Sound("sounds/pickup_kunai.wav")
        self.pickup_kunai.set_volume(0.1)
        self.laser_sound = pygame.mixer.Sound("sounds/laser.wav")
        self.laser_sound.set_volume(0.75)
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.wav")
        self.shoot_kunai_sound = pygame.mixer.Sound("sounds/throw_kunai.wav")
        self.shoot_kunai_sound.set_volume(0.2)
        self.laser_aim = pygame.mixer.Sound("sounds/laser_aim.wav")
        self.laser_aim.set_volume(0.2)
        self.kunai_hit = pygame.mixer.Sound("sounds/kunai_hit.wav")
        self.kunai_hit.set_volume(0.8)
        self.jump_sound = pygame.mixer.Sound("sounds/jump.wav")
        self.jump_sound.set_volume(0.3)


        self.press_e= pygame.image.load("images/press_e.png")

        self.horizon = c.GAME_HEIGHT * 0.6
        self.floor = c.GAME_HEIGHT - 140
        self.game_time = 0

        self.player = Player(self)
        self.player.position = Pose((c.GAME_WIDTH//2, -100))

        self.particles = []
        self.enemies = []

        self.water_texture = pygame.image.load("images/water.png")

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
        self.pickups = []

        self.quad_ui = pygame.image.load("images/charge_quadrant_one.png")
        self.quad_color_ui = pygame.image.load("images/charge_quad_color.png")
        self.center_ui = pygame.image.load("images/charge_center.png")
        self.center_color_ui = pygame.image.load("images/charge_center_color.png")
        self.charge_back_ui = pygame.image.load("images/charge_background.png")
        self.charge_glow = pygame.image.load("images/charge_glow.png")

        self.since_scuttle = 0


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
        if self.game_started:
            if not self.rewinding:
                self.day -= (1/36.5)*dt
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
        return
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
        surf.blit(self.water_texture, (0, self.horizon + offset[1]), special_flags= pygame.BLEND_ADD)

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
        pygame.mixer.music.fadeout(250)
        self.rewind_sound.play()
        self.rewinding = True
        self.player.start_tractor_beam()
        self.day_when_rewind = self.day
        if self.day_when_rewind == 1:
            self.day_when_rewind = 0.999
        for i in range(1000):
            self.particles.append(RewindParticle(self))
        self.particles.append(SunTint(duration=3, alpha=100))
        self.destroy_all_enemies(silent=True)

    def destroy_all_enemies(self, silent=False):
        for enemy in self.enemies:
            if not enemy.destroyed:
                enemy.reward = 0
                enemy.destroy(silent=silent)

    def stop_rewinding(self):
        pygame.mixer.music.rewind()
        pygame.mixer.music.play()

        self.mrew.play()
        self.restart_sound.play()
        self.rewinding = False
        self.day = 1
        self.player.end_tractor_beam()
        self.particles.append(SunExplosion(self))
        self.player.charge = 0

    def lose(self):
        if self.lost:
            return
        self.particles.append(SunExplosionLong(self, duration=6, color=(255, 0, 0), callback=self.really_lose))
        self.lost = True
        self.last_distance = self.xpos

    def get_train_offset_from_x(self, x):
        return self.get_train_offset(self.get_train_number(x))

    def draw_hud(self, surf, offset=(0, 0)):
        x = c.GAME_WIDTH//2 - (self.player.ammo - 1) * 10 - 18
        y = c.GAME_HEIGHT - 45
        for i in range(self.player.ammo):
            surf.blit(self.kunai_ui, (x, y))
            x += 20

        charge_per_section = 25
        max_charge = charge_per_section * 5
        quads = self.player.charge//charge_per_section
        remainder = self.player.charge%charge_per_section

        x = c.WINDOW_WIDTH//2 - self.charge_back_ui.get_width()//2
        y = c.WINDOW_HEIGHT - 105 - self.charge_back_ui.get_height()//22

        quad = self.quad_ui.copy()
        quad_color = self.quad_color_ui.copy()
        quad_color.set_colorkey((0, 0, 0))
        center_color = self.center_color_ui.copy()
        center_color.set_colorkey((0, 0, 0))
        if quads >= 5:
            glow = self.charge_glow.copy()
            dark = pygame.Surface(glow.get_size())
            dark.fill((0, 0, 0))
            dark.set_alpha(50 + 128 * math.sin(self.game_time*6))
            glow.blit(dark, (0, 0))
            surf.blit(glow, (x - glow.get_width()//2 + quad.get_width()//2, y), special_flags=pygame.BLEND_ADD)
            if not self.rewinding and self.game_time%1 < 0.7:
                pos = c.WINDOW_WIDTH//2 - self.press_e.get_width()//2, y - 28
                surf.blit(self.press_e, pos)
        surf.blit(self.charge_back_ui, (x, y))
        for i in range(4):
            if i >= quads:
                break
            surf.blit(quad, (x, y))
            quad = pygame.transform.rotate(quad, -90)
            quad_color = pygame.transform.rotate(quad_color, -90)
        if quads < 4:
            quad_color.set_alpha(remainder/charge_per_section * 255)
            surf.blit(quad_color, (x, y))
        elif quads < 5:
            center_color.set_alpha(remainder/charge_per_section*255)
            surf.blit(center_color, (x, y))
        if quads >= 5:
            surf.blit(self.center_ui, (x, y))

        pixels = self.xpos
        if not self.game_started and self.last_distance:
            pixels = self.last_distance
        miles = round((100000 - pixels + self.start_pos)/1000, 1)
        if not self.game_started and not self.last_distance:
            miles = 100
        city_center_string = f"{miles} miles to city center"
        context_string = f"Last run:"
        ccs_string = self.alef_14.render(f"{miles}", 1, (255, 255, 255))
        if not self.ccs_surf:
            self.ccs_surf = self.alef_14.render(" miles to city center", 1, (255, 255, 255))
        surf.blit(ccs_string, (c.WINDOW_WIDTH - ccs_string.get_width() - self.ccs_surf.get_width() - 5, c.WINDOW_HEIGHT - ccs_string.get_height() - 3))
        surf.blit(self.ccs_surf, (c.WINDOW_WIDTH - self.ccs_surf.get_width() - 5, c.WINDOW_HEIGHT - self.ccs_surf.get_height() - 3))

        if self.last_distance and not self.game_started:
            cx_string = self.alef_14.render(context_string, 1, (255, 255, 255))
            surf.blit(cx_string, (c.WINDOW_WIDTH - cx_string.get_width() - 5, c.WINDOW_HEIGHT - cx_string.get_height() - 19))




    def get_multiplier(self):
        return ((self.xpos - self.start_pos)/14000 + 3)/3

    def main(self):
        self.lost = False
        self.clock.tick(60)

        while True:
            events, dt = self.get_events()
            if dt > 1/20:
                dt = 1/20
            self.update_background(dt, events)
            self.update_fps(dt, events)

            if not self.game_started:
                self.speed = 100

            self.shade_alpha -= 1500 * dt

            if self.game_started:
                keep_particles = []
                for particle in self.particles:
                    particle.update(dt, events)
                    if not particle.destroyed:
                        keep_particles.append(particle)
                self.particles = keep_particles
                if self.lost:
                    dt *= 0.01
                    events = [event for event in events if event.type != pygame.KEYDOWN and event.type != pygame.MOUSEBUTTONDOWN]
                self.player.update(dt, events)
                for pickup in self.pickups[:]:
                    pickup.update(dt, events)
                for enemy in self.enemies[:]:
                    enemy.update(dt, events)
                    if (enemy.position - self.player.position).magnitude() > c.WINDOW_WIDTH * 3:
                        self.enemies.remove(enemy)

                self.since_scuttle += dt
                self.since_orb += dt
                if self.since_scuttle > 3.5 / self.get_multiplier():
                    self.since_scuttle = 0
                    self.spawn_scuttle(random.choice([0, 1]))

                if self.get_multiplier() > 1.4:
                    if self.since_orb > 8 / self.get_multiplier():
                        has_left = False
                        has_right = False
                        for enemy in self.enemies:
                            if type(enemy) == Orb:
                                if enemy.direction.x < 0:
                                    has_right = True
                                else:
                                    has_left = True
                        if not has_left and not has_right:
                            self.spawn_orb(random.choice((1, 0)))
                            self.since_orb = 0
                        elif not (has_left and has_right):
                            self.spawn_orb(has_right)
                            self.since_orb = 0

            offset = self.get_offset()



            self.draw_background(self.screen, offset)
            self.draw_hud(self.screen)
            for pickup in self.pickups:
                pickup.draw(self.screen, offset)
            for enemy in self.enemies:
                enemy.draw(self.screen, offset)
            for particle in self.particles[:]:
                particle.draw(self.screen, offset)
            self.player.draw(self.screen, offset)
            self.draw_fps(self.screen)

            x = c.GAME_WIDTH//2 - self.title.get_width()//2
            y = int(c.GAME_HEIGHT * 0.3) - self.title.get_height()//2
            self.screen.blit(self.title, (x, y))

            if self.game_started:
                self.title_pos -= 1000 * dt
                self.title.set_alpha(self.title_pos * 255 / c.GAME_HEIGHT / 0.3)

            if self.shade_alpha > 0:
                self.shade.set_alpha(self.shade_alpha)
                self.screen.blit(self.shade, (0, 0))

            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if not self.game_started:
                            self.game_start()

            if self.day <= 0:
                self.lose()

            self.update_display()
            if self.really_lost:
                break

            if self.xpos >= 100000:
                self.win()


    def win(self):
        self.victory_screen(self.screen.copy())

    def really_lose(self):
        self.really_lost = True

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