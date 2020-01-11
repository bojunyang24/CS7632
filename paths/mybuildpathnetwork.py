'''
 * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.
 * Originally developed by Mark Riedl.
 * Last edited by Mark Riedl 05/2015
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
'''

import sys, pygame, math, numpy, random, time, copy, operator
from pygame.locals import *

from constants import *
from utils import *
from core import *

'''
Modify mybuildpathnetwork.py and complete the myBuildPathNetwork() function. myBuildPathNetwork() takes in a list of pathnodes,
a reference to the GameWorld object, and a reference to the agent doing the navigation. myBuildPathNetwork() must return a list of
lines between any path nodes that should be considered adjacent. The list of lines must be computed such that each line originates
and terminates at a path node (use shallow copies so the game engine can correlate the list of pathnodes and the list of edges) and
an agent following the line will not collide with any obstacle.
'''

# Creates the path network as a list of lines between all path nodes that are traversable by the agent.
def myBuildPathNetwork(pathnodes, world, agent = None):
	lines = []
	### YOUR CODE GOES BELOW HERE ###
	obstacleLines = world.getLines()
	agentRadius = agent.getMaxRadius()
	for i in range(len(pathnodes)):
		for j in range(i, len(pathnodes)):
			line = (pathnodes[i], pathnodes[j])
			collision = False
			for k in range(len(obstacleLines)):
				if rayTrace(obstacleLines[k][0], obstacleLines[k][1], line):
					collision = True
				if minimumDistance(line, obstacleLines[k][0]) <= agentRadius or minimumDistance(line, obstacleLines[k][1]) <= agentRadius:
					collision = True
			if not collision:
				lines.append(line)
			# lines.append(line)
	### YOUR CODE GOES ABOVE HERE ###
	return lines
