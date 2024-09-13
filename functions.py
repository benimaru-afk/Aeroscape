# Functions for Aeroscape Game
import pygame

pygame.init()


def stripFromSheet(image_dir, scaling, num_x, num_y):  # strips images from a spritesheet, resizes them, and returns them in a list
    image = resize(pygame.image.load(image_dir), scaling)
    rect = image.get_rect()
    height = rect.height / num_y
    width = rect.width / num_x
    sheet = []
    for j in range(num_y):
        for i in range(num_x):
            sheet.append(image.subsurface(i * width, j * height, width, height))
    return sheet


def resize(image, scaling):  # shrinks or stretches an image and returns it
    rect = image.get_rect()
    dimensions = (int(rect.width * scaling), int(rect.height * scaling))
    return pygame.transform.scale(image, dimensions)


