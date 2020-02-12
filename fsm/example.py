# uncompyle6 version 3.6.4
# Python bytecode 3.7 (3394)
# Decompiled from: Python 3.7.6 (default, Jan  8 2020, 13:42:34) 
# [Clang 4.0.1 (tags/RELEASE_401/final)]
# Embedded file name: BaselineMinion.py
# Size of source mod 2**32: 5031 bytes
__doc__ = '\n * Copyright (c) 2014, 2015 Entertainment Intelligence Lab, Georgia Institute of Technology.\n * Originally developed by Mark Riedl.\n * Last edited by Mark Riedl 05/2015\n *\n * Licensed under the Apache License, Version 2.0 (the "License");\n * you may not use this file except in compliance with the License.\n * You may obtain a copy of the License at\n *\n *     http://www.apache.org/licenses/LICENSE-2.0\n *\n * Unless required by applicable law or agreed to in writing, software\n * distributed under the License is distributed on an "AS IS" BASIS,\n * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n * See the License for the specific language governing permissions and\n * limitations under the License.\n'
import sys, pygame, math, numpy, random, time, copy
from pygame.locals import *
from constants import *
from utils import *
from core import *
from moba import *

class BaselineMinion(Minion):

    def __init__(self, position, orientation, world, image=NPC, speed=SPEED, viewangle=360, hitpoints=HITPOINTS, firerate=FIRERATE, bulletclass=SmallBullet):
        Minion.__init__(self, position, orientation, world, image, speed, viewangle, hitpoints, firerate, bulletclass)
        self.states = [Idle]
        self.states += [Move, Kill]

    def start(self):
        Minion.start(self)
        self.world.computeFreeLocations(self)
        self.changeState(Idle)


class Idle(State):

    def enter(self, oldstate):
        State.enter(self, oldstate)
        self.agent.stopMoving()

    def execute(self, delta=0):
        State.execute(self, delta)
        targets = self.agent.world.getEnemyTowers(self.agent.getTeam())
        targets = sorted(targets, key=(lambda x: distance(x.getLocation(), self.agent.getLocation())))
        targets = targets + self.agent.world.getEnemyBases(self.agent.getTeam())
        if len(targets) > 0:
            self.agent.changeState(Move, targets[0])


class Taunt(State):

    def parseArgs(self, args):
        self.victim = args[0]

    def execute(self, delta=0):
        if self.victim is not None:
            print('Hey ' + str(self.victim) + ", I don't like you!")
        self.agent.changeState(Idle)


class Move(State):

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
            visibleMinions = self.agent.getVisibleType(Minion)
            targetMinions = []
            for m in visibleMinions:
                if m.getTeam() != self.agent.getTeam():
                    targetMinions.append(m)

            if self.target in self.agent.getVisibleType(Tower) and distance(self.agent.getLocation(), self.target.getLocation()) < SMALLBULLETRANGE:
                self.agent.changeState(Kill, self.target)
            else:
                if self.target in self.agent.getVisibleType(Base) and distance(self.agent.getLocation(), self.target.getLocation()) < SMALLBULLETRANGE:
                    self.agent.changeState(Kill, self.target)
                else:
                    if self.agent.getMoveTarget() == None:
                        if self.target is not None:
                            self.agent.navigateTo(self.target.getLocation())

    def exit(self):
        State.exit(self)
        self.agent.stopMoving()


class Kill(State):

    def __init__(self, agent, args=[]):
        State.__init__(self, agent, args)
        self.target = args[0]

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.target is not None and self.target.isAlive():
            self.agent.turnToFace(self.target.getLocation())
            self.agent.shoot()
        else:
            if self.target.isAlive() == False:
                self.agent.changeState(Idle)


class Heal(State):

    def enter(self, oldstate):
        State.enter(self, oldstate)
        if self.agent.getOwner() is not None:
            self.agent.navigateTo(self.agent.getOwner().getLocation())

    def execute(self, delta=0):
        State.execute(self, delta)
        if self.agent.getHitpoints() == self.agent.getMaxHitpoints():
            self.agent.changeState(Idle)
# okay decompiling BaselineMinion.pyc
