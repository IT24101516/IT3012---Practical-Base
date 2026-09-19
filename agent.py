# agent.py
#Lab 03 - IT24101516
import random
from collections import deque
import heapq

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
        self.active_algo = 'BFS'

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

        if self.plan:
            return self.plan.pop(0)

        return 'Stay'