
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
    # calculates the taxicab distance from (x1, y1) to the food
    def foodDist(self, x1, y1):
        dist = taxiDist(x1, y1, self.state.food[0], self.state.food[1])
        return dist

    # calculates a weighted distance to the body
    def tailDist(self, x1, y1):
        # keeping track of length-to-tail on snake body
        t = 0
        for i in range(1, len(self.state.body)):
            t += self.state.body[i].length

        distSum = 0
        for i in range(1,math.floor(math.log(len(self.state.body), 2))):
            x = self.state.body[2^i].x1
            y = self.state.body[2^i].y1
            try:
                distSum += t/((2^i)*(taxiDist(x1, y1, x, y)))
            except:
                distSum += t/(2^(i+1))

        # x = self.state.body[len(self.state.body) // 2].x1
        # y = self.state.body[len(self.state.body) // 2].y1
        # try:
        #     distSum += t/(taxiDist(x1, y1, x, y))/2
        # except:
        #     distSum += t/2
        # if len(self.state.body) >= 4:
        #     x = self.state.body[len(self.state.body) // 4].x1
        #     y = self.state.body[len(self.state.body) // 4].y1
        #     try:
        #         distSum += t / (taxiDist(x1, y1, x, y)) / 4
        #     except:
        #         distSum += t / 4

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
        #         distSum += (headDist)
        #         # distSum = distSum + ((t * i)/(2*headDist))
        #     except:
        #         pass
        #     t = t - (self.state.body[i].length / 2)

        return distSum

    # detects collisions based on taxicab distance, since our snake only moves in "taxicab lines"
    def collision(self, x1, y1):
        for line in self.state.body:
            dist1 = taxiDist(x1, y1, line.x1, line.y1)
            dist2 = taxiDist(x1, y1, line.x2, line.y2)

            if dist1+dist2 == line.length:
                return True

        return False

    # finds the number of left and right turns in snake body -- returns the ratio L/R
    def numLR (self):
        L = 0
        R = 0
        # POV = []
        for i in range(1, len(turns)):
            if turns[i-1] == 3:
                if turns[i-1]-turns[i] == 1:
                    L += 1
                    # POV.append('L')
                else:
                    R += 1
                    # POV.append('R')
            elif turns[i-1] == 0:
                if (turns[i - 1] - turns[i]) == -1:
                    R += 1
                    # POV.append('R')
                else:
                    L += 1
                    # POV.append('L')
            elif (turns[i-1]-turns[i]) == -1:
                R += 1
                # POV.append('R')
            else:
                L += 1
                # POV.append('L')

        return L, R
    
    
    
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
        global turns
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
        Dkeys = []
        for key in self.options:
            if self.collision(x1=self.options[key][0], y1=self.options[key][1]):
                Dkeys.append(key)
                
        for key in Dkeys:
            del self.options[key]
        
        self.foodHeadDist = self.foodDist(x1=self.state.body[0].x1, y1=self.state.body[0].y1)

        heuristicSum = {}
        for key in self.options:
            heuristicSum[key] = 0
        if heuristicSum=={}:
            return NOOP


        # putting tailDist weight into heuristicSum
        for key in self.options:
            weight = self.tailDist(x1=self.options[key][0], y1=self.options[key][1])
            heuristicSum[key] += weight

        # weighs left and right turn in heuristicSum based on numLR ratio of L/R
        if len(turns) > 1:
            weights = self.numLR()
            if weights[0] > weights[1]:
                w = weights[0]-weights[1]
                if turns[-1] == 0 and '03' in heuristicSum.keys():
                    heuristicSum['03'] *= w
                if turns[-1] == 1 and '00' in heuristicSum.keys():
                    heuristicSum['00'] *= w
                if turns[-1] == 2 and '01' in heuristicSum.keys():
                    heuristicSum['01'] *= w
                if turns[-1] == 3 and '02' in heuristicSum.keys():
                    heuristicSum['02'] *= w
            elif weights[1] > weights[0]:
                w = weights[1]-weights[0]
                if turns[-1] == 0 and '01' in heuristicSum.keys():
                    heuristicSum['01'] *= w
                if turns[-1] == 1 and '02' in heuristicSum.keys():
                    heuristicSum['02'] *= w
                if turns[-1] == 2 and '03' in heuristicSum.keys():
                    heuristicSum['03'] *= w
                if turns[-1] == 3 and '00' in heuristicSum.keys():
                    heuristicSum['00'] *= w
            # if turns[-1] == 0:
            #     if '03' in heuristicSum.keys():
            #         heuristicSum['03'] += weights[0]/len(self.state.body)
            #     if '01' in heuristicSum.keys():
            #         try:
            #             heuristicSum['01'] += weights[1]/len(self.state.body)
            #         except Exception:
            #             pass
            # elif turns[-1] == 1:
            #     if '00' in heuristicSum.keys():
            #         heuristicSum['00'] += weights[0]/len(self.state.body)
            #     if '02' in heuristicSum.keys():
            #         try:
            #             heuristicSum['02'] += weights[1]/len(self.state.body)
            #         except Exception:
            #             pass
            # elif turns[-1] == 2:
            #     if '01' in heuristicSum.keys():
            #         heuristicSum['01'] += weights[0]/len(self.state.body)
            #     if '03' in heuristicSum.keys():
            #         try:
            #             heuristicSum['03'] += weights[1]/len(self.state.body)
            #         except Exception:
            #             pass
            # elif turns[-1] == 3:
            #     if '02' in heuristicSum.keys():
            #         heuristicSum['02'] += weights[0]/len(self.state.body)
            #     if '00' in heuristicSum.keys():
            #         try:
            #             heuristicSum['00'] += weights[1]/len(self.state.body)
            #         except Exception:
            #             pass


        # putting foodDist weight into heuristicSum
        for key in self.options:
            weight = self.foodDist(x1=self.options[key][0], y1=self.options[key][1])
            try:
                weight =  weight / (self.foodHeadDist)
            except:
                pass

            heuristicSum[key] += weight


        # setting the favored choice
        # choice = max(self.optionsProb, key=self.optionsProb.get)
        choice = min(heuristicSum, key=heuristicSum.get)
        if heuristicSum[choice] == 0:
            return NOOP
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
