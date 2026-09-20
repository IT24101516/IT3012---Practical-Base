# agent.py
#Lab 03 - IT24101516
import random
from collections import deque
import heapq
# Lab 04 - IT24101516 - Used for Euclidean distance calculation
import math

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # If standing directly on food, or just wander / move towards coordinates
        pos = percept['agent_pos']
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

#Lab 03 - IT24101516
class SearchAgent:

    def __init__(self):
        self.plan = []
        #self.active_algo = 'BFS'
        # Lab 04 - IT24101516 - Use A* as the active search algorithm
        self.active_algo = 'AStar'

    def get_neighbors(self, state, grid_size, walls):
        x, y = state
        width, height = grid_size

        directions = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        neighbors = []

        for action, new_state in directions:
            nx, ny = new_state

            if (
                0 <= nx < width
                and 0 <= ny < height
                and new_state not in walls
            ):
                neighbors.append((new_state, action))

        return neighbors

    # Lab 04 - IT24101516 - Step 1.1
    # Calculates Manhattan distance between current position and goal
    def manhattan_distance(self, pos, goal):
        return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


    # Lab 04 - IT24101516 - Step 1.1
    # Calculates straight-line Euclidean distance between current position and goal
    def euclidean_distance(self, pos, goal):
        return math.sqrt(
            (pos[0] - goal[0]) ** 2 +
            (pos[1] - goal[1]) ** 2
        )

    def bfs_search(self, start, goal, grid_size, walls):

        frontier = deque()
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current_state, path = frontier.popleft()

            if current_state == goal:
                return path

            for next_state, action in self.get_neighbors(
                    current_state, grid_size, walls):

                if next_state not in reached:
                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append((next_state, new_path))

        return []

    def dfs_search(self, start, goal, grid_size, walls):

        frontier = []
        frontier.append((start, []))

        reached = {start}

        while frontier:

            current_state, path = frontier.pop()

            if current_state == goal:
                return path

            for next_state, action in self.get_neighbors(
                    current_state, grid_size, walls):

                if next_state not in reached:
                    reached.add(next_state)

                    new_path = path + [action]

                    frontier.append((next_state, new_path))

        return []

    def ucs_search(self, start, goal, grid_size, walls):

        frontier = []

        heapq.heappush(frontier, (0, start, []))

        reached = set()

        while frontier:

            cost, current_state, path = heapq.heappop(frontier)

            if current_state in reached:
                continue

            reached.add(current_state)

            if current_state == goal:
                return path

            for next_state, action in self.get_neighbors(
                    current_state, grid_size, walls):

                if next_state not in reached:

                    new_cost = cost + 1
                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (new_cost, next_state, new_path)
                    )

        return []


    # Lab 04 - IT24101516 - Step 1.2
    # A* Search uses path cost g(n) and heuristic h(n)
    def astar_search(
            self,
            start_pos,
            goal_pos,
            walls,
            grid_size,
            heuristic_type='manhattan'
    ):

        frontier = []
        reached_states = set()

        # Calculate heuristic value for the starting position
        if heuristic_type == 'euclidean':
            h_cost = self.euclidean_distance(start_pos, goal_pos)
        else:
            h_cost = self.manhattan_distance(start_pos, goal_pos)

        # Starting path cost
        g_cost = 0

        # f(n) = g(n) + h(n)
        f_cost = g_cost + h_cost

        # Store:
        # (f cost, g cost, current position, path)
        heapq.heappush(
            frontier,
            (f_cost, g_cost, start_pos, [])
        )

        while frontier:

            f_cost, g_cost, current_pos, path = heapq.heappop(frontier)

            # Skip already explored states
            if current_pos in reached_states:
                continue

            # Check whether goal is reached
            if current_pos == goal_pos:
                return path

            reached_states.add(current_pos)

            # Check all valid neighboring cells
            for next_pos, action in self.get_neighbors(
                    current_pos,
                    grid_size,
                    walls
            ):

                if next_pos not in reached_states:

                    # Every movement costs 1
                    new_g_cost = g_cost + 1

                    # Calculate heuristic
                    if heuristic_type == 'euclidean':
                        new_h_cost = self.euclidean_distance(
                            next_pos,
                            goal_pos
                        )
                    else:
                        new_h_cost = self.manhattan_distance(
                            next_pos,
                            goal_pos
                        )

                    # f(n) = g(n) + h(n)
                    new_f_cost = new_g_cost + new_h_cost

                    new_path = path + [action]

                    heapq.heappush(
                        frontier,
                        (
                            new_f_cost,
                            new_g_cost,
                            next_pos,
                            new_path
                        )
                    )

        return []
    

    def sense_and_act(self, percept: dict) -> str:

        if not self.plan:

            all_food = percept['all_food']

            if not all_food:
                return 'Stay'

            start = tuple(percept['agent_pos'])
            grid_size = percept['grid_size']
            walls = set(percept['walls'])

            # Find closest food
            goal = min(
                all_food,
                key=lambda food:
                abs(food[0] - start[0]) +
                abs(food[1] - start[1])
            )

            goal = tuple(goal)

            if self.active_algo == 'BFS':

                self.plan = self.bfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'DFS':

                self.plan = self.dfs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            elif self.active_algo == 'UCS':

                self.plan = self.ucs_search(
                    start,
                    goal,
                    grid_size,
                    walls
                )

            # Lab 04 - IT24101516 - Step 1.3
            # Creates a path to the selected food using A* Search
            elif self.active_algo == 'AStar':

                self.plan = self.astar_search(
                    start,
                    goal,
                    walls,
                    grid_size,
                    'manhattan'
                )

        if self.plan:
            return self.plan.pop(0)

        return 'Stay'