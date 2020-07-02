import pygame
import neat
import time
import os
import random
from pygame.locals import *

pygame.font.init()
WIN_WIDTH = 400
WIN_HEIGHT = 700


BEAR_IMGS = [pygame.image.load(os.path.join("img","bear" + str(x) + ".png")) for x in range(1,7)]
BAR_IMG = pygame.image.load(os.path.join("img", "bar.png"))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg_0.png")), (500, 800))
STAT_FONT = pygame.font.SysFont("comicsan", 50)


class Bear:
    IMGS = BEAR_IMGS
    ANIMATION_TIME = 7

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel = 0
        self.acc = 1
        self.img_count = 0
        self.img = self.IMGS[0]

    def turn(self):
        self.acc = -self.acc

    def move(self):
        self.vel += self.acc
        self.x += self.vel


    def draw(self, win):
        self.img_count += 1

        if self.acc > 0:
            if self.img_count <= self.ANIMATION_TIME:
                self.img = self.IMGS[0]
            elif self.img_count <= self.ANIMATION_TIME*2:
                self.img = self.IMGS[1]
            elif self.img_count <= self.ANIMATION_TIME*3:
                self.img = self.IMGS[2]
            elif self.img_count <= self.ANIMATION_TIME*4:
                self.img = self.IMGS[1]
            elif self.img_count == self.ANIMATION_TIME*4 + 1:
                self.img = self.IMGS[0]
                self.img_count = 0
        else:
            if self.img_count <= self.ANIMATION_TIME:
                self.img = self.IMGS[3]
            elif self.img_count <= self.ANIMATION_TIME*2:
                self.img = self.IMGS[4]
            elif self.img_count <= self.ANIMATION_TIME*3:
                self.img = self.IMGS[5]
            elif self.img_count <= self.ANIMATION_TIME*4:
                self.img = self.IMGS[4]
            elif self.img_count == self.ANIMATION_TIME*4 + 1:
                self.img = self.IMGS[3]
                self.img_count = 0

        new_rect = self.img.get_rect(center = self.img.get_rect(topleft = (self.x, self.y)).center)
        win.blit(self.img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

class Bar:
    GAP = 200
    VEL = 5

    def __init__(self,x):
        self.x  = x
        self.width = 0
        self.left = 0
        self.right = 0
        self.BAR_RIGHT = BAR_IMG
        self.BAR_LEFT = BAR_IMG

        self.passed = False
        self.set_length()

    def set_length(self):
        self.length = random.randrange(-400, -200)
        self.left = self.length
        self.right = self.length + self.BAR_LEFT.get_width() + self.GAP

    def move(self):
        self.x += self.VEL

    def draw(self,win):
        win.blit(self.BAR_LEFT, (self.left, self.x))
        win.blit(self.BAR_RIGHT, (self.right, self.x))

    def collide(self, bear):
        bear_mask = bear.get_mask()
        left_mask = pygame.mask.from_surface(self.BAR_LEFT)
        right_mask = pygame.mask.from_surface(self.BAR_RIGHT)

        left_offset = ((self.length - round(bear.x)), self.x - bear.y)
        right_offset = (self.right - round(bear.x), self.x - bear.y)

        l_point = bear_mask.overlap(left_mask, left_offset)
        r_point = bear_mask.overlap(right_mask, right_offset)

        if l_point or r_point:
            return True

        return False 

def draw_window(win, bear, bars, score ):
    win.blit(BG_IMG, (0,0))

    for bar in bars:
        bar.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    bear.draw(win)


    pygame.display.update()

def start():
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    bear = Bear(150,450)
    end_it=False
    while (end_it==False):
        win.blit(BG_IMG, (0,0))
        bear.draw(win)
        myfont=pygame.font.SysFont("Britannic Bold", 50)
        nlabel=myfont.render("Start Screen", 1, (255, 255, 255))
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                break
            if (event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)):
                end_it=True
                
        win.blit(nlabel,(100,200))
        pygame.display.flip()

def main():
    bear = Bear(150,450)
    score = 0
    bars = [Bar(0)]
    
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()
    start() 
    run = True
    while run:
        
        bear.move()
        clock.tick(30)
        add_bar = False
        rem = []
        for bar in bars:
            bar.move()
            if bar.collide(bear):
                   break

            if not bar.passed and bar.x - bar.BAR_LEFT.get_height() > bear.y:
                bar.passed = True
                add_bar = True

            if bar.x > WIN_HEIGHT + 40:
                rem.append(bar)

            if bear.x + bear.img.get_width() - 36 > WIN_WIDTH or bear.x  < -bear.img.get_width() + 36: 
                pygame.quit()  

        if add_bar:
            score += 1
            bars.append(Bar(-30))

        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                break
            if (event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP)):
                bear.turn()



        for r in rem:
            bars.remove(r)

                

        draw_window(win, bear, bars, score)
    
    

main()