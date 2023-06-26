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

font = pygame.font.Font(None, 36)

###### INITIALIZE ######
# Jelly
positionLibrary = [] # bank of positions of all the points
nextPositionLibrary = [] # buffer of the next frame's point positions
oldPositionLibrary = [] # buffer of the last frame's point positions, used for calculating intersections of line segments
velocityLibrary = [] # bank of velocities of all the points
nextVelocityLibrary = [] # buffer of the next frame's point velocities
edgeTable = [] # bank of all edges, stored as pairs of point indices
restingDistanceTable = [] # reference table of all the resting distances of the edges
ecofTable = [] # bank of all edges' elastic coefficients

# Environment
lineLibrary = [] # list of quad-tuples that creates the shape of the ground, format = (x1, y1, x2, y2)
normalsLibrary = [] # list of whether or not the normals of each line segment is flipped from the assumed direction, format (1) or (0)
pointSignsLibrary = [] # list of n-tuples that store each point's "side" relationship with each line segment, format = (0,0,0,0...)
sampleBuffer = [] # empty list that initializes the values for the line interactions of every point, the length is equal to the length of line library
passedPoints = [] # constantly updating list of points that have passed through a line segment in the past frame, format = (pointIndex, lineIndex)

###### VARIABLES ######
gravity = (0, 0.15)
#restingDistance = 10

# elasticity = 0.5
simResolution = 10
trueElasticity = 0.5
dampening = 0.99
scale = 500
momentum = 0
denominator = 0.001

# test ground state

# Left Half Platform
#lineLibrary.append((0, 600, 640, 600))

# Tilt to Left
#lineLibrary.append((0, 720, 1280, 600))

# Tilt to Right
lineLibrary.append((0, 550, 1280, 720))

# Right Wall
#lineLibrary.append((1000, 720, 1280, 0))


fps = 60
clock = pygame.time.Clock()

###### OPERATOR FUNCTIONS ######

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
        return (x, y)  # No intersection within line segments (lines are not parallel, but they don't intersect in the specified segments)

###### MAIN FUNCTIONS ######

def primeLists(): # readies the libraries with points to begin the simulation
    for y in range(simResolution):
        for x in range(simResolution):
            positionLibrary.append((x*(500 / simResolution) + (640 - (simResolution - 1) / 2 * (scale / simResolution)), y*(500 / simResolution) + (360 - (simResolution - 1) / 2 * (scale / simResolution)))) # appends a position on the screen
            #positionLibrary.append((random.randint(0,100), random.randint(0,100)))
    for y in range(simResolution):
        for x in range(simResolution):
            nextPositionLibrary.append((x*(500 / simResolution) + (640 - (simResolution - 1) / 2 * (scale / simResolution)), y*(500 / simResolution) + (360 - (simResolution - 1) / 2 * (scale / simResolution))))
            oldPositionLibrary.append((x*(500 / simResolution) + (640 - (simResolution - 1) / 2 * (scale / simResolution)), y*(500 / simResolution) + (360 - (simResolution - 1) / 2 * (scale / simResolution))))
    for item in range(simResolution ** 2):
            velocityLibrary.append((0,0)) # appends a null vector (not moving at the start)
    for item in range(simResolution ** 2):
            nextVelocityLibrary.append((0,0)) # appends a null vector



    for i in range(len(lineLibrary)): # generates a sample buffer that is the length of the line library, which allows each point to store its status with every line
        sampleBuffer.append(True)

    for i in range(simResolution ** 2):
        pointSignsLibrary.append(copy.deepcopy(sampleBuffer))

    for i in lineLibrary:
        normalsLibrary.append(False)

def createEdgeTable():
    # This script is extremely inefficient, looping every vertex for every other vertex (time complexity: n^2 where n is 100) however it runs only once so it is ok.
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

def side(point, line, flipNormal): # tells if a point is above or below a line, defined as an extension of a line segment
    pointX = point[0]
    pointY = point[1]

    lineX1 = line[0]
    lineY1 = line[1]
    lineX2 = line[2]
    lineY2 = line[3]

    vectorAB = (lineX2 - lineX1, lineY2 - lineY1)
    vectorAP = (pointX - lineX1, pointY - lineY1)
    crossProduct = vectorAB[0] * vectorAP[1] - vectorAB[1] * vectorAP[0]
    crossProductIsNeg = crossProduct < 0

    return (crossProductIsNeg) ^ (flipNormal) # if the cross product of the vectors AP and AB is less than 0, the point is above the line, but this can be flipped if the normal vector is flipped

def lineCollisions():
    global pointSignsLibrary
    global passedPoints
    passedPoints = [] # clears the current passed points to make new ones (hence, "constantly refreshing")
    ln = 0
    for line in lineLibrary: # loops through every line
        pt = 0
        for point in positionLibrary: # loops through every point
            if point[0] > line[0] and point[0] < line[2]:
                if pointSignsLibrary[pt][ln] != side(point, line, normalsLibrary[ln]):
                    passedPoints.append((pt, ln))
            pointSignsLibrary[pt][ln] = side(point, line, normalsLibrary[ln])
            
            pt += 1
        
        ln += 1


def transformPoint(point, connectedPoints, resting): # applies transformations to the point location based on inputted data
    global denominator

    elasticVectors = []
    for linkedPoint in range(len(connectedPoints)):
        ecof = ((dist(positionLibrary[connectedPoints[linkedPoint]], positionLibrary[point])) - restingDistanceTable[resting[linkedPoint]]) * (1 / trueElasticity) # behold, the elastic function

        # the above function is based on the Wikipedia article on Hooke's Law: https://en.wikipedia.org/wiki/Hooke%27s_law which states,
        # "In physics, Hooke's law is an empirical law which states that the force (F) needed to extend or compress a spring by some distance (x) scales linearly with respect to that distance"

        dirToPoint = dirTo(positionLibrary[point], positionLibrary[connectedPoints[linkedPoint]]) # swap if not working
        elasticVector = (ecof * cos(dirToPoint), ecof * sin(dirToPoint))
        # above is a trig function that takes a direction and magnitude and converts it to an (x,y) vector
        elasticVectors.append(elasticVector)
    
    newTransformVector = addTuplesAsVectors(elasticVectors) # takes all acting elastic forces as vectors and adds them (net force)

    velocityTuple = list(velocityLibrary[point]) # tuples are immutable
    positionTuple = list(positionLibrary[point]) # tuples are immutable

    
    passedPoints = [] # clears the current passed points to make new ones (hence, "constantly refreshing")

    
    nextPointVelocity = [0, 0]
    nextPointPosition = [0, 0]
    ln = 0
    for line in lineLibrary: # loops through every line
        
        if positionTuple[0] > line[0] and positionTuple[0] < line[2]:
            nextPointVelocity[0] = velocityTuple[0] + gravity[0] + newTransformVector[0]
            nextPointVelocity[1] = velocityTuple[1] + gravity[1] + newTransformVector[1]

            nextPointPosition[0] = positionTuple[0] + nextPointVelocity[0]
            nextPointPosition[1] = positionTuple[1] + nextPointVelocity[1]

            if side(nextPointPosition, line, normalsLibrary[ln]) != side(positionTuple, line, normalsLibrary[ln]):
                passedPoints.append((point, ln))
                #positionTuple = nextPointPosition
        #pointSignsLibrary[pt][ln] = side(positionLibrary[point], line, normalsLibrary[ln])
    
        ln += 1
    

    
    velocityTuple[0] += gravity[0]
    velocityTuple[1] += gravity[1]
    velocityTuple[0] += newTransformVector[0]
    velocityTuple[1] += newTransformVector[1]
    
    touchingALine = False
    for line in range(len(lineLibrary)):
        if (point,line) in passedPoints: # or (point,line,1) in passedPoints:
            
            liq = lineLibrary[line]
            rise = liq[3] - liq[1]
            run = liq[2] - liq[0]
            hyp = dist((liq[0],liq[1]),(liq[2],liq[3]))

            '''
            velocityTuple[0] -= newTransformVector[0]
            velocityTuple[1] -= newTransformVector[1]
            velocityTuple[0] -= gravity[0]
            velocityTuple[1] -= gravity[1]
            '''

            momentum = dist((0,velocityTuple[0]),(0,velocityTuple[1]))

            # we have two line segments - one is the line segment that defines the ground, and the other is the line segment that defines the last position the particle was in
            # before intersecting with the ground and the position right after. We need to calculate the intersection point of these two line segments.
            x, y = getIntersectionPoint((oldPositionLibrary[point][0],oldPositionLibrary[point][1],positionLibrary[point][0],positionLibrary[point][1]),(liq))

            positionTuple[1] = y - 3
            positionTuple[0] = x

            #velocityTuple[1] = 0
            #velocityTuple[0] = 0

            velocityTuple[1] -= momentum * (run/hyp) * (run/hyp) + 2
            velocityTuple[0] += momentum * (run/hyp) * (rise/hyp)

            touchingALine = True

    #if positionTuple[1] > 720:#- positionTuple[0]/2.5: # floor
        #positionTuple[1] = 720# - positionTuple[0]/2.5
        #velocityTuple[1] = 0

    '''
        if not True:
            velocityTuple[0] += gravity[0]
            velocityTuple[1] += gravity[1]
            velocityTuple[0] += newTransformVector[0]
            velocityTuple[1] += newTransformVector[1]
        else:   
            if not touchingALine:
                velocityTuple[0] += gravity[0]
                velocityTuple[1] += gravity[1]
                velocityTuple[0] += newTransformVector[0]
                velocityTuple[1] += newTransformVector[1]
    '''

    positionTuple[0] = positionTuple[0] + (velocityTuple[0])
    positionTuple[1] = positionTuple[1] + (velocityTuple[1])

    nextVelocityLibrary[point] = copy.deepcopy(tuple(velocityTuple)) # adds transformations to next frame
    nextPositionLibrary[point] = copy.deepcopy(tuple(positionTuple))



###### MAINLOOP ######

primeLists()
createEdgeTable()
createRestingDistanceTable()
running = True # Runs the game loop
while running:

    screen.fill((0,0,0))
    #lineCollisions()

    for pt in range(len(positionLibrary)):
        localX = positionLibrary[pt][0]
        localY = positionLibrary[pt][1]

        connected = findConnectedFromEdgeTable(pt)
        restingDistances = findRestingDistances(pt)

        transformPoint(pt, connected, restingDistances)
        
        for ln in range(len(lineLibrary)):
            pygame.draw.circle(screen, (255,255,255), (localX, localY), 5)
            #if (pt,ln) in passedPoints:
            #    pygame.draw.circle(screen, (255,0,0), (localX, localY), 15)
            #else:
            #    pygame.draw.circle(screen, (255,255,255), (localX, localY), 5)
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
        
        '''
        localX1 = oldPositionLibrary[edgeTable[edge][0]][0]
        localY1 = oldPositionLibrary[edgeTable[edge][0]][1]

        localX2 = oldPositionLibrary[edgeTable[edge][1]][0]
        localY2 = oldPositionLibrary[edgeTable[edge][1]][1]

        localECof = (dist((localX1, localY1), (localX2, localY2)) - restingDistanceTable[edge]) * (1 / trueElasticity) # behold, the elastic function again
        ecofTable[edge] = localECof

        pygame.draw.aaline(screen, (255, 0, 0), (localX1 ,localY1), (localX2 ,localY2), 5)
        '''

    for line in lineLibrary:
        localX1 = line[0]
        localY1 = line[1]

        localX2 = line[2]
        localY2 = line[3]

        pygame.draw.aaline(screen, (255, 255, 255), (localX1 ,localY1), (localX2 ,localY2), 5)

    oldPositionLibrary = copy.deepcopy(positionLibrary)
    positionLibrary = copy.deepcopy(nextPositionLibrary) # cascades next frame into current frame
    velocityLibrary = copy.deepcopy(nextVelocityLibrary)
    


    #text = font.render("denominator: " + str((round(denominator*1000))/1000), True, (255, 255, 255))
    #text_rect = text.get_rect()
    #screen.blit(text, text_rect)

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