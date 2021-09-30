
import numpy as np
import math
from numpy.random import default_rng
from NetworkManager import NetworkManager
from EnvironmentState import State

rng = default_rng()

LEFT = bytes.fromhex('00')
UP = bytes.fromhex('01')
RIGHT =  bytes.fromhex('02')
DOWN =  bytes.fromhex('03')
NOOP =  bytes.fromhex('04')

global turns
turns = []

# a general Manhattan distance function
def taxiDist(x1, y1, x2, y2):
    x = abs(x1 - x2)
    # need to take "wall teleportation" into account
    if x > 200:
        x = 400 - x

    y = abs(y1 - y2)
    # need to take "wall teleportation" into account
    if y > 150:
        y = 300 - y

    # calculating Manhattan distance (a.k.a. taxi distance)
    dist = x + y
    return dist

class Controller:

    # Helper functions for my agent
    def foodDist(self, x1, y1):
        dist = taxiDist(x1, y1, self.state.food[0], self.state.food[1])
        return dist

    def tailDist(self, x1, y1):
        # keeping track of length-to-tail on snake body
        t = taxiDist(x1, y1, self.state.body[0].x1, self.state.body[0].y1)
        diff = []
        for i in range(0, len(self.state.body)):
            diff.append(t-taxiDist(x1, y1, self.state.body[i].x1, self.state.body[i].y1))
            t += self.state.body[i].length

        distSum = max(diff)
        distIndex = diff.index(distSum)
        distSum = taxiDist(x1, y1, self.state.body[distIndex].x1, self.state.body[distIndex].y1)
        # "expected value" calculation
        # for i in range(1, math.floor(math.log(len(self.state.body), 2))):
        #     x = self.state.body[2 ** i].x1
        #     y = self.state.body[2 ** i].y1
        #
        #     distSum += (taxiDist(x1, y1, x, y) / (2**i))
        # midpoint calculation
        # for i in range(1, len(self.state.body) - 1):
        #     t = t - (self.state.body[i].length / 2)
        #     # finding midpoint of line (need to take into account wall tp)
        #     x = (self.state.body[i].x1 + self.state.body[i].x2) / 2
        #     y = (self.state.body[i].y1 + self.state.body[i].y2) / 2
        #     # or just setting to the top of the line
        #     # x = self.state.body[i].x1
        #     # y = self.state.body[i].y1
        #     # want a weight of headDist/tailDist
        #     headDist = taxiDist(x1, y1, x, y)
        #     try:
        #         distSum = distSum + ((t*i)/(2*headDist))
        #     except:
        #         pass
        #     t = t - (self.state.body[i].length / 2)

        return distSum

    def collision(self, x1, y1):
        for line in self.state.body:
            dist1 = taxiDist(x1, y1, line.x1, line.y1)
            dist2 = taxiDist(x1, y1, line.x2, line.y2)

            if dist1+dist2 == line.length:
                return True

        return False

    # def lineCollision(self, x1, y1, x1_incr, y1_incr, steps):
    #     x = x1
    #     y = y1
    #     while (x<400 and x>=0) and (y<300 and y>=0) and (steps<len(self.state.body)):
    #         if self.collision(x, y):
    #             return steps
    #         x += x1_incr
    #         y += y1_incr
    #         steps += 1
    #
    #     if steps == len(self.state.body):
    #         return 700
    #
    #     if x==400:
    #         return steps + self.lineCollision(0, y, x1_incr, y1_incr)
    #     elif y==300:
    #         return steps + self.lineCollision(x, 0, x1_incr, y1_incr)
    #
    #     return steps

    def numLR(self):
        POV = []
        for i in range(1, len(turns)):
            if turns[-(i + 1)] == 3:
                if turns[-(i + 1)] - turns[-i] == 1:
                    POV.append('L')
                else:
                    POV.append('R')
            elif turns[-i - 1] == 0:
                if (turns[-(i + 1)] - turns[-i]) == -1:
                    POV.append('R')
                else:
                    POV.append('L')
            elif (turns[-(i + 1)] - turns[-i]) == -1:
                POV.append('R')
            else:
                POV.append('L')

        sumL = 0
        sumR = 0
        for i in range(0,min(10, len(POV))):
            if POV[i] == 'L':
                sumL += 1
            else:
                sumR += 1

        return sumL, sumR

    
    
    def __init__(self,ip='localhost',port=4668):
        #Do not Modify
        self.networkMgr=NetworkManager()
        State.col_dim,State.row_dim=self.networkMgr.initiateConnection(ip,port) # Initialize network manager and set environment dimensions
        self.state=State() # Initialize empty state
        self.myInit() # Initialize custom variables
        pass

    #define your variables here
    def myInit(self):
        #TODO
        self.options = {}
        self.foodHeadDist = 700
        pass
    
    #Returns next command selected by the agent.
    def getNextCommand(self):
        #TODO Implement an Intelligent agent that plays the game
        # Hint You will require a collision detection function.

        global turns
        # setting options and foodHeadDist
        self.options = {'00': (self.state.body[0].x1 - 1, self.state.body[0].y1),
                        '01': (self.state.body[0].x1, self.state.body[0].y1 - 1),
                        '02': (self.state.body[0].x1 + 1, self.state.body[0].y1),
                        '03': (self.state.body[0].x1, self.state.body[0].y1 + 1)}

        if (self.state.body[0].y1_incr == 1):
            del self.options['01']
        elif (self.state.body[0].y1_incr == -1):
            del self.options['03']
        elif (self.state.body[0].x1_incr == 1):
            del self.options['02']
        elif (self.state.body[0].x1_incr == -1):
            del self.options['00']

        # Collision function call
        dKeys = []
        for key in self.options:
            if self.collision(x1=self.options[key][0], y1=self.options[key][1]):
                dKeys.append(key)
        for key in dKeys:
            del self.options[key]

        # "loop detection"
        if len(turns) > 2:
            LR = self.numLR()
            if LR[0] > LR[1]:
                if turns[-1] == 0 and '03' in self.options.keys():
                    del self.options['03']
                if turns[-1] == 1 and '00' in self.options.keys():
                    del self.options['00']
                if turns[-1] == 2 and '01' in self.options.keys():
                    del self.options['01']
                if turns[-1] == 3 and '02' in self.options.keys():
                    del self.options['02']
            elif LR[1] > LR[0]:
                if turns[-1] == 0 and '01' in self.options.keys():
                    del self.options['01']
                if turns[-1] == 1 and '02' in self.options.keys():
                    del self.options['02']
                if turns[-1] == 2 and '03' in self.options.keys():
                    del self.options['03']
                if turns[-1] == 3 and '00' in self.options.keys():
                    del self.options['00']


        # setting straight-line distance to body in direction
        # lineColl = {}
        # for key in self.options:
        #     x1_incr = self.options[key][0] - self.state.body[0].x1
        #     y1_incr = self.options[key][1] - self.state.body[0].y1
        #     lineColl[key] = self.lineCollision(self.options[key][0], self.options[key][1], x1_incr, y1_incr, 0)

        self.foodHeadDist = self.foodDist(x1=self.state.body[0].x1, y1=self.state.body[0].y1)

        heuristicSum = {'04': float('inf')}
        # putting foodDist weight into heuristicSum
        for key in self.options:
            weight = self.foodDist(x1=self.options[key][0], y1=self.options[key][1])
            heuristicSum[key] = weight

        bodyDet = {'04': 0}
        # putting tailDist weight in
        for key in self.options:
            weight = self.tailDist(x1=self.options[key][0], y1=self.options[key][1])
            bodyDet[key] = weight


        # setting the favored choice
        # choice = min(heuristicSum, key=heuristicSum.get)
        choice = '04'
        for key in self.options:
            if heuristicSum[key] < bodyDet[key] and heuristicSum[key] < heuristicSum[choice]:
                choice = key
        if choice == '04':
            # if heuristicSum[choice] < bodyDet[choice]:
            choice = max(bodyDet, key=bodyDet.get)

        # appending choice data to our turn history
        turns.append(int(choice[1]))
        if len(turns) > 1:
            if turns[-1] == turns[-2]:
                turns = turns[:-1]
        if self.state.body[-1].length == 1:
            turns = turns[1:]

        return bytes.fromhex(choice)

    def control(self):
        #Do not modify the order of operations.
        # Get current state, check exit condition and send next command.
        while(True):
            # 1. Get current state information from the server
            self.state.setState(self.networkMgr.getStateInfo())
            # 2. Check Exit condition
            if self.state.food==None:
                break
            # 3. Send next command
            self.networkMgr.sendCommand(self.getNextCommand())
        



cntrl=Controller()
cntrl.control()
