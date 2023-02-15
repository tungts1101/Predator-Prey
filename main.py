import sys
import pygame
import argparse
import random
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('-w', '--width', type=int)

class Entity:
    def __init__(self, id, screen_width, size=7, radius=20, speed=10, dir=np.array([1, 1])):
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
    
    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id

def find_locals(entity, entities):
    local_preds = []
    local_preys = []
    for e in entities:
        if entity.id == e.id: continue
        distance = ((entity.pos[0]-e.pos[0]) ** 2 + (entity.pos[1]-e.pos[1]) ** 2)
        if distance > entity.radius**2: continue
        if isinstance(e, Predator):
            local_preds.append(e)
        elif isinstance(e, Prey):
            local_preys.append(e)
    return local_preds, local_preys

class Predator(Entity):
    def __init__(self, id, screen_width, time_alive=0, size=7, radius=70, speed=4, dir=np.array([1, 1])):
        super().__init__(id, screen_width, size, radius, speed, dir)
        self.time_alive = time_alive
    
    def update(self, interval, entities):
        self.time_alive += interval
        local_preds, local_preys = find_locals(self, entities)
        removed_preys = []
        distance = 1e6
        for prey in local_preys:
            distance_to_prey = (self.pos[0] - prey.pos[0]) ** 2 + (self.pos[1] - prey.pos[1]) ** 2
            if distance > distance_to_prey:
                distance = distance_to_prey
                self.dir = np.array([prey.pos[0] - self.pos[0], prey.pos[1] - self.pos[1]])

        norm = np.sqrt(self.dir.dot(self.dir))
        self.dir = self.dir/(norm + (norm == 0))

        self.pos = (
            (self.pos[0] + self.dir[0]*self.speed) % self.screen_width, 
            (self.pos[1] + self.dir[1]*self.speed) % self.screen_width
        )
        for prey in local_preys:
            distance_to_prey = (self.pos[0] - prey.pos[0]) ** 2 + (self.pos[1] - prey.pos[1]) ** 2
            if distance_to_prey < 10 ** 2:
                removed_preys.append(prey)
                self.time_alive -= 2000
        
        return removed_preys

    def show(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.pos, self.size, 0)
        pygame.draw.circle(screen, (255,0,0), self.pos, self.radius, 1)     

class Prey(Entity):
    def __init__(self, id, screen_width, size=7, radius=100, speed=3, dir=np.array([1, 1])):
        super().__init__(id, screen_width, size, radius, speed, dir)
    
    def update(self, interval, entities):
        local_preds, local_preys = find_locals(self, entities)
        if local_preds:
            pos = np.average([pred.pos for pred in local_preds], axis=0)
            self.dir = np.array([-pos[0] + self.pos[0], -pos[1] + self.pos[1]])
            norm = np.sqrt(self.dir.dot(self.dir))
            self.dir = self.dir/(norm + (norm == 0))
        else:
            self.dir = np.array([0, 0])

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
        predators.append(Predator(id, screen_width, dir=np.array([random.randint(-1, 1), random.randint(-1, 1)])))
        id += 1
    for _ in range(10):
        preys.append(Prey(id, screen_width))
        id += 1

    passed_time = 0
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or pygame.key.get_pressed()[pygame.K_ESCAPE]: sys.exit()
        
        screen.fill(screen_color)

        interval = clock.tick(60)
        passed_time += interval
        if passed_time > 1000:
            passed_time = 0
            for pred in predators:
                pred.dir = np.array([random.randint(-1, 1), random.randint(-1, 1)])

        removed_preds = set()
        for pred in predators:
            if pred.time_alive > 5000:
                removed_preds.add(pred.id)
        predators = [pred for pred in predators if pred.id not in removed_preds]

        entities = predators + preys
        removed_preys = set()
        for pred in predators:
            for prey in pred.update(interval, entities):
                removed_preys.add(prey.id)
        preys = [prey for prey in preys if prey.id not in removed_preys]
        for prey in preys:
            prey.update(interval, entities)

        for pred in predators:
            pred.show(screen)
        for prey in preys:
            prey.show(screen)
        pygame.display.update()