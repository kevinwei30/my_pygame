# encoding: utf-8

import random
import copy

class Orb(object):
    def __init__(self, pygame, canvas, name, rect):
        self.pygame = pygame
        self.canvas = canvas
        self.name = name
        self.rect = rect
        self.color = (255, 255, 255)
        self.pos = 1
        self.visible = True
        
    def move_right(self):
        if self.pos != 2:
            self.rect[0] += 100
            self.pos += 1

    def move_left(self):
        if self.pos != 0:
            self.rect[0] -= 100
            self.pos -= 1

    def update(self):
        if self.visible:
            # self.pygame.draw.rect(self.canvas, self.color, self.rect)
            orb_img = self.pygame.image.load('images/orb_small.png').convert_alpha()
            self.canvas.blit(orb_img, self.rect)

class Dinasour(object):
    def __init__(self, pygame, canvas, d_id, rect):
        self.pygame = pygame
        self.canvas = canvas
        self.id = str(d_id)
        self.name = 'dinasour' + self.id
        self.init_rect = copy.copy(rect)
        self.rect = rect
        self.path = d_id % 3
        # self.color = tuple([random.randint(100, 200) for i in range(3)])
        self.active = False
        self.visible = False
        self.type = random.randint(1, 3)
        self.init_v = [0, 5, 8, 10][self.type]

    def go(self):
        self.active = True
        self.visible = True

    def move_down(self, dy, h):
        self.rect[1] += self.init_v + dy
        run_away = self.rect[1] >= h
        if run_away:
            self.reset()
        return run_away

    def reset(self):
        self.active = False
        self.visible = False
        self.rect = copy.copy(self.init_rect)

    def update(self):
        if self.visible:
            # self.pygame.draw.rect(self.canvas, self.color, self.rect)
            dinasour_img = self.pygame.image.load('images/dinasour_' + str(self.type) + '_small.png').convert_alpha()
            self.canvas.blit(dinasour_img, self.rect)
