# Aeroscape
import pygame
import math
import random
import classes as c
import functions as f

pygame.init()

# game window
bottom_pannel = 150
screen_width = 1500
screen_height = 780

# basic variables
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
fps = 30
font = pygame.font.Font("pixelated/pixelated.ttf", 40)

# load images
# background image
background_image = pygame.image.load('img/background.png')
ground_image = pygame.image.load('img/dirt_ground.png')

# resizing stuff
background_image = f.resize(background_image, 1)
ground_image = f.resize(ground_image, 5)

'''game loop functions / level etc. - maybe etsevan or sam idk'''


def handleEvents():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def levels(key, level):
    # level = 0 #defaults to level 0, you'll have to change this for each level.
    # key = ["Goblin", "Glizzy Goblin", "Necromancer"] # add one for each enemy type

    f = open("levels.txt", "r")
    lines = f.readlines()
    f.close()

    enemies = []

    for i in range(len(lines)):
        if "level " + str(level) in lines[i]:
            # print("found level")
            for j in range(1, 4):
                temp = []
                for letter in lines[i + j]:
                    if letter != "\n":
                        temp.append(c.Enemy(screen, key[int(letter)]))
                enemies.append(temp)
            break
    return enemies


def levels2(key, level):
    f = open("levels.txt", 'r')
    lines = f.readlines()
    f.close()

    groups = []

    for i in range(len(lines)):
        if "level " + str(level) in lines[i]:
            print("found level")
            for j in range(5):
                target_line = lines[i+j]
                if target_line != "Ignore\n":
                    target_line = target_line.split(",")
                    target_line[-1] = target_line[-1][:-1] # remove \n from end of line
                    for i in range(target_line):
                        target_line[i] = int(target_line[i])
                    type = key[target_line[0]]
                    per_group_min = target_line[1]
                    per_group_max = target_line[2]
                    group_count = target_line[3]
                    delay_min = target_line[4]
                    delay_max = target_line[5]
                    group = c.GroupGenerator(screen, type, per_group_min, per_group_max, group_count, delay_min, delay_max)
                    groups.append(group)

    return groups


def revive(dead):
    if len(dead) > 0:
        target = random.choice(dead)
        undead = c.Enemy(screen, "Skeleton")
        undead.rect.center = target.rect.center
        return undead


def levelDisplay(level, enemies):
    count = 0
    for i in range(len(enemies)):
        count += len(enemies[i])

    screen.blit(font.render(f"Level: {level} Enemies Remaining: {count}", False, (255, 255, 255)), (500, 0))


def handleKeyboardInput():
    keys = pygame.key.get_pressed()
    mouse = pygame.mouse.get_pressed()
    motion = 0
    jump = False
    attack = False
    special = False
    dash = False
    if keys[pygame.K_d]:
        motion += 1
    if keys[pygame.K_a]:
        motion += -1
    if keys[pygame.K_SPACE]:
        jump = True
    if mouse[0]:
        attack = True
    if mouse[2]:
        special = True
    if keys[pygame.K_LSHIFT]:
        dash = True
    return motion, jump, attack, special, dash


def gameOverLoop(explosion):
    draw_exp = True
    while True:
        handleEvents()
        screen.fill((0, 0, 0))
        if draw_exp:
            draw_exp = not explosion.draw()
        else:
            screen.blit(font.render(f"GAME OVER. YOU MADE IT TO LEVEL {lvl}", False, (255, 255, 255)), (500, 200))
        pygame.display.flip()
        clock.tick(fps)


def chooseCharacterLoop():
    chosen = False
    spear_anim = c.Animation(f.stripFromSheet("img/fighter/spear_idle_right.png", 5, 2, 1), 5, screen)
    spear_rect = pygame.Rect(100, 100, 80, 80)
    bard_anim = c.Animation(f.stripFromSheet("img/bard/bard_idle_right.png", 5, 2, 1), 5, screen)
    bard_rect = pygame.Rect(screen_width - 180, 100, 80, 80)
    while not chosen:
        handleEvents()
        screen.fill((0, 0, 0))
        spear_anim.draw(spear_rect)
        bard_anim.draw(bard_rect)

        pos = pygame.mouse.get_pos()
        if pygame.mouse.get_pressed()[0]:
            if spear_rect.collidepoint(pos):
                return "Fighter"
            elif bard_rect.collidepoint(pos):
                return "Bard"

        pygame.display.flip()
        clock.tick(fps)


key = ["Skeleton", "Goblin", "Strong Goblin", "Necromancer", "Dragon", "King Goblin"]
reviver = c.Reviver(screen)
enemies = [[]]
explosions = []

lvl = 0
hero_motion = 0


fighter = c.Hero(screen, chooseCharacterLoop())

''' loop '''
run = True
while run:
    handleEvents()

    # get arguments for fighter.update based on keyboard input
    hero_motion, jump, attack, special, dash = handleKeyboardInput()

    # move waves if necessary, move levels if necessary
    if len(enemies[0]) == 0:  # if no more enemies in this wave, pop this first list, moves on to next wave
        enemies.pop(0)
        if len(enemies) == 0:  # if no more waves in this level, get the enemies for the next level using levels()
            lvl += 1
            enemies = levels(key, lvl)
            fighter.hp = fighter.max_hp

    # update enemies and enemies list
    for i in reversed(range(len(enemies[0]))):
        if enemies[0][i].alive:
            enemies[0][i].update(fighter)
        else:
            explosions.append(c.Explosion(screen, enemies[0][i].x, enemies[0][i].y))
            enemies[0].pop(i)

    reviver.revive(enemies)

    # update fighter
    if fighter.alive:
        fighter.update(hero_motion, jump, attack, special, dash, list(enemies[0]))
    else:
        gameOverLoop(c.Explosion(screen, fighter.x, fighter.y))

    # draw bg
    screen.fill((0, 0, 0))
    screen.blit(background_image, (0, 0))
    screen.blit(ground_image, (0, c.GROUND))

    # draw explosions
    for i in reversed(range(len(explosions))):
        if explosions[i].draw():
            explosions.pop(i)

    # draw enemies
    for enemy in enemies[0]:
        enemy.draw()

    # draw the hero
    fighter.draw()

    # display level and enemy counter
    levelDisplay(lvl, enemies)

    # update display and tick for fps
    pygame.display.update()
    clock.tick(fps)

pygame.quit()
