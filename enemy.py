from battery import Battery
from primitives import GameObject, Pose
from sprite import Sprite, SpriteSheet
from particle import BoomParticle, BigBoom, Laser, LaserBoomParticle, LaserGuide
import constants as c


class Enemy(GameObject):

    starting_hp = 1
    reward = 25

    def __init__(self, game, position=(0, 0)):
        self.game = game
        self.hp = self.starting_hp
        self.position = Pose(position)
        self.stuck_projectiles = []
        self.destroyed = False
        self.since_destroy = 0
        self.velocity = Pose((0, 0))
        self.recoil_position = Pose((0, 0))
        self.silent = False

    def update(self, dt, events):
        self.recoil_position += self.velocity * dt
        self.velocity *= 0.0005**dt
        self.recoil_position *= 0.002**dt

        for projectile in self.game.player.projectiles[:]:
            if self.destroyed:
                break
            if self.collides_with_projectile(projectile):
                self.hp -= 1
                self.velocity += projectile.velocity * 0.15
                self.stuck_projectiles.append((projectile, projectile.position - self.position))
                projectile.hit(self)
                projectile.gravity = False
                projectile.pickup = False

        for projectile, rel_pos in self.stuck_projectiles[:]:
            if not projectile.stuck:
                self.stuck_projectiles.remove((projectile, rel_pos))
                continue
            projectile.position = self.position + rel_pos + self.recoil_position

        if self.hp <= 0 and not self.destroyed:
            self.destroy()

        if self.destroyed:
            self.since_destroy += dt
        if self.since_destroy > 0.3:
            self.clean_up()

    def clean_up(self):
        if not self.silent:
            self.game.explosion_sound.play()
        self.game.enemies.remove(self)
        for projectile, rel_pos in self.stuck_projectiles:
            projectile.velocity = rel_pos * 40
            projectile.stuck = False
            projectile.gravity = True

        for i in range(40):
            self.game.particles.append(BoomParticle(self.position.get_position()))
        self.game.particles.append(BigBoom(self.position.get_position()))
        self.game.shake(amt=20)

        for i in range(int(self.reward / self.game.get_multiplier())):
            self.game.pickups.append(Battery(self.game, 1, self.position.get_position()))



    def destroy(self, silent=False):
        self.silent = silent
        self.destroyed = True
        self.since_destroy = 0


    def collides_with_projectile(self, projectile):
        pass


class Orb(Enemy):

    starting_hp = 1

    def __init__(self, game, position, direction):
        self.radius = 42
        super().__init__(game, position)

        self.direction = Pose(direction)
        reversed = self.direction.x < 0
        idle = SpriteSheet("images/enemy_closed.png", (1, 1), 1, xflip=reversed)
        opening = SpriteSheet("images/enemy_open.png", (5, 1), 5, xflip=reversed, repeat=False)
        open = SpriteSheet("images/enemy_opened.png", (1, 1), 1, xflip=reversed)
        closing = SpriteSheet("images/enemy_open.png", (5, 1), 5, xflip=reversed, reversed=True, repeat=False)
        self.sprite = Sprite(12)
        self.sprite.add_animation(
            {
                "idle": idle,
                "opening": opening,
                "open": open,
                "closing": closing,
            }
        )
        self.sprite.start_animation("idle")

        self.since_laser = 0
        self.since_lockon = 0
        self.locked_on = False
        self.cooldown = 2.5
        self.has_closed = False


    def get_target_position(self):
        y = self.game.player.position.y
        if y > c.GAME_HEIGHT * 0.7:
            y = c.GAME_HEIGHT * 0.7
        if self.direction.x > 0:
            return Pose((100, y))
        else:
            return Pose((c.GAME_WIDTH - 100, y))

    def update(self, dt, events):
        if self.game.rewinding:
            dt *= 0.1
        self.sprite.update(dt)
        diff = self.get_target_position() - self.position

        if diff.magnitude() >= 5 and not self.locked_on and not self.destroyed:
            if diff.magnitude() > 500:
                diff *= 500/diff.magnitude()
            self.position += diff*dt*2
        elif not self.locked_on and self.since_laser > self.cooldown:
            if self.direction.x > 0 and self.game.player.position.x > self.position.x and not self.destroyed:
                self.lock_on()
            elif self.direction.x < 0 and self.game.player.position.x < self.position.x and not self.destroyed:
                self.lock_on()

        self.since_laser += dt

        if self.locked_on and not self.destroyed:
            self.since_lockon += dt
            if self.since_lockon > 1 and self.since_laser > self.cooldown:
                self.fire_laser()
            if self.since_lockon > 2 and not self.has_closed:
                self.close_up()
            if self.since_lockon > 3:
                self.locked_on = False

        super().update(dt, events)



    def lock_on(self):
        self.game.laser_aim.play()
        self.locked_on = True
        self.since_lockon = 0
        self.sprite.start_animation("opening")
        self.has_closed = False
        self.game.particles.append(LaserGuide(self.position.get_position(), self.direction.get_position()))




    def fire_laser(self):
        self.since_laser = 0
        self.game.laser_sound.play()
        if self.direction.x > 0:
            self.velocity.x -= 1500
        else:
            self.velocity.x += 1500
        self.game.particles.append(Laser(self.position.get_position(), self.direction.get_position()))
        for i in range(50):
            self.game.particles.append(LaserBoomParticle(self.position.get_position(), direction=self.direction.get_position(), duration=1))

        player = self.game.player
        if (player.position.x - self.position.x) * self.direction.x > 0 and abs(player.position.y - self.position.y) < 80:
            player.get_hit_by_enemy(self)


    def close_up(self):
        self.sprite.start_animation("closing")
        self.has_closed = True

    def draw(self, surf, offset=(0, 0)):
        self.sprite.set_position((self.position + self.recoil_position + Pose(offset)).get_position())
        self.sprite.draw(surf)

    def destroy(self, silent=False):
        super().destroy(silent)
        self.sprite.start_animation("idle")

    def collides_with_projectile(self, projectile):
        if projectile.stuck or projectile.pickup:
            return False
        diff = projectile.position - self.position - self.recoil_position
        if diff.magnitude() < self.radius + 5:
            return True

    def clean_up(self):
        super().clean_up()

class Scuttle(Enemy):
    reward = 25

    def __init__(self, game, position, direction):
        super().__init__(game, position=position)
        self.radius = 50
        self.direction = Pose(direction)
        self.sprite = Sprite(12)
        if self.direction.x < 0:
            self.velocity = Pose((-800, 0))
            idle = SpriteSheet("images/scuttle_left.png", (8, 1), 8)
        else:
            self.velocity = Pose((800, 0))
            idle = SpriteSheet("images/scuttle_left.png", (8, 1), 8, reversed=True)
        self.sprite.add_animation({"idle": idle})
        self.sprite.start_animation("idle")

    def update(self, dt, events):
        if self.game.rewinding:
            dt *= 0.1
        super().update(dt, events)
        if not self.destroyed:
            if self.direction.x < 0:
                self.position += Pose((-400, 0))*dt
            else:
                self.position += Pose((400, 0))*dt
        self.position += self.velocity*dt
        self.sprite.update(dt)
        if self.recoil_position.y > 0:
            self.recoil_position.y = 0

    def draw(self, surf, offset=(0, 0)):
        self.sprite.set_position((self.position + self.recoil_position + Pose(offset)).get_position())
        self.sprite.draw(surf)

    def collides_with_projectile(self, projectile):
        if projectile.stuck or projectile.pickup:
            return False
        diff = projectile.position - self.position - self.recoil_position
        if diff.magnitude() < self.radius + 5:
            return True

    def destroy(self, silent=False):
        super().destroy(silent)
        self.velocity = Pose((0, 0))