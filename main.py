import sys
import pygame
import argparse
import random
import numpy as np
import time

from obstacle import Obstacle
from agent import Predator, Prey
from predator_policy import NearestPreyPolicy

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--width', type=int)
parser.add_argument('-npred', '--num_predator', type=int)
parser.add_argument('-nprey', '--num_prey', type=int)
 
if __name__ == '__main__':
    args = parser.parse_args()

    # pygame screen attributes
    screen_color = (0.2 * 255, 0.3 * 255, 0.3 * 255)
    screen_width = 640 if args.width is None else args.width
    screen = pygame.display.set_mode((screen_width, screen_width))
    clock = pygame.time.Clock()

    num_pred = 5 if args.num_predator is None else args.num_predator
    num_prey = 10 if args.num_prey is None else args.num_prey

    obstacles = []
    # positions = [(0, 0), (300, 300), (0, 250)]
    # for i in range(3):
    #     obs = Obstacle(positions[i], 150, 70)
    #     obstacles.append(obs)

    predators = []
    preys = []
    for _ in range(num_pred):
        num_try = 0
        pos = (random.randint(0, screen_width), random.randint(0, screen_width))
        while num_try < 10 and any([obs.rect.collidepoint(pos) for obs in obstacles]):
            pos = (random.randint(0, screen_width), random.randint(0, screen_width))
            num_try += 1
        if any([obs.rect.collidepoint(pos) for obs in obstacles]): continue

        pred = Predator(
            id=time.time_ns(), 
            screen_width=screen_width,
            pos=np.array(pos),
            vision_radius=50,
            speed=4,
            direction=np.array([1, 1]),
            size=7,
            capture_radius=10,
            max_time_alive=5000,
        )
        pred.set_policy(NearestPreyPolicy)
        predators.append(pred)
    
    for _ in range(num_prey):
        num_try = 0
        pos = (random.randint(0, screen_width), random.randint(0, screen_width))
        while num_try < 10 and any([obs.rect.collidepoint(pos) for obs in obstacles]):
            pos = (random.randint(0, screen_width), random.randint(0, screen_width))
            num_try += 1
        if any([obs.rect.collidepoint(pos) for obs in obstacles]): continue

        prey = Prey(
            id=time.time_ns(), 
            screen_width=screen_width,
            pos=np.array(pos),
            vision_radius=70,
            speed=3,
            direction=np.array([1, 1]),
            size=7,
        )
        preys.append(prey)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]: 
                sys.exit()
        
        screen.fill(screen_color)
        for obs in obstacles:
            obs.show(screen)

        interval = clock.tick(60)

        removed_preds = set([pred.id for pred in predators if pred.is_hunger])
        predators = [pred for pred in predators if pred.id not in removed_preds]

        agents = predators + preys
        removed_preys = set()
        for pred in predators:
            captured_preys = pred.update(interval, agents, obstacles)
            removed_preys.update([prey.id for prey in captured_preys])
        preys = [prey for prey in preys if prey.id not in removed_preys]

        for prey in preys:
            prey.update(interval, agents, obstacles)

        for pred in predators:
            pred.show(screen)
        for prey in preys:
            prey.show(screen)

        pygame.display.update()