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

pygame.display.set_caption("Soft Body Simulation") # Sets title of window
screen = pygame.display.set_mode(windowSize) # Sets the dimensions of the window to the windowSize

#font = pygame.font.Font(None, 36)

###### INITIALIZE ######
# Jelly
positionLibrary = [] # bank of positions of all the points
nextPositionLibrary = [] # buffer of the next frame's point positions
velocityLibrary = [] # bank of velocities of all the points
nextVelocityLibrary = [] # buffer of the next frame's point velocities
edgeTable = [] # bank of all edges, stored as pairs of point indices
restingDistanceTable = [] # reference table of all the resting distances of the edges
ecofTable = [] # bank of all edges' elastic coefficients

# Environment
lineLibrary = [] # list of quad-tuples that creates the shape of the ground, format = (x1, y1, x2, y2)

###### VARIABLES ######
gravity = (0, 0.15)
#restingDistance = 10

# elasticity = 0.5
simResolution = 10
trueElasticity = 0.5
dampening = 0.98

# test ground state
lineLibrary.append(())

fps = 60
clock = pygame.time.Clock()

###### FUNCTIONS ######

def dist(point1, point2): # abstracted distance function
    return sqrt((point2[0] - point1[0]) ** 2 + (point2[1] - point1[1]) ** 2)

def dirTo(point1, point2): # abstracted direction function
    return atan2((point2[1] - point1[1]), (point2[0] - point1[0]))

def addTuplesAsVectors(listOfTuples): # function for adding all tuples in a list as vectors
    xVec = 0
    for item in range(len(listOfTuples)):
        xVec = xVec + listOfTuples[item][0]

    yVec = 0
    for item in range(len(listOfTuples)):
        yVec = yVec + listOfTuples[item][1]

    if len(listOfTuples) != 0:
        xVec = xVec/len(listOfTuples)
        yVec = yVec/len(listOfTuples)
    return(xVec,yVec)

def primeLists(): # readies the libraries with points to begin the simulation
    for y in range(simResolution):
        for x in range(simResolution):
            positionLibrary.append((x*(500 / simResolution) + 415, y*(500 / simResolution) + 135)) # appends a position on the screen
            #positionLibrary.append((random.randint(0,100), random.randint(0,100)))
    for y in range(simResolution):
        for x in range(simResolution):
            nextPositionLibrary.append((x*(500 / simResolution) + 415, y*(500 / simResolution) + 135))
    for item in range(simResolution ** 2):
            velocityLibrary.append((0,0)) # appends a null vector (not moving at the start)
    for item in range(simResolution ** 2):
            nextVelocityLibrary.append((0,0)) # appends a null vector

def createEdgeTable():
    # This script is extremely inefficient, looping every vertex for every other vertex (time complexity: n^2 where n is 100)
    # This function is a very basic way to retrieve an edge table from a point field, based on the distance between points.

    for item in range(len(positionLibrary)):
        thisPos = positionLibrary[item]

        thisLinks = []
        for otherItem in range(len(positionLibrary)): # loops through every item in the library for each item, checking if they are within 15 px
            otherPos = positionLibrary[otherItem]
            if dist(otherPos, thisPos) <= (ceil(750 / simResolution)) and not otherPos == thisPos:
                thisLinks.append(otherItem) # if the point is close enough, it is added to the list of linked points
        
        for link in range(len(thisLinks)): # finally, all linked points are added as edges (tuples of two points) to the edge table
            if not ((thisLinks[link]), item) in edgeTable:
                if not (item, (thisLinks[link])) in edgeTable:
                    edgeTable.append((item, thisLinks[link]))
    
        for item in range(100):
            ecofTable.append(0) # appends a zero coefficient

def createRestingDistanceTable(): # calculates resting distances from initial point positions
    for item in range(len(edgeTable)):
        restingDistanceTable.append(dist(positionLibrary[edgeTable[item][0]],positionLibrary[edgeTable[item][1]]))

def findConnectedFromEdgeTable(point): # takes a point index and returns all points connected
    connected = []
    for item in range(len(edgeTable)): # loops through all edges in edge table
        if point in edgeTable[item]: # if the point in question is in the inspected edge,
            if edgeTable[item].index(point) == 0: # and if the point is the first item in the tuple,
                connected.append(edgeTable[item][1]) # add the second (other) point to the connected points list.
            else:
                connected.append(edgeTable[item][0]) # if not add the first (other) point to the connected points list.

    return connected

def findRestingDistances(point): # takes a point and returns the resting distances of all connected points
    restingDistances = []
    for item in range(len(edgeTable)):
        if point in edgeTable[item]:
            restingDistances.append(item)
    
    return restingDistances

def transformPoint(point, connectedPoints, resting): # applies transformations to the point location based on inputted data

    elasticVectors = []
    for linkedPoint in range(len(connectedPoints)):
        elasticCoefficient = ((dist(positionLibrary[connectedPoints[linkedPoint]], positionLibrary[point])) - restingDistanceTable[resting[linkedPoint]]) * (1 / trueElasticity) # behold, the elastic function

        # the above function is based on the Wikipedia article on Hooke's Law: https://en.wikipedia.org/wiki/Hooke%27s_law which states,
        # "In physics, Hooke's law is an empirical law which states that the force (F) needed to extend or compress a spring by some distance (x) scales linearly with respect to that distance"

        dirToPoint = dirTo(positionLibrary[point], positionLibrary[connectedPoints[linkedPoint]]) # swap if not working
        elasticVector = (elasticCoefficient * cos(dirToPoint), elasticCoefficient * sin(dirToPoint))
        # above is a trig function that takes a direction and magnitude and converts it to an (x,y) vector
        elasticVectors.append(elasticVector)
    
    newTransformVector = addTuplesAsVectors(elasticVectors) # takes all acting elastic forces as vectors and adds them (net force)

    velocityTuple = list(velocityLibrary[point]) # tuples are immutable
    velocityTuple[0] = velocityTuple[0]*dampening + newTransformVector[0] + gravity[0] #+ (random.randint(-100,100))/2000
    velocityTuple[1] = velocityTuple[1]*dampening + newTransformVector[1] + gravity[1] #+ (random.randint(-100,100))/2000


    positionTuple = list(positionLibrary[point]) # tuples are immutable
    positionTuple[0] = positionTuple[0] + (velocityTuple[0])
    positionTuple[1] = positionTuple[1] + (velocityTuple[1])
    if positionTuple[1] > 720:#- positionTuple[0]/2.5: # floor
        positionTuple[1] = 720# - positionTuple[0]/2.5
    #if point < 10: # attachment point
        #positionTuple[1] = 0
        #velocityTuple[0] = 0
        #velocityTuple[1] = 0
    
    nextVelocityLibrary[point] = tuple(velocityTuple) # adds transformations to next frame
    nextPositionLibrary[point] = tuple(positionTuple)



###### MAINLOOP ######

primeLists()
createEdgeTable()
createRestingDistanceTable()
running = True # Runs the game loop
while running:

    screen.fill((0,0,0))

    for pt in range(len(positionLibrary)):
        localX = positionLibrary[pt][0]
        localY = positionLibrary[pt][1]

        connected = findConnectedFromEdgeTable(pt)
        restingDistances = findRestingDistances(pt)

        transformPoint(pt, connected, restingDistances)


        pygame.draw.circle(screen, (255,255,255), (localX, localY), 5)
        #pygame.draw.line(screen, (255,255,0), (640,0), (640,720), 3) # Guiding Line 1
        #pygame.draw.line(screen, (255,255,0), (0,360), (1280,360), 3) # Guiding Line 2


    for edge in range(len(edgeTable)):
        localX1 = positionLibrary[edgeTable[edge][0]][0]
        localY1 = positionLibrary[edgeTable[edge][0]][1]

        localX2 = positionLibrary[edgeTable[edge][1]][0]
        localY2 = positionLibrary[edgeTable[edge][1]][1]

        localECof = (dist((localX1, localY1), (localX2, localY2)) - restingDistanceTable[edge]) * (1 / trueElasticity) # behold, the elastic function again
        ecofTable[edge] = localECof
        #avgECof = sum(ecofTable) / len(ecofTable)

        #pygame.draw.aaline(screen, ((510/(1+exp(0.5 * ((localECof -0.8) - 0.5)**2))),(510/(1+exp(0.5 * ((sqrt(abs(localECof))))**2))),(510/(1+exp(0.5 * ((0 - localECof - 0.8) - 0.5)**2)))), (localX1 ,localY1), (localX2 ,localY2), 5)
        pygame.draw.aaline(screen, (255, 255, 255), (localX1 ,localY1), (localX2 ,localY2), 5)

    positionLibrary = copy.deepcopy(nextPositionLibrary) # cascades next frame into current frame
    velocityLibrary = copy.deepcopy(nextVelocityLibrary)

    #text = font.render("avgECof: " + str((round(avgECof*1000000))/1000), True, (255, 255, 255))
    #text_rect = text.get_rect()
    #screen.blit(text, text_rect)

    for event in pygame.event.get(): # checks if program is quit, if so stops the code
        if event.type == pygame.QUIT:
            running = False
    # runs framerate wait time
    clock.tick(fps)
    # update the screen
    pygame.display.update()

# quit Pygame
pygame.quit()