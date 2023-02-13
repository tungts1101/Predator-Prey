import sys
import pygame
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--width', type=int)

class Entity:
    def __init__(self, id, screen_width, size=7, radius=20, speed=10, dir=(1, 1)):
        self.id = id
        self.screen_width = screen_width
        self.pos = (screen_width * random.random(), screen_width * random.random())
        self.size = size
        self.radius = radius
        self.speed = speed
        self.dir = dir
    
    def update(self):
        raise Exception("Missing implementation")

    def show(self):
        raise Exception("Missing implementation")

def find_locals(entity, entities):
    local_preds = []
    local_preys = []
    for e in entities:
        if entity.id == e.id: continue
        distance = ((entity.pos[0]-e.pos[0]) ** 2 + (entity.pos[1]-e.pos[1]) ** 2)
        if distance > entity.radius**2: continue
        if isinstance(entity, Predator):
            local_preds.append(entity)
        elif isinstance(entity, Prey):
            local_preys.append(entity)
    return local_preds, local_preys

class Predator(Entity):
    def __init__(self, id, screen_width, size=7, radius=70, speed=4, dir=(1,1)):
        super().__init__(id, screen_width, size, radius, speed)
    
    def update(self, interval, entities):
        # self.dir = (random.random(), random.random())
        local_preds, local_preys = find_locals(self, entities)
        print([e.id for e in local_preds])

        self.pos = (
            (self.pos[0] + self.dir[0]*self.speed) % self.screen_width, 
            (self.pos[1] + self.dir[1]*self.speed) % self.screen_width
        )

    def show(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.pos, self.size, 0)
        pygame.draw.circle(screen, (255,0,0), self.pos, self.radius, 1)     

class Prey(Entity):
    def __init__(self, id, screen_width, size=7, radius=100, speed=3, dir=(1,1)):
        super().__init__(id, screen_width, size, radius, speed)
    
    def update(self, interval, entities):
        # self.dir = (random.random(), random.random())
        self.pos = (
            (self.pos[0] + self.dir[0]*self.speed) % self.screen_width, 
            (self.pos[1] + self.dir[1]*self.speed) % self.screen_width
        )

    def show(self, screen):
        pygame.draw.rect(screen, (0,255,0), (self.pos[0]-self.size/2,self.pos[1]-self.size/2,self.size,self.size),0)
        pygame.draw.circle(screen, (255,0,0), self.pos, self.radius, 1) 

if __name__ == '__main__':
    args = parser.parse_args()

    # pygame screen attributes
    screen_color = (0.2 * 255, 0.3 * 255, 0.3 * 255)
    screen_width = 640 if args.width is None else args.width
    screen = pygame.display.set_mode((screen_width, screen_width))
    clock = pygame.time.Clock()

    id = 0
    predators = []
    preys = []
    for _ in range(5):
        predators.append(Predator(id, screen_width))
        id += 1
        preys.append(Prey(id, screen_width))
        id += 1

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]: sys.exit()
        
        screen.fill(screen_color)

        interval = clock.tick(60)
        entities = predators + preys
        for pred in predators:
            pred.update(interval, entities)
        for prey in preys:
            prey.update(interval, entities)

        for pred in predators:
            pred.show(screen)
        for prey in preys:
            prey.show(screen)
        pygame.display.update()