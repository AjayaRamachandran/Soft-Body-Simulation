###### IMPORT ######

import pygame
import random
import time
from math import *
import numpy as np
import copy


###### SETUP ######
pygame.init()

windowSize = (1280, 720)

pygame.display.set_caption("intersectionTest") # Sets title of window
screen = pygame.display.set_mode(windowSize) # Sets the dimensions of the window to the windowSize

font = pygame.font.Font(None, 36)

fps = 1
clock = pygame.time.Clock()


###### FUNCTIONS ######
def getIntersectionPoint(line1, line2):
    x1 = line1[0]
    y1 = line1[1]
    x2 = line1[2]
    y2 = line1[3]

    x3 = line2[0]
    y3 = line2[1]
    x4 = line2[2]
    y4 = line2[3]

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        return None  # No intersection (lines are parallel)

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator

    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)

    if 0 <= t <= 1:
        return (x, y)  # Return the intersection point
    else:
        return (x, y) # No intersection within line segments (lines are not parallel, but they don't intersect in the specified segments)
    
###### INITIALIZE ######

def initialize():
    global pointX1,pointX2,pointY1,pointY2,pointX3,pointX4,pointY3,pointY4,x5,y5
    pointX1 = random.randint(340,940)
    pointY1 = random.randint(160,560)
    pointX2 = random.randint(340,940)
    pointY2 = random.randint(160,560)

    pointX3 = random.randint(340,940)
    pointY3 = random.randint(160,560)
    pointX4 = random.randint(340,940)
    pointY4 = random.randint(160,560)

    x5,y5 = getIntersectionPoint((pointX1,pointY1,pointX2,pointY2),(pointX3,pointY3,pointX4,pointY4))


###### MAINLOOP ######
running = True # Runs the game loop
while running:

    initialize()
    if (x5, y5) == (None, None):
        screen.fill((255,0,0))
    else:
        screen.fill((0,0,0))
        pygame.draw.circle(screen, (255, 255, 255), (x5, y5), 5)

    pygame.draw.aaline(screen, (255, 255, 255), (pointX1, pointY1), (pointX2, pointY2), 5)
    pygame.draw.aaline(screen, (255, 255, 255), (pointX3, pointY3), (pointX4, pointY4), 5)
    

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False
    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()
    #time.sleep(1)
    

# quit Pygame
pygame.quit()