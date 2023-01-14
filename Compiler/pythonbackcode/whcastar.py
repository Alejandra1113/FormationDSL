import math
from math import inf
from .utils import *
from queue import PriorityQueue
from itertools import chain

class Problem(object):
    def __init__(self, goals=None, **kwds): 
        self.goals=goals
        self.__dict__.update(**kwds)
        
    def actions(self, state):        raise NotImplementedError
    def result(self, state, action): raise NotImplementedError
    def is_goal(self, state):        return state in self.goals
    def action_cost(self, s, a, s1): return 1
    def h(self, node):               return 0
    
    def __str__(self):
        return '{}({!r}, {!r})'.format(
            type(self).__name__, self.goals)


class ViewProblem(Problem):
    def __init__(self, dimx, dimy, *args, **kwargs):
        self.dim_x, self.dim_y = dimx, dimy
        Problem.__init__(self, *args, **kwargs)

    def actions(self, state):
        """The actions executable in this state."""
        x, y = state
        dirs = [(dirvar.name, (I_DIR[dirvar.value - 1], J_DIR[dirvar.value - 1])) for dirvar in DIRECTIONS]
        return [(name, move) for name, move in dirs 
                                    if validMove(x + move[0], y + move[1], self.dim_x, self.dim_y)]

    def result(self, state, action):
        """The state that results from executing this action in this state."""
        x, y = state
        _, (x_dir, y_dir) = action
        return x + x_dir, y + y_dir

    def is_goal(self, state):
        """True if the goal level is in any one of the jugs."""
        return state in self.goals

class FindVertex(ViewProblem):
    def actions(self, state):
        """The actions executable in this state."""
        x, y = state
        dirs = [(dirvar.name, (I_DIR[dirvar.value - 1], J_DIR[dirvar.value - 1])) for dirvar in DIRECTIONS]
        return [(name, move) for name, move in dirs
                                    if validMove(x + move[0], y + move[1], self.dim_x, self.dim_y)]

class FindWithAgent(FindVertex):
    def __init__(self, reservation_table: dict, heigth, width, *args, **kwargs):
        self.reservation_table = reservation_table
        FindVertex.__init__(self, heigth, width,*args, **kwargs)

    def actions(self, state):
        poss, time = state
        actions = FindVertex.actions(self, poss)
        actions.append(("wait", (0, 0)))
        
        newactions = []
        id_1 = self.reservation_table.get((poss, time + 1))
        for name, move in actions:
            s1 = self.result(state, (name, move))
            id_2 = self.reservation_table.get((s1[0], time))
            if self.reservation_table.get(s1) is None and (id_1 is None or id_1 != id_2):
                newactions.append((name, move))
        return newactions
    
    def result(self, state, action):
        return (FindVertex.result(self, state[0], action), state[1] + 1)
    
    def action_cost(self, s, a, s1):
        if a[0] == "wait" and s1 in self.goals and s1[1] < self.goals[0][1]:
            return 0
        if s1[1] != self.goals[0][1]:
            return 1
        return FindVertex.action_cost(self, s, a, s1)    
    
    def is_goal(self, state):
        return FindVertex.is_goal(self, state)

class Node(object):
    "A Node in a search tree."
    def __init__(self, state, actions=None):
        self.state=state
        self.actions=actions

    def __repr__(self): return '<{}>'.format(self.state)
    def __eq__(self, __o: object) -> bool: return __o is not None and self.state == __o.state
    def __hash__(self): return hash(self.state)

class NodeTree(Node):
    def __init__(self, parent=None, path_cost=0, *args, **kwargs):
        self.parent=parent
        self.path_cost=path_cost
        Node.__init__(self, *args, **kwargs)
    
    def __len__(self): return 0 if self.parent is None else (1 + len(self.parent))
    def __lt__(self, other): return self.path_cost < other.path_cost
    


def default_heuristic_cost(_): return 0
def astar_cost(g,he): return lambda n: g(n) + he(n)
failure = NodeTree(state='failure', path_cost=math.inf) # Indicates an algorithm couldn't find a solution.
cutoff  = NodeTree(state='cutoff',  path_cost=math.inf)
                   
def default_cost(n: NodeTree): return n.path_cost


def expand(problem: Problem, node: NodeTree):
    "Expand a node, generating the children nodes."
    s = node.state
    for actions in problem.actions(s):
        s1 = problem.result(s, actions)
        cost = node.path_cost + problem.action_cost(s, actions, s1)
        yield NodeTree(state=s1, parent=node, actions=actions, path_cost=cost)


def path_actions(node: NodeTree):
    "The sequence of actions to get to this node." 
    if node.parent is None:
        return []
    return path_actions(node.parent) + [node.actions]


def path_states(node: NodeTree):
    "The sequence of states to get to this node."
    if node in (cutoff, failure, None): 
        return []
    return path_states(node.parent) + [node.state]
    
def best_first_search(node: NodeTree, filter, adj, f=default_cost):
    "Search nodes with minimum f(node) value first."
    frontier = PriorityQueue()
    frontier.put((f(node), node))
    reached = {node.state: node}
    while len(frontier.queue):
        _, node = frontier.get()
        if filter(node):
            return node
        for child in adj(node):
            s = child.state
            if s not in reached or child.path_cost < reached[s].path_cost:
                reached[s] = child
                frontier.put((f(child), child))
    return None

def astar_search_problem(node: NodeTree, problem: Problem, he=default_heuristic_cost, g=default_cost):
    is_goal = lambda n: problem.is_goal(n.state)
    newexpand = lambda n: expand(problem=problem, node=n)
    return astar_search(node=node, is_goal=is_goal, adj=newexpand, he=he, g=g)

def astar_search(node: NodeTree, is_goal, adj, he=default_heuristic_cost, g=default_cost):
    """Search nodes with minimum f(n) = g(n) + he(n)."""
    return best_first_search(node, is_goal, adj=adj, f=astar_cost(g, he))


class RRAstar:
    def __init__(self, start, rrastar_problem, he=default_heuristic_cost, g=default_cost):
        self.f = astar_cost(g=g, he=he)
        self.frontier = PriorityQueue()
        self.frontier.put((self.f(start), start))
        self.reached = {start.state: start}
        self.filter = lambda n, p: n.state == p.state[0]
        self.adj = lambda n: expand(problem=rrastar_problem, node=n)

    def resume_rrastar(self, p):
        while len(self.frontier.queue):
            _, node = self.frontier.get()
            if self.filter(node, p):
                return node
            for child in self.adj(node):
                s = child.state
                if s not in self.reached or child.path_cost < self.reached[s].path_cost:
                    self.reached[s] = child
                    self.frontier.put((self.f(child), child))
        return None

def whcastar_heuristic(rrastar_instance: RRAstar, node: NodeTree):
    if rrastar_instance.reached.get(node.state[0]) is not None:
        return len(rrastar_instance.reached[node.state[0]])
    cost = len(rrastar_instance.resume_rrastar(node))
    if cost != 0:
        return cost
    return inf

def init_rrastar(start, target, heigth, width):
    rrastar_problem = FindVertex(heigth, width, goals=[start])
    he = lambda n: norma2(start, n.state)
    rrastar_instance = RRAstar(start=NodeTree(state=target), rrastar_problem=rrastar_problem, he=he)
    return rrastar_instance

def start_whcastar_search(reservation_table: dict, heigth, width, rrastar_instance: RRAstar, start, target, w: int):
    agent_problem = FindWithAgent(reservation_table=reservation_table, heigth= heigth, width = width, goals=[(target, w)])
    start_node = NodeTree(state=(start, 0))
    he = lambda n: whcastar_heuristic(rrastar_instance=rrastar_instance, node=n)
    filter = lambda n: agent_problem.is_goal(n.state) or n.state[1] == w
    adj = lambda n: chain(expand(agent_problem, n), add_edge(n=n, reservation_table=reservation_table, rrastar_instance=rrastar_instance, w=w))
    node = astar_search(node=start_node, is_goal=filter, adj=adj, he=he)
    return path_states(node=node)

def add_edge(n, reservation_table: dict, rrastar_instance: RRAstar, w):
    node = rrastar_instance.reached.get(n.state[0])
    time = len(node)
    if time > w:
        return []
    current_node = n
    id_1 = reservation_table.get((n.state[0], n.state[1] + 1))
    for item in path_states(node)[-2::-1]:
        id_2 = reservation_table.get((item, current_node.state[1]))
        state = item, current_node.state[1] + 1
        if reservation_table.get(state) is not None or (id_1 is not None and id_1 == id_2):
            return []
        id_1 = reservation_table.get((item, state[1] + 1))
        current_node = NodeTree(state=state, parent=current_node, path_cost=current_node.path_cost + 1)
    return [current_node]

def whcastar_search(connectors,starts:list[tuple] ,goals: list[tuple], rrastar_list: list[RRAstar], heigth, width, w: int, reservation_table):
    reservation_table = {} if not reservation_table else reservation_table

    for i in range(len(goals)):
        start, target = starts[i], goals[i]
        rrastar_list[i] = init_rrastar(start=start, target=target,heigth= heigth,width= width) if rrastar_list[i] is None else rrastar_list[i]
        reservation_table[(start, 0)] = connectors[i]
    paths = {}
    for i in range(len(goals)):
        start, target = starts[i], goals[i]
        rrastar_instance = rrastar_list[i]
        path = start_whcastar_search(reservation_table=reservation_table, heigth= heigth,width= width, rrastar_instance=rrastar_instance, start=start, target=target, w=w)
        paths[connectors[i]] = path
        for cell in path:
            reservation_table[cell] = connectors[i]
    return paths

