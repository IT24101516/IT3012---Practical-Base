# visual_grid_game.py
import random
import tkinter as tk


class VisualGridHuntGame:
    """A flexible Pacman-style grid environment with support for configurable opponents and larger scales."""

    def __init__(self, width=10, height=10, num_food=10, num_opponents=2, num_traps=4, custom_walls=None):
        self.width = width
        self.height = height
        self.agent_pos = [0, 0]  # Starting position (x, y)
        self.facing = 'Up' # Initial facing direction (IT24101516 Lab 02)

        if custom_walls is not None:
            self.walls = set(custom_walls)
        else:
            # Generate some default scattered walls for a larger grid
            self.walls = {(2, 2), (2, 3), (5, 5), (6, 5), (3, 7)}

        # Dynamically generate random food positions avoiding walls and agent start
        self.food_positions = set()
        while len(self.food_positions) < num_food:
            fx = random.randint(0, self.width - 1)
            fy = random.randint(0, self.height - 1)
            pos_tuple = (fx, fy)
            if pos_tuple != (0, 0) and pos_tuple not in self.walls:
                self.food_positions.add(pos_tuple)

        # Generate adversarial opponents
        self.opponents = []
        while len(self.opponents) < num_opponents:
            ox = random.randint(0, self.width - 1)
            oy = random.randint(0, self.height - 1)
            op_pos = [ox, oy]
            if tuple(op_pos) != (0, 0) and tuple(op_pos) not in self.walls and tuple(op_pos) not in self.food_positions:
                self.opponents.append(op_pos)

#Set up toxic traps (IT24101516)-Question 2.1
        self.toxic_traps = set()
        while len(self.toxic_traps) < num_traps:
            tx = random.randint(0, self.width - 1)
            ty = random.randint(0, self.height - 1)
            trap_tuple = (tx, ty)
            if (trap_tuple != (0, 0)
                    and trap_tuple not in self.walls
                    and trap_tuple not in self.food_positions):
                self.toxic_traps.add(trap_tuple)

        self.score = 0
        self.steps = 0
        self.collision = False

    def get_percept(self) -> dict:
        # Removing agent's sensors to make a partially observable world (IT24101516 Lab 02)
        x, y = self.agent_pos

        if self.facing == 'Left':
            ahead = (x - 1, y)
        elif self.facing == 'Right':
            ahead = (x + 1, y)
        elif self.facing == 'Down':
            ahead = (x, y - 1)
        else :
            ahead = (x, y + 1)

        return {
            'wall_ahead': (
                ahead in self.walls or
                ahead[0] < 0 or
                ahead[0] >= self.width or
                ahead[1] < 0 or
                ahead[1] >= self.height
            ),
            'food_here': tuple(self.agent_pos) in self.food_positions
        }
        """
        return {
            'agent_pos': list(self.agent_pos),
            'opponent_positions': [list(op) for op in self.opponents],
            'smells_food': tuple(self.agent_pos) in self.food_positions,
            'hit_wall': tuple(self.agent_pos) in self.walls,
            # Toxin sensor(IT24101516) - Q 2.2
            'smells_toxin': tuple(self.agent_pos) in self.toxic_traps,
            'collision': self.collision,
            'score': self.score,
            'remaining_food': len(self.food_positions)
        }
        """
    def execute_action(self, action: str):
        self.steps += 1
# Updating the environment according to the SimpleReflexAgent's actions(IT24101516 Lab 02)
        if action == 'Turn_Left':
            if self.facing == 'Up':
                self.facing = 'Left'
            elif self.facing == 'Left':
                self.facing = 'Down'
            elif self.facing == 'Down':
                self.facing = 'Right'
            elif self.facing == 'Right':
                self.facing = 'Up'
        elif action == 'Suck':
            tuple_pos = tuple(self.agent_pos)
            if tuple_pos in self.food_positions:
                self.food_positions.remove(tuple_pos)
                self.score += 20
        elif action == 'Move_Forward':
            new_pos = list(self.agent_pos)
            if self.facing == 'Up':
                new_pos[1] += 1
            elif self.facing == 'Down':
                new_pos[1] -= 1
            elif self.facing == 'Left':
                new_pos[0] -= 1
            elif self.facing == 'Right' :
                new_pos[0] += 1

        """
        if action == 'Up':
            new_pos[1] = min(self.height - 1, new_pos[1] + 1)
        elif action == 'Down':
            new_pos[1] = max(0, new_pos[1] - 1)
        elif action == 'Left':
            new_pos[0] = max(0, new_pos[0] - 1)
        elif action == 'Right':
            new_pos[0] = min(self.width - 1, new_pos[0] + 1)
        """
        if (0 <= new_pos[0] < self.width and 0 <= new_pos[1] < self.height):

            if tuple(new_pos) in self.walls:
                self.score -= 5
            else:
                self.agent_pos = new_pos

                tuple_pos = tuple(self.agent_pos)

                if tuple_pos in self.food_positions:
                    self.food_positions.remove(tuple_pos)
                    self.score += 20

                #Trap penalty (IT24101516)
                if tuple_pos in self.toxic_traps:
                    self.score -= 15

        for op in self.opponents:
            move = random.choice(['Up', 'Down', 'Left', 'Right', 'Stay'])
            if move == 'Up' and op[1] < self.height - 1:
                op[1] += 1
            elif move == 'Down' and op[1] > 0:
                op[1] -= 1
            elif move == 'Left' and op[0] > 0:
                op[0] -= 1
            elif move == 'Right' and op[0] < self.width - 1:
                op[0] += 1

            if op == self.agent_pos:
                self.score -= 50
                self.collision = True

    def is_done(self) -> bool:
        return len(self.food_positions) == 0 or self.steps >= 60 or self.collision

# Step 1.2: Implementing The Simple Reflex Agent (IT24101516 Lab 02)
class SimpleReflexAgent:
    def sense_and_act(self, percept):
        if percept['food_here']:
            return 'Suck'
        elif percept['wall_ahead']:
            return 'Turn_Left'
        else:
            return 'Move_Forward'

# Step 1.3: Model-Based Agent (IT24101516 Lab 02)
class ModelBasedAgent:
    def __init__(self):
        # Internal model of the agent's estimated position
        self.model_x = 0
        self.model_y = 0
        # Current estimated facing direction
        self.facing = 'Up'
        # IT24101516 - Store cells that the agent has already visited.
        self.visited_cells = set()
        # IT24101516 - Remember the previous action taken by the agent.
        self.last_action = None

    def sense_and_act(self, percept):
        # Current cell according to the agent's internal model
        current_cell = (self.model_x, self.model_y)
        # IT24101516 - Add the current cell to memory.
        self.visited_cells.add(current_cell)
        # Food has the highest priority.
        if percept['food_here']:
            action = 'Suck'
        # If there is a wall ahead, turn left.
        elif percept['wall_ahead']:
            action = 'Turn_Left'
        else:
            # Calculate the cell that would be reached by moving forward.
            if self.facing == 'Up':
                next_cell = (self.model_x, self.model_y + 1)
            elif self.facing == 'Down':
                next_cell = (self.model_x, self.model_y - 1)
            elif self.facing == 'Left':
                next_cell = (self.model_x - 1, self.model_y)

            else:  # Right
                next_cell = (self.model_x + 1, self.model_y)
            # IT24101516 - Use memory to avoid moving into a
            # previously visited cell when possible.
            if next_cell in self.visited_cells:
                # Turn left to explore another direction.
                action = 'Turn_Left'
            else:
                # Continue moving forward into an unvisited cell.
                action = 'Move_Forward'

        # Update the internal model after choosing the action.
        if action == 'Turn_Left':
            # Update the estimated facing direction.
            if self.facing == 'Up':
                self.facing = 'Left'
            elif self.facing == 'Left':
                self.facing = 'Down'
            elif self.facing == 'Down':
                self.facing = 'Right'
            elif self.facing == 'Right':
                self.facing = 'Up'
        elif action == 'Move_Forward':
            # Update the estimated position.
            if self.facing == 'Up':
                self.model_y += 1
            elif self.facing == 'Down':
                self.model_y -= 1
            elif self.facing == 'Left':
                self.model_x -= 1
            elif self.facing == 'Right':
                self.model_x += 1

        # IT24101516 - Store the selected action for the next decision.
        self.last_action = action
        return action

class GridGameGUI:
    """Tkinter wrapper that dynamically scales cell sizes to keep larger grids on screen."""

    def __init__(self, root, width=10, height=10, num_food=12, num_opponents=2, walls=None):
        self.root = root
        self.root.title("IT3012 - Scalable Multi-Agent Grid Hunt")

        self.env = VisualGridHuntGame(width=width, height=height, num_food=num_food, num_traps=4, num_opponents=num_opponents,
                                      custom_walls=walls)

        #SimplereflexAgent Creation Lab 02 (IT24101516) for step 1.2
        #self.agent = SimpleReflexAgent()

        #Creating the ModelBasedAgent Lab 02 (IT24101516) for step 1.3
        self.agent = ModelBasedAgent()

        # Dynamically calculate cell size so the total canvas fits nicely within a 600x600 window ceiling
        max_canvas_dim = 600
        self.cell_size = max(20, min(max_canvas_dim // self.env.width, max_canvas_dim // self.env.height))

        canvas_w = self.env.width * self.cell_size
        canvas_h = self.env.height * self.cell_size

        self.canvas = tk.Canvas(root, width=canvas_w, height=canvas_h, bg="white")
        self.canvas.pack()

        self.label = tk.Label(root, text="Score: 0 | Steps: 0", font=("Arial", 14))
        self.label.pack(pady=10)

        self.btn = tk.Button(root, text="Start Simulation", command=self.run_loop, font=("Arial", 12), bg="#000066",
                             fg="white")
        self.btn.pack(pady=5)

        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")

        for x in range(self.env.width):
            for y in range(self.env.height):
                x1 = x * self.cell_size
                y1 = (self.env.height - 1 - y) * self.cell_size
                x2 = x1 + self.cell_size
                y2 = y1 + self.cell_size

                color = "#f1f5f9" if (x, y) not in self.env.walls else "#64748b"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#cbd5e1")

                # Only draw text if cell is large enough
                if self.cell_size >= 40 and (x, y) in self.env.walls:
                    self.canvas.create_text(x1 + self.cell_size / 2, y1 + self.cell_size / 2, text="W", fill="white",
                                            font=("Arial", 8, "bold"))

        for fx, fy in self.env.food_positions:
            offset = self.cell_size * 0.25
            x1 = fx * self.cell_size + offset
            y1 = (self.env.height - 1 - fy) * self.cell_size + offset
            self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.5, y1 + self.cell_size * 0.5, fill="#f59e0b",
                                    outline="#d97706")

        # Render traps as purple diamonds (IT24101516) - Q 2.3
        for tx, ty in self.env.toxic_traps:
            cx = tx * self.cell_size + self.cell_size / 2
            cy = (self.env.height - 1 - ty) * self.cell_size + self.cell_size / 2
            half = self.cell_size * 0.3
            points = [cx, cy - half, cx + half, cy, cx, cy + half, cx - half, cy]
            self.canvas.create_polygon(points, fill="#7c3aed", outline="#5b21b6")

        for ox, oy in self.env.opponents:
            offset = self.cell_size * 0.2
            x1 = ox * self.cell_size + offset
            y1 = (self.env.height - 1 - oy) * self.cell_size + offset
            self.canvas.create_rectangle(x1, y1, x1 + self.cell_size * 0.6, y1 + self.cell_size * 0.6, fill="#990000",
                                         outline="#7a0000")

        ax, ay = self.env.agent_pos
        offset = self.cell_size * 0.15
        x1 = ax * self.cell_size + offset
        y1 = (self.env.height - 1 - ay) * self.cell_size + offset
        self.canvas.create_oval(x1, y1, x1 + self.cell_size * 0.7, y1 + self.cell_size * 0.7, fill="#000066",
                                outline="#1e3a8a")

    def run_loop(self):
        self.btn.config(state="disabled")

        def step():
            if not self.env.is_done():

                # Get percept and let the Simple Reflex Agent choose an action
                """
                action = random.choice(['Up', 'Down', 'Left', 'Right'])
                self.env.execute_action(action)
                """
                percept = self.env.get_percept()
                action = self.agent.sense_and_act(percept)

                self.env.execute_action(action)

                self.draw_grid()
                self.label.config(text=f"Score: {self.env.score} | Steps: {self.env.steps} | Action: {action}")
                self.root.after(250, step)
            else:
                end_text = f"Collision! Game Over! Final Score: {self.env.score}" if self.env.collision else f"Finished! Final Score: {self.env.score}"
                self.label.config(text=end_text)
                self.btn.config(state="normal")

        step()


if __name__ == "__main__":
    root = tk.Tk()
    # Try a larger grid size like 12x12 with 15 food and 3 opponents!
    app = GridGameGUI(root, width=12, height=12, num_food=15, num_opponents=0)
    root.mainloop()