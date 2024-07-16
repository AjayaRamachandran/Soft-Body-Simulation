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
fpsMultiplier = 10
clock = pygame.time.Clock()
dt = 1/10

###### INITIALIZE ######

SIMSPEED = 0.01
GRAVITY = [0, 2]
SPACING = 40
CLOSELIMIT = 20
RESOLUTION = 3
#SPRINGLIMIT = SPACING * 1.5
SPRINGLIMIT = 125
STIFFNESS = 60
DAMPING = 0.998

###### VARIABLES ######

listOfPoints = []
newListOfPoints = []
chasePoints = []
springs = []

objects = []
newObjects = []
objectSprings = []

things = []
newThings = []

oldMouse = pygame.mouse.get_pos()
mode = "test"
editor = True

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

def getIntersectionPoint(line1, line2):
    '''
    ## getIntersectionPoint()
    Computes the coordinate of intersection between two line segments, outputting `None` if the line segments do not intersect.
    '''
    x1 = line1[0][0]
    y1 = line1[0][1]
    x2 = line1[1][0]
    y2 = line1[1][1]

    x3 = line2[0][0]
    y3 = line2[0][1]
    x4 = line2[1][0]
    y4 = line2[1][1]

    denominator = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if denominator == 0:
        return None  # No intersection (lines are parallel)

    t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denominator
    u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denominator

    x = x1 + t * (x2 - x1)
    y = y1 + t * (y2 - y1)

    if 0 <= t <= 1 and 0 <= u <= 1:
        return (x, y)  # Return the intersection point
    else:
        return None  # No intersection within line segments (lines are not parallel, but they don't intersect in the specified segments)

def colorLerp(color1, color2, fac): # function for adding all tuples in a list as vectors
    '''
    ## colorLerp()
    Takes two colors (tuples/lists) and a lerp value `fac` between 0 and 1 that blends between those colors at that proportion.
    '''

    return [color1[0] * (1-fac) + color2[0] * fac, color1[1] * (1-fac) + color2[1] * fac, color1[2] * (1-fac) + color2[2] * fac]

###### MAIN FUNCTIONS ######

def initializePoints(): # function to create the points in a grid setup
    '''
    ## initializePoints()
    Function for creating points in a grid setup. Uses global variables like `SPACING` and `RESOLUTION` to control the shape.
    '''
    global newListOfPoints, chasePoints
    if mode == "grid":
        for x in range(-RESOLUTION, RESOLUTION + 1):
            for y in range(-RESOLUTION, RESOLUTION + 1):
                listOfPoints.append([width/2 + x*SPACING, height/2 + y*SPACING, 0, 0, False, 1])
        chasePoints = copy.deepcopy(listOfPoints)
    else:
        listOfPoints.append([width/2 - 250, height/2 + 50, 0, 0, True, 1])
        for truss in range(1,6):
            if not truss == 5:
                listOfPoints.append([width/2 - 250 + (truss)*100, height/2 + 50, 0, 0, False, 1])
            listOfPoints.append([width/2 - 250 + (truss - 0.5)*100, height/2 - 50, 0, 0, False, 1])
        listOfPoints.append([width/2 + 250, height/2 + 50, 0, 0, True, 1])
        chasePoints = copy.deepcopy(listOfPoints)
    #listOfPoints.append([width/2, height/2, 0, -1])
    #listOfPoints.append([width/2, height/2 + SPACING, 0, 1])

    newListOfPoints = copy.deepcopy(listOfPoints)
            
def createSprings(listOfPoints, SPRINGLIMIT): # function to create springs between a list of points that have a resting distance
    '''
    ## createSprings()
    Function for creating springs between points. Takes in a list of points and outputs indices of all the springs that are generated.
    '''
    generatedSprings = []
    for pointIndex1 in range(len(listOfPoints)):
        for pointIndex2 in range(len(listOfPoints)):
            if pointIndex1 != pointIndex2:
                if dist(listOfPoints[pointIndex1], listOfPoints[pointIndex2]) < SPRINGLIMIT:
                    if listOfPoints[pointIndex1][1] > height/2 and listOfPoints[pointIndex2][1] > height/2:
                        generatedSprings.append([pointIndex1, pointIndex2, dist(listOfPoints[pointIndex1], listOfPoints[pointIndex2]), "road"])
                    else:
                        generatedSprings.append([pointIndex1, pointIndex2, dist(listOfPoints[pointIndex1], listOfPoints[pointIndex2]), "wood"])

    return generatedSprings


def transformPoint(index, localListOfPoints, springsList, internalAcceleration, isObject=False): # master function to transform a point
    '''
    ## transformPoint()
    Master function for transforming points. Takes in a point index, list of connected points, etc. and outputs an updated point coordinate.
    '''
    position = [0,0]
    velocity = [0,0]
    #print(listOfPoints)
    [position[0], position[1], velocity[0], velocity[1], fixed, mass] = localListOfPoints[index]
    #position = addVectors([position, [random.randint(-1,1), random.randint(-1,1)]])\
    #mass *= 1.002
    acceleration = [0, 0]
    acceleration = addVectors([acceleration, internalAcceleration])

    if position[1] >= 550:
        position[1] = 550
        velocity[1] -= velocity[1] * 2
        #acceleration = addVectors([acceleration, [0, (-position[1] + 550) * 2]])

    for spring in springsList: # spring force calculation
        if index in spring[0:2]:
            if spring[1] == index: # checks to see if the spring has our current point on one of its ends
                direction = dirTo(localListOfPoints[spring[0]][0:2], localListOfPoints[spring[1]][0:2])
            else:
                direction = dirTo(localListOfPoints[spring[1]][0:2], localListOfPoints[spring[0]][0:2])
            distance = dist(localListOfPoints[spring[0]][0:2], localListOfPoints[spring[1]][0:2])
            springVector = [(cos(direction) * STIFFNESS * (spring[2] - distance)), (sin(direction) * STIFFNESS * (spring[2] - distance))] # converts polar to rect
            acceleration = addVectors([acceleration, [springVector[axis] / mass for axis in range(2)]])
    for index2 in range(len(localListOfPoints)): # "close pressure" calculation, inspired off of some other people's designs that did something similar to push close particles apart
        if index2 != index:
            distance = dist(position, localListOfPoints[index2][0:2])
            direction = dirTo(position, localListOfPoints[index2][0:2])
            if distance < CLOSELIMIT + 5:
                closePressure = 1 / (dist(localListOfPoints[spring[1]][0:2], localListOfPoints[spring[0]][0:2]) - CLOSELIMIT) - 1/5
                closeVector = [cos(direction) * closePressure, sin(direction) * closePressure]
                acceleration = addVectors([acceleration, closeVector])
    

    

    acceleration = [axis * SIMSPEED for axis in acceleration]
    velocity = addVectors([velocity, acceleration])
    velocity = [axis * DAMPING for axis in velocity]
    #position = addVectors([position, velocity]) # euler integration (old)
    
    if fixed:
        position = position # edge case where point is considered "fixed", if so do not change position
    else:
        position = [position[i] + velocity[i] * dt + 0.5 * acceleration[i] * dt**2 for i in range(len(position))] # VERLET integration, reduces jitter and we can get away with less sim steps/frame
    pointInformation = [position[0], position[1], velocity[0], velocity[1], fixed, mass]
    return pointInformation

def createThings():
    ## Location, Initial Velocity
    #CENTER = random.randint(300, 900), 100
    CENTER = width/2 - 150, height/2 + 50
    SIZE = 50

    things.append([CENTER[0] - SIZE, CENTER[1] - SIZE, 0, 0, 30, 50, [0.3, 2]])

def transformObjects():
    global objects
    for index in range(len(objects)):
        #print(objects)
        newObjects = copy.deepcopy(objects)
        object = objects[index] # `object` contains the point informations in the object
        for index2 in range(len(object)): # index2 is the index of the point within the object
            newObjects[index][index2] = transformPoint(index2, copy.copy(object), copy.copy(objectSprings[index]), GRAVITY, isObject=True)[:6]
    
    objects = copy.deepcopy(newObjects)

def transformThings():
    global things, dt
    for index in range(len(things)):
        position = [0,0]
        velocity = [0,0]

        [position[0], position[1], velocity[0], velocity[1], mass, radius, internalAcceleration] = things[index]
        acceleration = [0, 0]
        acceleration = addVectors([acceleration, internalAcceleration])
        if position[1] >= 550 - radius:
            position[1] = 550 - radius
            velocity[1] -= velocity[1] * 2
        
        for point in listOfPoints:
            point[5] = 1

        for spring in springs:
            if spring[3] == "road":
                coordinate1 = listOfPoints[spring[0]][:2]
                coordinate2 = listOfPoints[spring[1]][:2]

                for lerp in range(10):
                    interCoord = [coordinate1[i] * (lerp/10) + coordinate2[i] * (1-(lerp/10)) for i in range(2)]
                    #pygame.draw.circle(screen, (0, 255, 0), interCoord, 4)
                    if dist(position, interCoord) < radius:
                        moveDir = dirTo(interCoord, position)
                        position[0] += cos(moveDir) * 0.3
                        position[1] += sin(moveDir) * 0.3
                        #velocity[0] += cos(moveDir) * 0.05
                        #velocity[1] += sin(moveDir) * 0.05
                        acceleration[0] += cos(moveDir) * 0.3
                        acceleration[1] += sin(moveDir) * 0.3

                        listOfPoints[spring[0]][5] = mass * (1-lerp/10) + 1
                        listOfPoints[spring[1]][5] = mass * (lerp/10) + 1
                        #print(listOfPoints)

        acceleration = [axis * SIMSPEED for axis in acceleration]
        velocity = addVectors([velocity, acceleration])
        velocity = [axis * DAMPING for axis in velocity]
        position = [position[i] + velocity[i] * dt + 0.5 * acceleration[i] * dt**2 for i in range(len(position))] # VERLET integration, reduces jitter and we can get away with less sim steps/frame

        things[index] = [position[0], position[1], velocity[0], velocity[1], mass, radius, internalAcceleration]

###### MAINLOOP ######
initializePoints()
springs = createSprings(listOfPoints, SPRINGLIMIT)
createThings()
selected = None
running = True # Runs the game loop
while running:
    screen.fill((255, 255, 255))

    for index in range(len(chasePoints)):
        chasePoints[index][0] += (listOfPoints[index][0] - chasePoints[index][0]) * 0.4
        chasePoints[index][1] += (listOfPoints[index][1] - chasePoints[index][1]) * 0.4

    for point in chasePoints:
        pygame.draw.circle(screen, (150, 150, 150), point[0:2], 7)
        pygame.draw.circle(screen, (0,0,0), point[0:2], 4)
    
    for object in objects:
        pygame.draw.polygon(screen, (90, 90, 90), [point[:2] for point in object])

    for thing in things:
        pygame.draw.circle(screen, [90, 90, 90], thing[:2], thing[5])
    
    numDestructions = 0 # Hard Limit : Only one structure breakage per frame
    for spring in springs:
        stress = abs((dist(listOfPoints[spring[0]], listOfPoints[spring[1]]) - spring[2]))
        if stress > 5 and numDestructions <= 1:
            listOfPoints.append(copy.copy(listOfPoints[spring[0]]))
            listOfPoints.append(copy.copy(listOfPoints[spring[1]]))
            springs.append([len(listOfPoints) - 2, len(listOfPoints) - 1, copy.copy(spring[2]), spring[3]])
            springs.remove(spring)
            chasePoints.append(copy.copy(listOfPoints[spring[0]]))
            chasePoints.append(copy.copy(listOfPoints[spring[1]]))
            numDestructions += 1
        red = int(clamp(0 + 220 * stress, [0, 255])) / 255 # represents the amount of red that should be visible based on stress
        redColor = [255, 0, 0]
        if spring[3] == "road":
            pygame.draw.line(screen, colorLerp([30, 30, 30], redColor, red), chasePoints[spring[0]][0:2], chasePoints[spring[1]][0:2], 5)
        elif spring[3] == "wood":
            pygame.draw.line(screen, colorLerp([60, 60, 60], redColor, red), chasePoints[spring[0]][0:2], chasePoints[spring[1]][0:2], 5)
    if numDestructions != 0:
        springs.pop()
        listOfPoints.pop()
        listOfPoints.pop()
        chasePoints.pop()
        chasePoints.pop()
    newListOfPoints = copy.deepcopy(listOfPoints)

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False
    
    for frame in range(fpsMultiplier):
        #transformObjects()
        transformThings()
        for point in range(len(listOfPoints)):
            newListOfPoints[point] = transformPoint(point, listOfPoints, springs, GRAVITY)

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