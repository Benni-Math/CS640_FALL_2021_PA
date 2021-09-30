
import numpy as np
from numpy.random import default_rng
from NetworkManager import NetworkManager
from EnvironmentState import State

rng = default_rng()

LEFT = bytes.fromhex('00')
UP = bytes.fromhex('01')
RIGHT =  bytes.fromhex('02')
DOWN =  bytes.fromhex('03')
NOOP =  bytes.fromhex('04')

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
        t = 0
        for i in range(1, len(self.state.body)):
            t += self.state.body[i].length

        distSum = 0
        for i in range(1, len(self.state.body) - 1):
            t = t - (self.state.body[i].length / 2)
            # finding midpoint of line
            x = (self.state.body[i].x1 + self.state.body[i].x2) / 2
            y = (self.state.body[i].y1 + self.state.body[i].y2) / 2
            # or just setting to the top of the line
            # x = self.state.body[i].x1
            # y = self.state.body[i].y1
            # want a weight of headDist/tailDist
            headDist = taxiDist(x1, y1, x, y)
            try:
                distSum = distSum + (2*headDist / (t * i))
            except:
                continue
            t = t - (self.state.body[i].length / 2)

        return distSum

    def collision(self, x1, y1):
        for line in self.state.body:
            dist1 = taxiDist(x1, y1, line.x1, line.y1)
            dist2 = taxiDist(x1, y1, line.x2, line.y2)

            if dist1+dist2 == line.length:
                return True

        return False
    
    
    
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
        self.foodHeadDist = 1401
        pass
    
    #Returns next command selected by the agent.
    def getNextCommand(self):
        #TODO Implement an Intelligent agent that plays the game
        # Hint You will require a collision detection function.

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

        self.foodHeadDist = self.foodDist(x1=self.state.body[0].x1, y1=self.state.body[0].y1)

        heuristicSum = {'00': 0, '01': 0, '02': 0, '03': 0}

        # putting foodDist weight into heuristicSum
        for key in self.options:
            weight = self.foodDist(x1=self.options[key][0], y1=self.options[key][1])
            try:
                weight = (3*self.foodHeadDist) / weight
            except:
                continue
            heuristicSum[key] += weight

        # putting tailDist weight into heuristicSum
        for key in self.options:
            weight = self.tailDist(x1=self.options[key][0], y1=self.options[key][1])
            heuristicSum[key] += weight

        # Collision function call
        for key in self.options:
            if self.collision(x1=self.options[key][0], y1=self.options[key][1]):
                heuristicSum[key] = 0
            # detect walls
            # if self.options[key][0] == 0 or self.options[key][0] == 400 or self.options[key][1] == 0 or self.options[key][1] == 300:
            #     heuristicSum[key] = 0

        # setting the favored choice
        # choice = max(self.optionsProb, key=self.optionsProb.get)
        choice = max(heuristicSum, key=heuristicSum.get)
        if heuristicSum[choice] == 0:
            return NOOP
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
