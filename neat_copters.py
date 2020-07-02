import pygame
import neat
import time
import os
import random

pygame.font.init()
WIN_WIDTH = 400
WIN_HEIGHT = 700

GEN = 0

BEAR_IMGS = [pygame.image.load(os.path.join("img","bear" + str(x) + ".png")) for x in range(1,7)]
BAR_IMG = pygame.image.load(os.path.join("img", "bar.png"))
BG_IMG = pygame.transform.scale(pygame.image.load(os.path.join("img", "bg_0.png")), (400, 700))
STAT_FONT = pygame.font.SysFont("comicsan", 50)
win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT)) #display screen

class Bear:
    IMGS = BEAR_IMGS
    ANIMATION_TIME = 5

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

    def collide(self, bear, win):
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

def draw_window(win, bears, bars, score, gen):
    win.blit(BG_IMG, (0,0))

    for bar in bars:
        bar.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, (255,255,255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("GEN: " + str(gen), 1, (255,255,255))
    win.blit(text, (10 , 10))

    score_label = STAT_FONT.render("Alive: " + str(len(bears)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    for bear in bears:
        bear.draw(win)


    pygame.display.update()

def main(genomes, config):
    global GEN
    GEN += 1 
    nets = []
    ge = []
    bears = []

    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        bears.append(Bear(150,450))
        ge.append(genome)

    score = 0
    bars = [Bar(0)]
    clock = pygame.time.Clock()

    run = True
    while run and len(bears) > 0:
        clock.tick(200) #Speed of game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        bar_ind = 0
        if len(bears) > 0:
            if len(bars) > 1 and bears[0].y < bars[0].x + bars[0].BAR_LEFT.get_height(): #what bar to use
                bar_ind = 1

        for x, bear in enumerate(bears): # add fitness to encourage bear to live
            ge[x].fitness += 0.1
            bear.move()

            output = nets[bears.index(bear)].activate((abs(bear.x - (bars[bar_ind].right - 100)), #inputs middle of the gap of the bar
                abs(bars[bar_ind].x + bars[bar_ind].BAR_LEFT.get_height() - bear.y))) #distance of bear to bar in y axis

            if output[0] > 0.4: #decide to turn or not
                bear.turn()


        add_bar = False
        rem = []
        for bar in bars:
            bar.move()

            for bear in bears:
                if bar.collide(bear, win): #collision
                    ge[bears.index(bear)].fitness -= 100
                    nets.pop(bears.index(bear))
                    ge.pop(bears.index(bear))
                    bears.pop(bears.index(bear))

            if bar.x > bear.y + bear.img.get_height(): 
                rem.append(bar)

            if not bar.passed and bar.x + bar.BAR_LEFT.get_height() > bear.y:
                bar.passed = True
                add_bar = True



        if add_bar:
            score += 1
            for genome in ge:
                genome.fitness += 5 #reward for being able to score
            bars.append(Bar(-30))

        for r in rem:
            bars.remove(r)

        for bear in bears:
            if bear.x + bear.img.get_width() - 36 > WIN_WIDTH or bear.x  < -bear.img.get_width() + 36: #to keep bears inside screen
                ge[bears.index(bear)].fitness -= 250
                nets.pop(bears.index(bear))
                ge.pop(bears.index(bear))
                bears.pop(bears.index(bear))

        print(genome.fitness)
        draw_window(win, bears, bars, score, GEN)
    
    



def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    p = neat.Population(config)

    # p.add_reporter(neat.StdOutReporter(True))
    # stats = neat.StatisticsReporter()
    # p.add_reporter(stats)

    winner = p.run(main, 100)



if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)