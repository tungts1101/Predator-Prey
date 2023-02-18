import pygame
from sympy import Segment2D

class Obstacle:
    def __init__(self, pos, width, height) -> None:
        self.rect = pygame.Rect(pos[0], pos[1], width, height)
        self.edges = [
            (self.rect.topleft, self.rect.topright),
            (self.rect.topright, self.rect.bottomright),
            (self.rect.bottomright, self.rect.bottomleft),
            (self.rect.bottomleft, self.rect.topleft),
        ]

    def intersect(self, seg1, seg2):
        """Returns the intersection point of two line segments, if any."""
        x1, y1 = seg1[0]
        x2, y2 = seg1[1]
        x3, y3 = seg2[0]
        x4, y4 = seg2[1]

        # Calculate the direction of the two line segments
        dx1 = x2 - x1
        dy1 = y2 - y1
        dx2 = x4 - x3
        dy2 = y4 - y3

        # Calculate the denominators of the two equations
        denom = dx1 * dy2 - dx2 * dy1

        # Check if the segments are parallel or collinear
        if denom == 0:
            # Check if the two segments overlap
            if (min(x1, x2) <= x3 <= max(x1, x2) or min(x1, x2) <= x4 <= max(x1, x2)) \
            and (min(y1, y2) <= y3 <= max(y1, y2) or min(y1, y2) <= y4 <= max(y1, y2)):
                return int(x1), int(y1)
            else:
                return None

        # Calculate the numerators of the two equations
        num1 = (x1 - x3) * dy2 - (y1 - y3) * dx2
        num2 = (x1 - x3) * dy1 - (y1 - y3) * dx1

        # Calculate the parameters t and u
        t = num1 / denom
        u = -num2 / denom

        # Check if the intersection point lies within both line segments
        if 0 <= t <= 1 and 0 <= u <= 1:
            x = x1 + t * dx1
            y = y1 + t * dy1
            return int(x), int(y)
        else:
            return None
    
    def is_collided(self, agent_old_pos, agent_new_pos):
        return self.rect.clipline(agent_old_pos, agent_new_pos)

        # s = (agent_old_pos, agent_new_pos)
        # for edge in self.edges:
        #     inter = self.intersect(edge, s)
        #     if inter:
        #         return inter
        # return []
    
    def is_intersect(self, agent_old_pos, agent_new_pos):
        s = (agent_old_pos, agent_new_pos)
        for edge in self.edges:
            inter = self.intersect(s, edge)
            if inter:
                return inter
        return []
    
    def show(self, screen):
        pygame.draw.rect(screen, (255,255,0), self.rect, 0)