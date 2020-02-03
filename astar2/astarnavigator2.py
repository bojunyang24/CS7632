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

import sys, pygame, math, numpy, random, time, copy
from pygame.locals import * 

from constants import *
from utils import *
from core import *

import heapq

###############################
### AStarNavigator2
###
### Creates a path node network and implements the A* algorithm to create a path to the given destination.
			
class AStarNavigator2(PathNetworkNavigator):
	### Finds the shortest path from the source to the destination using A*.
	### self: the navigator object
	### source: the place the agent is starting from (i.e., its current location)
	### dest: the place the agent is told to go to
	def computePath(self, source, dest):
		self.setPath(None)
		### Make sure the next and dist matrices exist
		if self.agent != None and self.world != None: 
			self.source = source
			self.destination = dest
			### Step 1: If the agent has a clear path from the source to dest, then go straight there.
			### Determine if there are no obstacles between source and destination (hint: cast rays against world.getLines(), check for clearance).
			### Tell the agent to move to dest
			if clearShot(source, dest, self.world.getLinesWithoutBorders(), self.world.getPoints(), self.agent):
				self.agent.moveToTarget(dest)
			else:
				### Step 2: If there is an obstacle, create the path that will move around the obstacles.
				### Find the path nodes closest to source and destination.
				start = getOnPathNetwork(source, self.pathnodes, self.world.getLinesWithoutBorders(), self.agent)
				end = getOnPathNetwork(dest, self.pathnodes, self.world.getLinesWithoutBorders(), self.agent)
				if start != None and end != None:
					### Remove edges from the path network that intersect gates
					newnetwork = unobstructedNetwork(self.pathnetwork, self.world.getGates(), self.world)
					closedlist = []
					### Create the path by traversing the pathnode network until the path node closest to the destination is reached
					path, closedlist = astar(start, end, newnetwork)
					if path is not None and len(path) > 0:
						### Determine whether shortcuts are available
						path = shortcutPath(source, dest, path, self.world, self.agent)
						### Store the path by calling self.setPath()
						self.setPath(path)
						if self.path is not None and len(self.path) > 0:
							### Tell the agent to move to the first node in the path (and pop the first node off the path)
							first = self.path.pop(0)
							self.agent.moveToTarget(first)
		return None
		
	### Called when the agent gets to a node in the path.
	### self: the navigator object
	def checkpoint(self):
		myCheckpoint(self)
		return None

	### This function gets called by the agent to figure out if some shortcuts can be taken when traversing the path.
	### This function should update the path and return True if the path was updated.
	def smooth(self):
		return mySmooth(self)

	def update(self, delta):
		myUpdate(self, delta)


### Removes any edge in the path network that intersects a worldLine (which should include gates).
def unobstructedNetwork(network, worldLines, world):
	newnetwork = []
	for l in network:
		hit = rayTraceWorld(l[0], l[1], worldLines)
		if hit == None:
			newnetwork.append(l)
	return newnetwork



### Returns true if the agent can get from p1 to p2 directly without running into an obstacle.
### p1: the current location of the agent
### p2: the destination of the agent
### worldLines: all the lines in the world
### agent: the Agent object
def clearShot(p1, p2, worldLines, worldPoints, agent):
    ### YOUR CODE GOES BELOW HERE ###
	path = (p1, p2)
	agentRadius = agent.getMaxRadius()
	for line in worldLines:
		assert len(line) == 2
		if rayTrace(line[0], line[1], path) or minimumDistance(path, line[0]) <= agentRadius or minimumDistance(path, line[1]) <= agentRadius:
			return False
	return True
    ### YOUR CODE GOES ABOVE HERE ###

### Given a location, find the closest pathnode that the agent can get to without collision
### agent: the agent
### location: the location to check from (typically where the agent is starting from or where the agent wants to go to) as an (x, y) point
### pathnodes: a list of pathnodes, where each pathnode is an (x, y) point
### world: pointer to the world
def getOnPathNetwork(location, pathnodes, worldLines, agent):
	node = None
	### YOUR CODE GOES BELOW HERE ###
	reachable = []
	heapq.heapify(reachable)
	for node in pathnodes:
		if clearShot(location, node, worldLines, worldLines, agent):
			heapq.heappush(reachable, (distance(location, node), node))
		heapq.heappush(reachable, (distance(location, node), node))
	if len(reachable) > 0:
		return reachable[0][1]
	else:
		return None
	### YOUR CODE GOES ABOVE HERE ###
	return None



### Implement the a-star algorithm
### Given:
### Init: a pathnode (x, y) that is part of the pathnode network
### goal: a pathnode (x, y) that is part of the pathnode network
### network: the pathnode network
### Return two values: 
### 1. the path, which is a list of states that are connected in the path network
### 2. the closed list, the list of pathnodes visited during the search process
def astar(init, goal, network):
	path = []
	open = []
	closed = []
	### YOUR CODE GOES BELOW HERE ###
	### Node: (heuristic, {(x,y), parentNode})
	### Node: (heuristic, (x,y), parentNode)
	heapq.heapify(open)
	curr = (distance(init, goal), init, init)
	heapq.heappush(open, curr)
	gs = {init: 0}
	### curr[1] is the (x,y) of current node
	while len(open) > 0 and curr[1] != goal:
		curr = heapq.heappop(open)
		if curr[1] == goal:
			prev = curr[2]
			while prev != curr[1]:
				path.append(curr[1])
				curr = prev
				prev = curr[2]
			path.reverse()
			return path, closed
		if curr[1] not in closed:
			closed.append(curr[1])
		neighbors = getNeighbors(curr[1], network)
		for neighbor in neighbors:
			if neighbor not in closed:
				neighbor_g = gs[curr[1]] + distance(curr[1], neighbor)
				if neighbor not in gs or neighbor_g < gs[neighbor]:
					gs[neighbor] = neighbor_g
					f = neighbor_g + distance(neighbor, goal)
					heapq.heappush(open, (f, neighbor, curr))
	if curr[1] == goal:
		prev = curr[2]
		while prev != curr[1]:
			path.append(curr[1])
			curr = prev
			prev = curr[2]
		path.reverse()
	return path, closed

def getNeighbors(node, network):
	neighbors = []
	for path in network:
		if path[0] == node or path[1] == node:
			neighbors.append(path[1] if path[0] == node else path[0])
			# n1, n2 = (path[1], path[0]) if path[1] == node else (path[0], path[1])
	return neighbors


def myUpdate(nav, delta):
	### YOUR CODE GOES BELOW HERE ###
	print('myupdate')
	# gates = nav.world.getGates()
	# if not clearShot(nav.agent.position, nav.agent.moveTarget, gates, gates, nav.agent):
	# 	nav.path, _ = astar(nav.agent.position, nav.destination, unobstructedNetwork(nav.pathnetwork, nav.world.getGates(), nav.world))
	### YOUR CODE GOES ABOVE HERE ###
	return None




def myCheckpoint(nav):
	### YOUR CODE GOES BELOW HERE ###
	print('mycheckpoint')
	# gates = nav.world.getGates()
	# if not clearShot(nav.agent.position, nav.agent.moveTarget, gates, gates, nav.agent):
	# 	nav.agent.stop()
	### YOUR CODE GOES ABOVE HERE ###
	return None







### This function optimizes the given path and returns a new path
### source: the current position of the agent
### dest: the desired destination of the agent
### path: the path previously computed by the A* algorithm
### world: pointer to the world
def shortcutPath(source, dest, path, world, agent):
	path = copy.deepcopy(path)
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES BELOW HERE ###
	return path


### This function changes the move target of the agent if there is an opportunity to walk a shorter path.
### This function should call nav.agent.moveToTarget() if an opportunity exists and may also need to modify nav.path.
### nav: the navigator object
### This function returns True if the moveTarget and/or path is modified and False otherwise
def mySmooth(nav):
	### YOUR CODE GOES BELOW HERE ###
	
	### YOUR CODE GOES ABOVE HERE ###
	return False

