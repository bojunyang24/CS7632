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
from moba import *

class MyMinion(Minion):
	
	def __init__(self, position, orientation, world, image = NPC, speed = SPEED, viewangle = 360, hitpoints = HITPOINTS, firerate = FIRERATE, bulletclass = SmallBullet):
		Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
		self.states = [Idle]
		### Add your states to self.states (but don't remove Idle)
		### YOUR CODE GOES BELOW HERE ###
		self.states.append(Seek)
		self.states.append(Destroy)
		self.states.append(Protect)
		### YOUR CODE GOES ABOVE HERE ###

	def start(self):
		Minion.start(self)
		self.changeState(Idle)





############################
### Idle
###
### This is the default state of MyMinion. The main purpose of the Idle state is to figure out what state to change to and do that immediately.

class Idle(State):
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		# stop moving
		self.agent.stopMoving()
	
	def execute(self, delta = 0):
		State.execute(self, delta)
		### YOUR CODE GOES BELOW HERE ###
		towers = self.agent.world.getEnemyTowers(self.agent.getTeam())
		towers = sorted(towers, key=(lambda x:distance(x.getLocation(), self.agent.getLocation())))
		targets = towers + self.agent.world.getEnemyBases(self.agent.getTeam())
		enemyMinions = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		# if more than 2 teammates alive, attack objectives
		if len(self.agent.world.getNPCsForTeam(self.agent.getTeam())) > 1:
			if len(targets) > 0:
				self.agent.changeState(Seek, targets[0])
		else:
			self.agent.changeState(Protect, enemyMinions[0])
		### YOUR CODE GOES ABOVE HERE ###
		return None

##############################
### Taunt
###
### This is a state given as an example of how to pass arbitrary parameters into a State.
### To taunt someome, Agent.changeState(Taunt, enemyagent)

class Taunt(State):

	def parseArgs(self, args):
		self.victim = args[0]

	def execute(self, delta = 0):
		if self.victim is not None:
			print("Hey " + str(self.victim) + ", I don't like you!")
		self.agent.changeState(Idle)

##############################
### YOUR STATES GO HERE:

class Seek(State):

	def __init__(self, agent, args=[]):
		State.__init__(self, agent, args)
		self.target = args[0]

	def enter(self, oldstate):
		State.enter(self, oldstate)
		if self.target is not None:
			self.agent.navigateTo(self.target.getLocation())

	def execute(self, delta=0):
		State.execute(self, delta)
		if self.target is not None:
			for m in self.agent.getVisibleType(Minion):
				if m.getTeam() != self.agent.getTeam() and distance(m.getLocation(), self.agent.getLocation()) < SMALLBULLETRANGE:
					self.agent.changeState(Destroy, m)
			# attack base
			if self.target in self.agent.getVisibleType(Base) and distance(self.agent.getLocation(), self.target.getLocation()) < SMALLBULLETRANGE:
				self.agent.changeState(Destroy, self.target)
			# attack towers
			elif self.target in self.agent.getVisibleType(Tower) and distance(self.agent.getLocation(), self.target.getLocation()) < SMALLBULLETRANGE:
				self.agent.changeState(Destroy, self.target)
			# if target is destroyed and still have targets left to attack
			elif self.agent.getMoveTarget() == None and self.target is not None:
				self.agent.navigateTo(self.target.getLocation())
	
	def exit(self):
		State.exit(self)
		self.agent.stopMoving()

class Destroy(State):

	def __init__(self, agent, args=[]):
		State.__init__(self, agent, args)
		self.target = args[0]
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		if self.target in self.agent.world.getEnemyBases(self.agent.getTeam()) or self.target in self.agent.world.getEnemyTowers(self.agent.getTeam()):
			if distance(self.agent.getLocation(), self.target.getLocation()) < SMALLBULLETRANGE:
				self.agent.stopMoving()

	def execute(self, delta=0):
		State.execute(self, delta)
		enemyMinions = self.agent.world.getEnemyNPCs(self.agent.getTeam())
		if len(enemyMinions) > 3 and len(self.agent.world.getNPCsForTeam(self.agent.getTeam())) < 6:
			self.agent.changeState(Protect, enemyMinions[0])
		elif self.target is not None and self.target.isAlive() and distance(self.target.getLocation(), self.agent.getLocation()) < SMALLBULLETRANGE:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()
		elif distance(self.target.getLocation(), self.agent.getLocation()) >= SMALLBULLETRANGE:
			self.agent.changeState(Idle)
		else:
			if not self.target.isAlive():
				self.agent.changeState(Idle)

class Protect(State):

	def __init__(self, agent, args=[]):
		State.__init__(self, agent, args)
		self.target = args[0]
	
	def enter(self, oldstate):
		State.enter(self, oldstate)
		if distance(self.target.getLocation(), self.agent.getLocation()) < SMALLBULLETRANGE:
			self.agent.turnToFace(self.target.getLocation())
			self.agent.shoot()
		else:
			self.agent.navigateTo(self.target.getLocation())
	
	def execute(self, delta=0):
		State.execute(self, delta)
		# if teammates are less than 3, change to attacking objectives
		# if len(self.agent.world.getNPCsForTeam(self.agent.getTeam())) < 3:
		# 	self.agent.changeState(Idle)
		# attack the target minion: keep moving towards target minion's location and shoot when in range
		if self.target is not None and self.target.isAlive():
			if distance(self.target.getLocation(), self.agent.getLocation()) < SMALLBULLETRANGE:
				self.agent.turnToFace(self.target.getLocation())
				self.agent.shoot()
			self.agent.navigateTo(self.target.getLocation())
		else:
			if not self.target.isAlive():
				# find new enemy minion to attack
				enemyMinions = self.agent.world.getEnemyNPCs(self.agent.getTeam())
				if len(enemyMinions) > 0:
					self.target = enemyMinions[0]
				else:
					self.agent.changeState(Idle)