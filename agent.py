import numpy as np
import pygame
import sys
from predator_policy import PredatorPolicy

class Agent:
    def __init__(self, id, screen_width, pos, vision_radius, speed, direction, size):
        self.id = id
        self.screen_width = screen_width
        self.pos = pos % screen_width
        self.vision_radius = vision_radius
        self.speed = speed
        self.direction = direction
        self.size = size

    def find_locals(self, agents):
        preds, preys = [], []
        for agent in agents:
            if self == agent: continue
            if not self.is_in_vision(agent): continue
            if isinstance(agent, Predator):
                preds.append(agent)
            elif isinstance(agent, Prey):
                preys.append(agent)
        return preds, preys

    def get_square_distance(self, agent):
        return np.sum((self.pos - agent.pos) ** 2) 

    def is_in_vision(self, agent):
        return self.get_square_distance(agent) <= self.vision_radius ** 2

    def update_position(self, obstacles):
        pos = (self.pos + self.speed * self.direction) % self.screen_width
        # collided_obstacles = []
        # for obs in obstacles:
        #     collided = obs.is_intersect(self.pos, pos)
        #     if not collided: continue
        #     collided_obstacles.extend([(np.array(collided), obs)])
        # if collided_obstacles:
        #     obs = min(collided_obstacles, key=lambda x: np.sum((self.pos - x[0])) ** 2)
        #     collided_point, rect = obs[0], obs[1].rect
        #     target = collided_point
        #     if np.sum((self.pos - target) ** 2) < 1:
        #         corners = [
        #             np.array([rect.topleft[0], rect.topleft[1]]), 
        #             np.array([rect.topright[0], rect.topright[1]]),
        #             np.array([rect.bottomleft[0], rect.bottomleft[1]]),
        #             np.array([rect.bottomright[0], rect.bottomright[1]]),
        #         ]
        #         target = min(corners, key=lambda x: np.sum((collided_point - x)) ** 2)
            
        #     self.direction = target - self.pos
        #     norm = np.sqrt(self.direction.dot(self.direction))
        #     self.direction = self.direction/(norm + (norm == 0))
        #     pos = (self.pos + self.speed * self.direction) % self.screen_width

        #     print(f"target = {target}")
        #     print(f"old pos = {self.pos}, new pos = {pos}")
        #     print(f"in = {obs[1].is_intersect(self.pos, target)}")
        #     # print(rect.collidepoint(self.pos))
        #     # if rect.collidepoint(self.pos):
        #     #     pos = np.array(obs[1].is_intersect(self.pos, target))
        #     # print(rect.collidepoint(pos))

        #     # if rect.collidepoint(pos):
        #     #     print("wrong")
        #     #     print(f"clip = {pos}, in = {obs[1].is_intersect(self.pos, pos)}")
        #     #     clipped_line = rect.clipline(self.pos, collided_point)
        #     #     if clipped_line:
        #     #         pos = np.array(clipped_line[0])
        #     #     print(f"clip = {pos}, in = {obs[1].is_intersect(self.pos, pos)}")
        #         # pos = np.array([obs.is_collided(self.pos, pos)])

        #         # if np.sum((self.pos - collided_point) ** 2) == 0:
        #         #     clipped_line = rect.clip_line(self.pos, collided_point)
        #         #     pos = clipped_line[0]

        #     self.pos = pos
        #     return

        self.pos = pos

    def update(self, interval, agents, obstacles):
        raise Exception("Missing implementation")

    def show(self):
        raise Exception("Missing implementation")
    
    def __eq__(self, __o: object) -> bool:
        return self.id == __o.id
    
class Predator(Agent):
    def __init__(
        self, 
        id, 
        screen_width, 
        pos, 
        vision_radius=2,
        speed=1,
        direction=np.array([1, 1]),
        size=7,
        capture_radius=1,
        max_time_alive=5000,
        max_time_change_dir=1000,
    ):
        assert max_time_alive > 0
        assert speed > 0
        assert capture_radius > 0
        assert capture_radius < vision_radius

        super().__init__(id, screen_width, pos, vision_radius, speed, direction, size)
        self.capture_radius = capture_radius

        self.time_alive = 0
        self.max_time_alive = max_time_alive
        self.time_change_dir = 0 # pred will not change dir all the time
        self.max_time_change_dir = max_time_change_dir
        self.is_hunger = False

        self.is_show_vision = True
        self.is_show_capture = True

    def set_policy(self, fn: PredatorPolicy):
        self.policy = fn

    def update(self, interval, agents, obstacles) -> list[Agent]:
        assert self.policy != None

        self.time_alive += interval
        if self.time_alive > self.max_time_alive:
            self.is_hunger = True
            return []

        captured_preys = []

        local_preds, local_preys = self.find_locals(agents)
        direction = self.policy.apply(self, local_preds, local_preys, obstacles)
        if len(direction) > 0:
            self.direction = direction
        else:
            self.time_change_dir += interval
            if self.time_change_dir >= self.max_time_change_dir:
                self.time_change_dir = 0
                self.direction = np.random.uniform(low=-1, high=1, size=(2))

        norm = np.sqrt(self.direction.dot(self.direction))
        self.direction = self.direction/(norm + (norm == 0))

        self.update_position(obstacles)

        for prey in local_preys:
            if self.get_square_distance(prey) <= self.capture_radius ** 2:
                captured_preys.append(prey)
                self.time_alive -= 2000
        
        return captured_preys

    def show(self, screen):
        pygame.draw.circle(screen, (0,0,255), self.pos, self.size, 0)
        if self.is_show_capture:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.capture_radius, 1)
        if self.is_show_vision:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.vision_radius, 1)

class Prey(Agent):
    def __init__(
        self,
        id, 
        screen_width, 
        pos, 
        vision_radius=2,
        speed=1,
        direction=np.array([1, 1]),
        size=7, 
    ):
        super().__init__(id, screen_width, pos, vision_radius, speed, direction, size)

        self.is_show_vision = True
    
    def update(self, interval, agents, obstacles):
        local_preds, local_preys = self.find_locals(agents)
        
        if local_preds:
            pos = np.average([pred.pos for pred in local_preds], axis=0)
            self.direction = np.array([-pos[0] + self.pos[0], -pos[1] + self.pos[1]])
            norm = np.sqrt(self.direction.dot(self.direction))
            self.direction = self.direction/(norm + (norm == 0))
        else:
            self.direction = np.array([0, 0])

        self.update_position(obstacles)

    def show(self, screen):
        pygame.draw.rect(screen, (0,255,0), (self.pos[0]-self.size/2,self.pos[1]-self.size/2,self.size,self.size),0)
        if self.is_show_vision:
            pygame.draw.circle(screen, (255,0,0), self.pos, self.vision_radius, 1) 