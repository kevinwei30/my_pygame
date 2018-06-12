# encoding: utf-8

import os, sys, random
import pygame
import random
from pygame.locals import *
from mydrew import *

canvas_width = 300
canvas_height = 600

block = (0, 0, 0)
dinasour_list = []
active_list = dict()
dy = 0
game_mode = 0
score = 0
last_score = 0
max_score = 0

pygame.init()
pygame.display.set_caption(u'恐龍大逃亡')
canvas = pygame.display.set_mode((canvas_width, canvas_height))
clock = pygame.time.Clock()

font = pygame.font.Font('font/HanaMinA.ttf', 18)
bg_img = pygame.image.load('images/volcano.jpg').convert_alpha()

orb_x = 110
orb_y = canvas_height - 90
orb = Orb(pygame, canvas, 'orb', [orb_x, orb_y, 80, 80])

class GameState:
	def __init__(self):
		self.actions = ['no_op', 'go_left', 'go_right']
		resetGame()

	def frame_step(self, input_action):
		global game_mode, dinasour_list, dy, active_list, score, last_score, max_score
		# print(len(dinasour_list))
		game_mode = 1
		pygame.event.pump()

		reward = 0.01
		terminal = False

		if sum(input_action) != 1:
			raise ValueError('Invalid input actions!')

		if input_action[1] == 1:
			orb.move_left()
		elif input_action[2] == 1:
			orb.move_right()

		canvas.fill(block)
		# canvas.blit(bg_img, [0, 0])

		for d_id, dinasour in active_list.items():
			if isCollision(orb.rect, dinasour.rect):
				terminal = True
				reward = -1
				resetGame()
				break

		orb.update()

		showFont(u'上一輪分數: ' + str(last_score), 0, 0)
		showFont(u'最高分數: ' + str(max_score), 0, 25)
		if game_mode == 0:
			showFont(u'請按SPACE開始遊戲', 70, 100)
		elif game_mode == 1:
			showFont(u'現在分數: ' + str(score), 180, 20, 'white')

		if game_mode == 1:
			new_dinasour = 0
			pop_ids = []
			for d_id, dinasour in active_list.items():
				run_away = dinasour.move_down(dy, canvas_height)
				if run_away == True:
					pop_ids.append(d_id)
					new_dinasour += 1
				dinasour.update()
			
			for i in pop_ids:
				active_list.pop(i)

			for i in range(new_dinasour):
				tmp_path = active_list[list(active_list.keys())[0]].path if bool(active_list) else 0
				while True:
					rand = random.randint(0, 20)
					if dinasour_list[rand].active == False and dinasour_list[rand].path != tmp_path:
						dinasour_list[rand].go()
						active_list[str(rand)] = dinasour_list[rand]
						score += 1
						reward = 1
						if score % 10 == 0:
							dy += 2
						break

		image_data = pygame.surfarray.array3d(pygame.display.get_surface())
		pygame.display.update()
		clock.tick(40)

		return image_data, reward, terminal

def showFont(text, x, y, color='black'):
	global canvas
	if color == 'black':
		text = font.render(text, 1, (0, 0, 0))
	elif color == 'white':
		text = font.render(text, 1, (255, 255, 255))
	canvas.blit(text, (x, y))

def isCollision(obj1Rect, obj2Rect):
	if (obj1Rect[0] >= obj2Rect[0] and obj1Rect[0] <= obj2Rect[0] + obj2Rect[2]) \
		or (obj2Rect[0] >= obj1Rect[0] and obj2Rect[0] <= obj1Rect[0] + obj1Rect[2]):
		if (obj1Rect[1] >= obj2Rect[1] and obj1Rect[1] <= obj2Rect[1] + obj2Rect[3]) \
			or (obj2Rect[1] >= obj1Rect[1] and obj2Rect[1] <= obj1Rect[1] + obj1Rect[3]):
			return True
	return False

def resetGame():
	global game_mode, dinasour_list, dy, active_list, score, last_score, max_score

	dinasour_list.clear()
	tmp_x = [10, 110, 210]
	tmp_y = [-80 * i + 10 for i in range(5)]
	dinasour_w = 80
	dinasour_h = 80
	for i in range(21):
		dinasour_x = tmp_x[i % 3]
		dinasour_y = tmp_y[random.randint(0, 2)]
		dinasour_list.append(Dinasour(pygame, canvas, i,
							[dinasour_x, dinasour_y, dinasour_w, dinasour_h]))

	game_mode = 1
	active_list.clear()
	dy = 0
	last_score = score
	score = 0
	if last_score > max_score:
		max_score = last_score

	for dinasour in dinasour_list[:2]:
		dinasour.go()
		active_list[dinasour.id] = dinasour
