from constants import *
from utils import *
from core import *

import pdb
import copy
from functools import reduce

from statesactions import *

import heapq

############################
## HELPERS

### Return true if the given state object is a goal. Goal is a State object too.
def is_goal(state, goal):
  return len(goal.propositions.difference(state.propositions)) == 0

### Return true if the given state is in a set of states.
def state_in_set(state, set_of_states):
  for s in set_of_states:
    if s.propositions != state.propositions:
      return False
  return True

### For debugging, print each state in a list of states
def print_states(states):
  for s in states:
    ca = None
    if s.causing_action is not None:
      ca = s.causing_action.name
    print(s.id, s.propositions, ca, s.get_g(), s.get_h(), s.get_f())

def stateComapare(self, other):
  return 1

State.__lt__ = stateComapare

############################
### Planner 
###
### The planner knows how to generate a plan using a-star and heuristic search planning.
### It also knows how to execute plans in a continuous, time environment.

class Planner():

  def __init__(self):
    self.running = False              # is the planner running?
    self.world = None                 # pointer back to the world
    self.the_plan = []                # the plan (when generated)
    self.initial_state = None         # Initial state (State object)
    self.goal_state = None            # Goal state (State object)
    self.actions = []                 # list of actions (Action objects)

  ### Start running
  def start(self):
    self.running = True
    
  ### Stop running
  def stop(self):
    self.running = False

  ### Called every tick. Executes the plan if there is one
  def update(self, delta = 0):
    result = False # default return value
    if self.running and len(self.the_plan) > 0:
      # I have a plan, so execute the first action in the plan
      self.the_plan[0].agent = self
      result = self.the_plan[0].execute(delta)
      if result == False:
        # action failed
        print("AGENT FAILED")
        self.the_plan = []
      elif result == True:
        # action succeeded
        done_action = self.the_plan.pop(0)
        print("ACTION", done_action.name, "SUCCEEDED")
        done_action.reset()
    # If the result is None, the action is still executing
    return result

  ### Call back from Action class. Pass through to world
  def check_preconditions(self, preconds):
    if self.world is not None:
      return self.world.check_preconditions(preconds)
    return False

  ### Call back from Action class. Pass through to world
  def get_x_y_for_label(self, label):
    if self.world is not None:
      return self.world.get_x_y_for_label(label)
    return None

  ### Call back from Action class. Pass through to world
  def trigger(self, action):
    if self.world is not None:
      return self.world.trigger(action)
    return False

  ### Generate a plan. Init and goal are State objects. Actions is a list of Action objects
  ### Return the plan and the closed list
  def astar(self, init, goal, actions):
    '''
    curr = (heuristic state, state)
    get to state by state.causing_action from state.parent
    '''
    plan = []    # the final plan. list of actions
    open = []
    heapq.heapify(open)    # heap that holds which state to visit next
    closed = []  # the closed list (already visited states). Holds state objects
    curr = (0, init)
    heapq.heappush(open, curr)
    while len(open) > 0:
      curr = heapq.heappop(open) # get next state to visit
      if goal.propositions.issubset(curr[1].propositions):
        return self.constructPlan(curr[1]), closed
      for new_state in self.possibleStates(curr[1], goal, actions, closed, open):
        if new_state not in closed:
          # check for different actions that bring the final state to the same propositions
          # no need to consider these
          f = new_state.g + new_state.h
          repeat = False
          for s in open:
            if new_state.g==s[1].g and new_state.h == s[1].h and s[1].propositions.issubset(new_state.propositions) and new_state.propositions.issubset(s[1].propositions) and s[1].causing_action == new_state.causing_action:
              repeat = True
          if not repeat:
            heapq.heappush(open, (f, new_state))
      closed.append(curr)
    print('no plan found')
    return plan, closed

  def constructPlan(self, state):
    '''
    uses the causing_action and parent property of finalState to reconstruct plan
    '''
    plan = []
    while state.causing_action != None:
      plan.append(state.causing_action)
      state = state.parent
    plan.reverse()
    return plan

  def possibleStates(self, current_state, goal_state, actions, closed, open):
    '''
    returns list of possible states that can be reached from the current state
    '''
    new_states = []
    for action in actions:
      # since all propositions are positive, preconditions of actions must be a subset of current_state's propositions in order to perform actions
      if action.preconditions.issubset(current_state.propositions):
        propositions = current_state.propositions.difference(action.delete_list)
        propositions = propositions.union(action.add_list)
        new_state = State(propositions)
        new_state.parent = current_state
        new_state.causing_action = action
        new_state.g = current_state.g + action.cost
        new_state.h = self.compute_heuristic(current_state, goal_state, actions)
        new_states.append(new_state)
    return new_states

  ### Compute the heuristic value of the current state using the HSP technique.
  ### Current_state and goal_state are State objects.
  def compute_heuristic(self, current_state, goal_state, actions):
    actions = copy.deepcopy(actions)  # Make a deep copy just in case
    h = len(actions) ** 2                             # heuristic value to return
    edges = []
    dummyStart = Action('dummyStart', [], current_state.propositions, [], 0)
    dummyGoal = Action('dummyGoal', goal_state.propositions, [], [], 0)
    actions.append(dummyStart)
    actions.append(dummyGoal)

    for action1 in actions:
      for action2 in actions:
        if action1 != action2:
          for new_truths in action1.add_list:
            if new_truths in action2.preconditions:
              edges.append(Edge(action1, action2, new_truths, action1.cost))
    
    q = []
    q.append(dummyStart)
    closed = set()
    relaxed_world = dummyStart.add_list # set of relaxed world's propositions
    curr = dummyStart

    while len(q) > 0:
      curr = q.pop(0)
      closed.add(curr.name)
      relaxed_world = relaxed_world.union(curr.add_list)
      for action in actions:
        if action.name not in closed and action.preconditions.issubset(relaxed_world):
          q.append(action)
          closed.add(action.name)
          # calculate max incoming cost
          cost = 0
          for incoming in edges:
            if incoming.pre_action.name in closed and incoming.post_action.name == action.name:
              if incoming.cost > cost:
                cost = incoming.cost
          if action.name == 'dummyGoal':
            return cost
          cost += action.cost
          for outgoing in edges:
            if outgoing.pre_action.name == action.name:
              outgoing.cost = cost
    return h

class Edge():

  def __init__(self, pre_action, post_action, proposition, cost):
    self.pre_action = pre_action
    self.post_action = post_action
    self.proposition = proposition
    self.cost = cost