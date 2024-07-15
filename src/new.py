###### IMPORT ######

import pygame
import random
import time
from math import *
import numpy as np
import copy


###### SETUP ######
pygame.init()

width = 1280
height = 720
windowSize = (width, height)

pygame.display.set_caption("Soft Body Simulation") # Sets title of window
screen = pygame.display.set_mode(windowSize) # Sets the dimensions of the window to the windowSize

font = pygame.font.Font(None, 36)

fps = 60
fpsMultiplier = 5
clock = pygame.time.Clock()
dt = 1/5

###### INITIALIZE ######

SIMSPEED = 0.08
GRAVITY = [0, 2]
SPACING = 40
CLOSELIMIT = 20
RESOLUTION = 3
SPRINGLIMIT = SPACING * 1.5
STIFFNESS = 5
DAMPING = 0.992

###### VARIABLES ######

listOfPoints = []
newListOfPoints = []
springs = []
oldMouse = pygame.mouse.get_pos()
mode = "grid"

###### OPERATOR FUNCTIONS ######

def dist(point1, point2): # abstracted distance function
    '''
    ## dist()
    Abstracted function for finding the distance from one point to another.
    '''
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def dirTo(point1, point2): # abstracted direction function
    '''
    ## dirTo()
    Abstracted function for finding the direction (in absolute radians) from one point to another.
    '''
    return atan2((point2[1] - point1[1]), (point2[0] - point1[0]))

def clamp(value, range): # range clamping function
    '''
    ## clamp()
    Outputs the upper limit of the range if the value is greater than it, and the lower limit of the range if the value is less than it.
    '''
    return min(max(value, range[0]), range[1])

def addVectors(listOfVectors): # function for adding all tuples in a list as vectors
    '''
    ## addVectors()
    Takes in a list of vectors and outputs the sums of the X values and Y values in a vector.
    '''
    xVec = 0
    for item in range(len(listOfVectors)):
        xVec = xVec + listOfVectors[item][0]

    yVec = 0
    for item in range(len(listOfVectors)):
        yVec = yVec + listOfVectors[item][1]

    return [xVec,yVec]

###### MAIN FUNCTIONS ######

def initializePoints(): # function to create the points in a grid setup
    '''
    ## initializePoints()
    Function for creating points in a grid setup. Uses global variables like `SPACING` and `RESOLUTION` to control the shape.
    '''
    global newListOfPoints
    if mode == "grid":
        for x in range(-RESOLUTION, RESOLUTION + 1):
            for y in range(-RESOLUTION, RESOLUTION + 1):
                listOfPoints.append([width/2 + x*SPACING, height/2 + y*SPACING, 0, 0])
    else:
        for i in range(10):
            listOfPoints.append([width/2 + random.randint(-100, 100), height/2 + random.randint(-100, 100), 0, 0])

    #listOfPoints.append([width/2, height/2, 0, -1])
    #listOfPoints.append([width/2, height/2 + SPACING, 0, 1])

    newListOfPoints = listOfPoints
            
def createSprings(): # function to create springs between the points that have a resting distance
    '''
    ## createSprings()
    Function for creating springs between the points. Uses the global variable `SPRINGLIMIT` to control which point pairs get springs.
    '''
    for pointIndex1 in range(len(listOfPoints)):
        for pointIndex2 in range(len(listOfPoints)):
            if pointIndex1 != pointIndex2:
                if dist(listOfPoints[pointIndex1], listOfPoints[pointIndex2]) < SPRINGLIMIT:
                    springs.append([pointIndex1, pointIndex2, dist(listOfPoints[pointIndex1], listOfPoints[pointIndex2])])



def transformPoint(index): # master function to transform a point
    '''
    ## transformPoint()
    Master function for transforming points. Takes in a point index and outputs an updated point coordinate.
    '''
    position = [0,0]
    velocity = [0,0]
    [position[0], position[1], velocity[0], velocity[1]] = listOfPoints[index]
    #position = addVectors([position, [random.randint(-1,1), random.randint(-1,1)]])\
    acceleration = [0, 0]
    acceleration = addVectors([acceleration, GRAVITY])

    if position[1] >= 550:
        acceleration = addVectors([acceleration, [0, (-position[1] + 550) * 1]])

    for spring in springs:
        if index in spring[0:2]:
            if spring[1] == index:
                direction = dirTo(listOfPoints[spring[0]][0:2], listOfPoints[spring[1]][0:2])
            else:
                direction = dirTo(listOfPoints[spring[1]][0:2], listOfPoints[spring[0]][0:2])
            distance = dist(listOfPoints[spring[0]][0:2], listOfPoints[spring[1]][0:2])
            springVector = [(cos(direction) * STIFFNESS * (spring[2] - distance)), (sin(direction) * STIFFNESS * (spring[2] - distance))]
            acceleration = addVectors([acceleration, springVector])
    for index2 in range(len(listOfPoints)):
        if index2 != index:
            distance = dist(position, listOfPoints[index2][0:2])
            direction = dirTo(position, listOfPoints[index2][0:2])
            if distance < CLOSELIMIT + 5:
                closePressure = 1 / (dist(listOfPoints[spring[1]][0:2], listOfPoints[spring[0]][0:2]) - CLOSELIMIT) - 1/5
                closeVector = [cos(direction) * closePressure, sin(direction) * closePressure]
                acceleration = addVectors([acceleration, closeVector])

    acceleration = [axis * SIMSPEED for axis in acceleration]
    velocity = addVectors([velocity, acceleration])
    velocity = [axis * DAMPING for axis in velocity]
    #position = addVectors([position, velocity])
    position = [position[i] + velocity[i] * dt + 0.5 * acceleration[i] * dt**2 for i in range(len(position))]
    #if index == 0:
        #position = [width/2, height/2]
        #velocity = [0,0]
    pointInformation = [position[0], position[1], velocity[0], velocity[1]]
    return pointInformation

###### MAINLOOP ######
initializePoints()
createSprings()
selected = None
running = True # Runs the game loop
while running:
    screen.fill((255, 255, 255))

    for point in listOfPoints:
        pygame.draw.circle(screen, (150, 150, 150), point[0:2], 7)
        pygame.draw.circle(screen, (0,0,0), point[0:2], 4)
    
    for spring in springs:
        red = int(clamp(0 + 8 * abs((dist(listOfPoints[spring[0]], listOfPoints[spring[1]]) - spring[2])), [0, 255]))
        pygame.draw.aaline(screen, (red, 0, 0), listOfPoints[spring[0]][0:2], listOfPoints[spring[1]][0:2])

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False
    
    for frame in range(fpsMultiplier):
        for point in range(len(listOfPoints)):
            newListOfPoints[point] = transformPoint(point)

            if dist(listOfPoints[point], pygame.mouse.get_pos()) < 8 and selected == None and pygame.mouse.get_pressed()[0]:
                selected = point
            if selected == point:
                newListOfPoints[point][0:2] = pygame.mouse.get_pos()
                newListOfPoints[point][2:4] = [(pygame.mouse.get_pos()[axis] - oldMouse[axis])*SIMSPEED for axis in range(2)]
        listOfPoints = copy.deepcopy(newListOfPoints)
    oldMouse = pygame.mouse.get_pos()
    
    if not pygame.mouse.get_pressed()[0]:
        selected = None
    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()
    #time.sleep(1)
    
    if pygame.key.get_pressed()[pygame.K_RIGHT]:
        SIMSPEED *= 0.909
        print(SIMSPEED)
    if pygame.key.get_pressed()[pygame.K_LEFT]:
        SIMSPEED *= 1.1
        print(SIMSPEED)

# quit Pygame
pygame.quit()