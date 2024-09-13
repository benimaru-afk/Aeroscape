# Classes for Aeroscape Game
import pygame
import random
import functions as f
import math

pygame.init()

GROUND = 620
KB = 20
GRAV = .25
JUMP = -20
STARTY = 1200
font = pygame.font.Font("pixelated/pixelated.ttf", 40)


class Animation:
    def __init__(self, image_list, delay, screen):
        self.image_list = image_list
        self.screen = screen
        self.frame = 0
        self.delay = delay
        self.draw_counter = 0

    def draw(self, rect):
        self.screen.blit(self.image_list[self.frame], rect)
        self.draw_counter += 1
        if self.draw_counter > self.delay:
            self.frame += 1
            self.draw_counter = 0
            if self.frame >= len(self.image_list):
                self.frame = 0
                return True
        return False


class HealthBar:
    def __init__(self, screen, x, y, width, height, color_back, color_front):
        self.screen = screen
        self.rect_bg = pygame.Rect(x, y, width, height)
        self.rect_front = pygame.Rect(x + 5, y + 5, width - 10, height - 10)
        self.max_width = self.rect_front.width
        self.color_back = color_back
        self.color_front = color_front

    def draw(self, variable, max):
        self.rect_front.width = (variable / max) * self.max_width
        pygame.draw.rect(self.screen, self.color_back, self.rect_bg)
        pygame.draw.rect(self.screen, self.color_front, self.rect_front)


class Reviver:
    def __init__(self, screen):
        self.screen = screen
        self.delay_base = 150
        self.delay = self.delay_base

    def revive(self, alive):
        self.delay -= 1
        if self.delay <= 0:
            self.delay = self.delay_base
            for e in alive[0]:
                if e.name == "Necromancer":
                    if e.dancing == 0:
                        undead = Enemy(self.screen, "Skeleton")
                        alive[0].append(undead)


class Explosion:
    def __init__(self, screen, x, y):
        self.anim = Animation(f.stripFromSheet("img/explosion_sheet.png", 5, 5, 1), 5, screen)
        self.rect = self.anim.image_list[0].get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self):
        return self.anim.draw(self.rect)


class GroupGenerator:
    def __init__(self, screen, type, per_group_min, per_group_max, group_count, delay_min, delay_max):
        self.screen = screen
        self.type = type
        self.per_group_min = per_group_min
        self.per_group_max = per_group_max
        self.group_count = group_count
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.delay = random.randint(delay_min, delay_max)

    def update(self, groupgen_list, enemy_list):
        if self.delay > 0:
            self.delay -= 1
        else:
            group_size = random.randint(self.per_group_min, self.per_group_max)
            for i in range(group_size):
                enemy_list.append(Enemy(self.screen, self.type))

            self.group_count -= 1
            if self.group_count == 0:
                groupgen_list.remove(self)
            else:
                self.delay = random.randint(self.delay_min, self.delay_max)


class Hero:
    def __init__(self, screen, name):
        self.screen = screen

        self.can_dash = True

        self.name = name
        if self.name == "Fighter":
            self.speed = 10
            self.max_hp = 10
            self.max_special_charge = 1
            self.idle_anim_right = Animation(f.stripFromSheet('img/fighter/spear_idle_right.png', 5, 2, 1), 5, screen)
            self.idle_anim_left = Animation(f.stripFromSheet('img/fighter/spear_idle_left.png', 5, 2, 1), 5, screen)
            self.run_left_anim = Animation(f.stripFromSheet('img/fighter/spear_run_left.png', 5, 4, 1), 5, screen)
            self.run_right_anim = Animation(f.stripFromSheet('img/fighter/spear_run_right.png', 5, 4, 1), 5, screen)
            self.attack_img = f.resize(pygame.image.load('img/fighter/spear_attack.png'), 5)
            self.attack_delay_base = 30
            self.special_delay_base = 150
            self.x = 100
            self.y = 300
        elif self.name == "Bard":
            self.speed = 10
            self.max_hp = 10
            self.max_special_charge = 1
            self.idle_anim_right = Animation(f.stripFromSheet('img/bard/bard_idle_right.png', 5, 2, 1), 5, screen)
            self.idle_anim_left = Animation(f.stripFromSheet('img/bard/bard_idle_left.png', 5, 2, 1), 5, screen)
            self.run_left_anim = Animation(f.stripFromSheet('img/bard/bard_run_left.png', 5, 4, 1), 5, screen)
            self.run_right_anim = Animation(f.stripFromSheet('img/bard/bard_run_right.png', 5, 4, 1), 5, screen)
            self.attack_img = f.resize(pygame.image.load('img/bard/note_attack.png'), 1)
            self.attack_delay_base = 45
            self.special_delay_base = 300
            self.x = 225
            self.y = 300

        self.attack_bar = HealthBar(self.screen, 0, 750, 200, 30, (0, 0, 0), (255, 255, 255))
        self.special_bar = HealthBar(self.screen, 1300, 750, 200, 30, (0, 0, 0), (255, 255, 255))
        self.health_bar = HealthBar(self.screen, 0, 0, 200, 30, (255, 0, 0), (0, 255, 0))

        self.anim = self.idle_anim_left

        self.alive = True
        self.direction = 0
        self.dx, self.dy = 0, 0
        self.gravity = 0
        self.hp = self.max_hp
        self.special_charge = self.max_special_charge
        self.rect = self.anim.image_list[0].get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.on_ground = False
        self.attack_hitbox = pygame.Rect(80, 16, -100, -100)
        self.attacking = False
        self.attack_duration = 0
        self.attacks = []
        self.attack_delay = self.attack_delay_base
        self.special_delay = self.special_delay_base
        self.takingdamage = 0
        self.dmgimg = f.resize(pygame.image.load('img/ouch.png'), 5)

    def takeDamage(self, damage, direction, kb):
        if self.takingdamage <= 0:
            self.hp -= damage
            self.takingdamage = 30

    def resetAnim(self):
        if self.direction >= 0:
            self.anim = self.idle_anim_right
        elif self.direction == -1:
            self.anim = self.idle_anim_left

    def draw(self):
        # if we want to switch to a different animation, like a fight animation, we can simply set
        # self.anim = self.fight_anim. Once it goes through the animation one time fully, it will return to the
        # idle_anim, or whichever other anim you rewrite it to use.
        if self.anim.draw(self.rect):
            self.resetAnim()
        for attack in self.attacks:
            attack.draw()
        # draw red overlay when taking damage
        if self.takingdamage > 0:
            self.takingdamage -= 1
            if self.takingdamage > 20:
                self.screen.blit(self.dmgimg, self.rect)

        self.attack_bar.draw(self.attack_delay_base - self.attack_delay, self.attack_delay_base)
        self.special_bar.draw(self.special_delay_base - self.special_delay, self.special_delay_base)
        self.health_bar.draw(self.hp, self.max_hp)
        self.screen.blit(font.render(str(f"x{self.special_charge}"), False, (255, 255, 255)), (1250, 740))

    def attack(self):
        if not self.attacking:
            if self.name == "Bard" or self.name == "Fighter":
                if self.direction >= 0:
                    x = self.x + self.rect.width
                elif self.direction == -1:
                    x = self.x - 80
                self.attacks.append(
                    MeleeAttack(self.screen, self.direction, 15, 1, self.attack_img, x, self.y + 32))
                self.attacking = True
                self.attack_duration = 15
                self.attack_delay = self.attack_delay_base

    def special(self, targets):
        if not self.attacking:
            if self.name == "Fighter":
                if self.direction >= 0:
                    x = self.x + self.rect.width
                elif self.direction == -1:
                    x = self.x - 80
                self.attacks.append(RangedAttack(self.screen, self.direction, 15, 1, self.attack_img, x, self.y, 25, 0))
                self.special_charge -= 1
            elif self.name == "Bard":
                pos = pygame.mouse.get_pos()
                for t in targets:
                    if t.rect.collidepoint(pos):
                        self.special_charge -= 1
                        t.dancing = 120

    def update(self, motion, jump, attack, special, dash, targets):
        if not self.attacking:
            if self.dx == 0:
                self.move(motion, jump)
            else:
                self.move(0, jump)
            # update gravity and deltas
            if self.rect.bottom < GROUND:
                self.gravity += GRAV
                self.on_ground = False
                self.can_dash = True

            if self.dx < 0:
                self.dx += 1
            elif self.dx > 0:
                self.dx -= 1
            else:
                self.dx = 0
            self.dy += self.gravity
            self.x += self.dx
            self.y += self.dy

            if self.y + self.rect.height > GROUND:
                self.y = GROUND - self.rect.height
                self.gravity = 0
                self.dy = 0
                self.on_ground = True

        if dash and self.dx == 0 and self.can_dash:
            self.dx = self.direction * 20
        if abs(self.dx) <= 5:
            self.dx = 0

        # update animations
        if self.direction == 0:
            self.resetAnim()
        elif self.direction == 1:
            self.anim = self.run_right_anim
        elif self.direction == -1:
            self.anim = self.run_left_anim

        # don't be offscreen left or right. thanks.
        if self.x < 0:
            self.x = 0
        elif self.x + self.rect.width > 1500:
            self.x = 1500 - self.rect.width

        self.rect.x, self.rect.y = self.x, self.y

        # update attacks
        if self.attack_delay > 0:
            self.attack_delay -= 1
        if attack:
            self.attack()

        if self.special_delay > 0 and self.special_charge < self.max_special_charge:
            self.special_delay -= 1
        if self.special_delay <= 0 and self.special_charge < self.max_special_charge:
            self.special_charge += 1
            self.special_delay = self.special_delay_base

        if special and self.special_charge > 0:
            self.special(targets)

        for i in reversed(range(len(self.attacks))):
            if self.attacks[i].update(targets):
                self.attacks.pop(i)
        if len(self.attacks) == 0:
            self.attacking = False

        if self.hp <= 0:
            self.die()

    def move(self, direction, jump):
        # remember most recent movement
        if direction != 0:
            self.direction = direction
        # normal movement
        if self.direction == 1:
            self.x += self.speed
        elif self.direction == -1:
            self.x -= self.speed

        # jump movement
        if jump and self.on_ground:
            self.dy = JUMP

    def die(self):
        self.alive = False


class Enemy:
    def __init__(self, screen, name):
        self.screen = screen
        self.random_counter = 0 # idk bro i need more counters i dont actually i could have done this all any other way and it would've been so much better but i didn't and now we're here

        # initialize variables that arent used for all enemy types
        self.attack_delay_base = 0
        self.attack_img = False
        self.attack_dur = 0
        self.special_delay_base = 0

        # Initialize specific game variables based on name arg
        self.name = name
        if self.name == "Goblin":
            self.hp = 1
            self.strength = 3
            self.start_potions = 0
            self.idle_anim = Animation(f.stripFromSheet('img/enemy/goblin-run-sheet.png', 5, 4, 1), 5, screen)
            self.x, self.y = random.randint(50, 750), STARTY
            self.hitbox = self.idle_anim.image_list[0].get_rect()
            self.attack_img = f.resize(pygame.image.load('img/fighter/spear_attack.png'), 5)
            self.hitbox.width -= 32
            self.hitbox.x += 16
            self.speed = 5
            self.damage = 1
            # add self.fight_anim and any other animations you want, like running or jumping.
        elif self.name == "Skeleton":
            self.hp = 1
            self.idle_anim = Animation(f.stripFromSheet('img/enemy/skeleton.png', 5, 1, 1), 5, screen)
            self.x, self.y = random.randint(50, 1450), STARTY
            self.hitbox = self.idle_anim.image_list[0].get_rect()
            self.attack_img = f.resize(pygame.image.load('img/fighter/spear_attack.png'), 5)
            self.hitbox.width -= 32
            self.hitbox.x += 16
            self.speed = 5
            self.damage = 1
        elif self.name == "Strong Goblin":
            self.hp = 2
            self.strength = 5
            self.start_potions = 0
            self.idle_anim = Animation(f.stripFromSheet('img/enemy/strong_goblin.png', 5, 1, 1), 5, screen)
            self.x, self.y = random.randint(50, 1450), STARTY
            self.hitbox = self.idle_anim.image_list[0].get_rect()
            self.hitbox.width -= 32
            self.hitbox.x += 16
            self.attack_delay_base = 120
            self.attack_img = f.resize(pygame.image.load('img/enemy/slam_attack.png'), 5)
            self.speed = 2.5
            self.attack_dur = 60
            self.damage = 1
        elif self.name == "Necromancer":
            self.hp = 3
            self.strength = 3
            self.start_potions = 2
            self.idle_anim = Animation(f.stripFromSheet('img/enemy/necromancer.png', 5, 1, 1), 5, screen)
            self.x, self.y = random.randint(50, 1450), 1000
            self.hitbox = self.idle_anim.image_list[0].get_rect()
            self.hitbox.width -= 32
            self.hitbox.x += 16
            self.attack_delay_base = 120
            self.special_delay_base = 300
            self.attack_img = f.resize(pygame.image.load('img/enemy/necro_ball.png'), 5)
            self.speed = 5
            self.damage = 1
            self.attack_dur = 60
        elif self.name == "Dragon":
            self.max_hp = 45
            self.strength = 15
            self.start_potions = 0
            self.idle_anim = Animation(f.stripFromSheet('img/enemy/goblin-run-sheet.png', 10, 3, 1), 5, screen)
            self.x, self.y = random.randint(50, 750), 200

        self.alive = True
        self.ignores_gravity = False
        self.attack_delay = random.randint(0, self.attack_delay_base)
        self.special_delay = self.special_delay_base
        self.speed_mod = 1
        self.attacks = []
        self.anim = self.idle_anim
        self.dx, self.dy = 0, 0
        self.gravity = 0
        self.rect = self.anim.image_list[0].get_rect()
        self.rect.x, self.rect.y = self.x, self.y
        self.takingdamage = 0
        self.dmgimg = f.resize(pygame.image.load('img/ouch.png'), 5)
        self.direction = 1
        self.attacking = False
        self.another_boolean = False
        self.flying = False
        self.emerging = True
        self.dancing = 0

        self.motion_length = random.randint(15, 90)

    def takeDamage(self, damage, direction, kb):
        if self.dx == 0 and self.takingdamage <= 0:
            self.hp -= damage
            self.takingdamage = 15
            if self.name == "Necromancer":
                self.y -= 150
                self.ignores_gravity = True
            if kb:
                self.dx = KB * direction

    def draw(self):
        # if we want to switch to a different animation, like a fight animation, we can simply set
        # self.anim = self.fight_anim. Once it goes through the animation one time fully, it will return to the
        # idle_anim, or whichever other anim you rewrite it to use.
        if self.anim.draw(self.rect):
            self.anim = self.idle_anim
        if self.takingdamage > 0:
            self.takingdamage -= 1
            self.screen.blit(self.dmgimg, self.rect)

        for attack in self.attacks:
            attack.draw()

    def move(self, direction):
        # normal movement
        """
        if not self.attacking and self.dx == 0:
            if direction == 1:
                self.x += self.speed
            elif direction == -1:
                self.x -= self.speed
        """

        if not self.attacking and self.dx == 0:
            if self.motion_length > 0:
                self.motion_length -= 1
                self.x += self.speed * direction * self.speed_mod
            else:
                self.motion_length = random.randint(15, 60)
                self.speed_mod = random.randint(1, 3)/2

        # remember most recent movement
        if direction != 0 and self.random_counter <= 0:
            self.direction = direction

    def attack(self, target):
        if self.name == "Strong Goblin":
            if self.dy == 0:
                self.dy = - 10
            elif self.dy > 5:
                self.attacks.append(MeleeAttack(self.screen, -1, self.attack_dur, self.damage, self.attack_img,
                                                self.x - self.rect.width, self.y+32))
                self.attacks.append(MeleeAttack(self.screen, 1, self.attack_dur, self.damage, self.attack_img,
                                                self.x + self.rect.width, self.y+32))
                self.attack_delay = self.attack_delay_base

        elif self.name == "Necromancer":
            if len(self.attacks) < 3:
                scalar = math.sqrt((target.x - self.x) ** 2 + (target.y - self.y) ** 2) / 10
                dx = (target.x - self.x) / scalar
                dy = (target.y - self.y) / scalar
                self.attacks.append(RangedAttack(self.screen, self.direction, self.attack_dur, self.damage
                                                 , self.attack_img, self.x, self.y, dx, dy))
                self.attack_delay = 10
            else:
                self.attack_delay = self.attack_delay_base
                self.ignores_gravity = False

        self.attacking = True

    def runAI(self, target):
        if self.name == "Goblin" or self.name == "Skeleton":
            attack = False
            jump = False
            if self.x > target.x + 60:
                direction = -1
            elif self.x < target.x - 60:
                direction = 1
            else:
                direction = 0
        elif self.name == "Strong Goblin":
            attack = True
            jump = False
            if self.x > target.x + 60:
                direction = -1
            elif self.x < target.x - 60:
                direction = 1
            else:
                direction = 0
        elif self.name == "Necromancer":
            attack = True
            jump = False
            direction = 0

            if self.special_delay > 0:
                self.special_delay -= 1
            else:
                self.special_delay = self.special_delay_base

        return direction, attack, jump

    def update(self, target):
        direction, attack, jump = self.runAI(target)

        # decrease dancing timer
        if self.dancing > 0:
            self.dancing -= 1

        # dont take knockback if mid-attack
        if self.attacking:
            self.dx = 0

        # move based on AI directives unless suppressed
        if not self.dancing and not self.emerging:
            self.move(direction)

        # if still emerging from the ground, emerge from the ground. god i hate everything.
        if self.emerging:
            attack = False
            self.dy = -5
            if self.y + self.rect.height <= GROUND:
                self.emerging = False
        # get affected by gravity
        if not self.ignores_gravity:
            if self.rect.bottom < GROUND:
                self.gravity += GRAV
                self.dy += self.gravity

        # reduce kb. "friction"
        if self.dx < 0:
            self.dx += 1
        elif self.dx > 0:
            self.dx -= 1
        else:
            self.dx = 0

        # update x, y based on dx, dy
        self.x += self.dx
        self.y += self.dy

        # after updating position, make sure that enemy is not below the GROUND.
        if not self.emerging and self.y + self.rect.height > GROUND:
            self.y = GROUND - self.rect.height
            self.gravity = 0
            self.dy = 0

        # don't be offscreen left or right. thanks.
        if self.x < 0:
            self.x = 0
        elif self.x + self.rect.width > 1500:
            self.x = 1500 - self.rect.width

        # update rect position
        self.rect.x, self.rect.y = self.x, self.y

        # update hitbox position
        self.hitbox.center = self.rect.center

        # damage player if player is touching enemy
        if self.hitbox.colliderect(target.rect):
            target.takeDamage(self.damage, self.direction, True)

        # unless supressed by bard, update atk delay and atk if possible.
        if self.dancing == 0 and not self.emerging:
            if self.attack_delay > 0:
                self.attack_delay -= 1
            if attack and self.attack_delay <= 0:
                self.attack(target)

        # update atks, remove atk from list if return is True (will be True if atk duration runs out)
        for i in reversed(range(len(self.attacks))):
            if self.attacks[i].update([target]):
                self.attacks.pop(i)
        if len(self.attacks) == 0:
            self.attacking = False

        # die
        if self.hp <= 0:
            self.die()

    def die(self):
        self.alive = False


class MeleeAttack:
    def __init__(self, screen, direction, duration, damage, image, x, y):
        self.screen = screen
        self.direction = direction
        self.duration = duration
        self.image = image
        self.damage = damage
        self.x = x
        self.y = y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, targets):
        for i in reversed(range(len(targets))):
            if self.rect.colliderect(targets[i].rect):
                targets[i].takeDamage(self.damage, self.direction, True)
                targets.pop(i)
        self.duration -= 1
        if self.duration <= 0:
            return True

    def draw(self):
        self.screen.blit(self.image, self.rect)


class RangedAttack(MeleeAttack):
    def __init__(self, screen, direction, duration, damage, image, x, y, dx, dy):
        super().__init__(screen, direction, duration, damage, image, x, y)
        self.dx = dx * direction
        self.dy = dy

    def move(self):
        self.x += self.dx
        self.y += self.dy
        self.rect.x, self.rect.y = self.x, self.y
        if self.rect.right < 0 or self.rect.left > 1500 or self.rect.top > 780 or self.rect.bottom < 0:
            return True
        return False

    def update(self, targets):
        if self.move() and self.duration <= 0:
            return True

        self.duration -= 1

        for i in reversed(range(len(targets))):
            if self.rect.colliderect(targets[i].rect):
                targets[i].takeDamage(self.damage, self.direction, False)
                targets.pop(i)
                return True
