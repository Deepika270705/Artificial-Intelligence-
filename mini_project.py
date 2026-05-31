import tkinter as tk
import random
from collections import deque

# --- CONFIGURATION CONSTANTS ---
GRID_SIZE = 15  # Must be an odd number
CELL_SIZE = 25
WIDTH = GRID_SIZE * CELL_SIZE
HEIGHT = GRID_SIZE * CELL_SIZE

class MazeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("The 'Blindfolded' Maze Solver (Simulation)")
        self.root.configure(bg="#1e1e2e")

        # Game State
        self.grid = []
        self.robot_f = [1, 1]  # Fully Observable
        self.robot_p = [1, 1]  # Partially Observable
        self.goal = [GRID_SIZE - 2, GRID_SIZE - 2]
        
        self.visited_f = set()
        self.visited_p = set()
        self.discovered_walls_p = set()
        self.stack_p = []
        
        self.steps_f = 0
        self.steps_p = 0
        self.running = False
        self.mode = "ai"  # "ai" or "manual"
        
        self.path_f = []
        self.path_index_f = 0

        self.setup_ui()
        self.generate_new_maze()
        
        # Bind manual movement keys
        self.root.bind("<Up>", lambda e: self.handle_manual_move(0, -1))
        self.root.bind("<Down>", lambda e: self.handle_manual_move(0, 1))
        self.root.bind("<Left>", lambda e: self.handle_manual_move(-1, 0))
        self.root.bind("<Right>", lambda e: self.handle_manual_move(1, 0))

    def setup_ui(self):
        # Header Controls Layout
        control_frame = tk.Frame(self.root, bg="#252538", padx=10, pady=10)
        control_frame.pack(fill=tk.X, padx=20, pady=10)

        # Dropdown Mode
        tk.Label(control_frame, text="Mode:", bg="#252538", fg="#cdd6f4", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5)
        self.mode_var = tk.StringVar(value="AI Auto-Solve Simulation")
        mode_menu = tk.OptionMenu(control_frame, self.mode_var, "AI Auto-Solve Simulation", "Manual Play (Arrow Keys)", command=self.change_mode)
        mode_menu.config(bg="#313244", fg="#cdd6f4", borderwidth=0)
        mode_menu.grid(row=0, column=1, padx=5)

        # Buttons
        self.btn_gen = tk.Button(control_frame, text="Generate New Maze", bg="#89b4fa", fg="#11111b", font=("Arial", 10, "bold"), command=self.generate_new_maze)
        self.btn_gen.grid(row=0, column=2, padx=10)

        self.btn_action = tk.Button(control_frame, text="Start Simulation", bg="#45475a", fg="#cdd6f4", font=("Arial", 10), command=self.toggle_simulation)
        self.btn_action.grid(row=0, column=3, padx=5)

        # Canvas Display Layout
        display_frame = tk.Frame(self.root, bg="#1e1e2e")
        display_frame.pack(padx=20, pady=10)

        # Left Panel (Fully Observable)
        panel_f = tk.Frame(display_frame, bg="#252538", padx=10, pady=10, bd=2, relief=tk.RIDGE)
        panel_f.grid(row=0, column=0, padx=10)
        tk.Label(panel_f, text="FULLY OBSERVABLE (God's Eye View)", bg="#252538", fg="#a6e3a1", font=("Arial", 11, "bold")).pack()
        
        self.lbl_stats_f = tk.Label(panel_f, text="Steps: 0 | Explored: 0", bg="#11111b", fg="#cdd6f4", width=30, pady=4)
        self.lbl_stats_f.pack(pady=5)
        
        self.canvas_f = tk.Canvas(panel_f, width=WIDTH, height=HEIGHT, bg="#11111b", highlightthickness=0)
        self.canvas_f.pack()

        # Right Panel (Partially Observable)
        panel_p = tk.Frame(display_frame, bg="#252538", padx=10, pady=10, bd=2, relief=tk.RIDGE)
        panel_p.grid(row=0, column=1, padx=10)
        tk.Label(panel_p, text="PARTIALLY OBSERVABLE (1-Square Vision)", bg="#252538", fg="#f38ba8", font=("Arial", 11, "bold")).pack()
        
        self.lbl_stats_p = tk.Label(panel_p, text="Steps: 0 | Explored: 0", bg="#11111b", fg="#cdd6f4", width=30, pady=4)
        self.lbl_stats_p.pack(pady=5)
        
        self.canvas_p = tk.Canvas(panel_p, width=WIDTH, height=HEIGHT, bg="#11111b", highlightthickness=0)
        self.canvas_p.pack()

    def change_mode(self, val):
        if "Manual" in val:
            self.mode = "manual"
            self.stop_simulation()
            self.btn_action.config(text="Reset Positions")
        else:
            self.mode = "ai"
            self.btn_action.config(text="Start Simulation")
        self.reset_positions()

    # --- MAZE GENERATOR (DFS algorithm) ---
    def generate_new_maze(self):
        self.stop_simulation()
        self.grid = [[1] * GRID_SIZE for _ in range(GRID_SIZE)]
        
        stack = []
        curr = (1, 1)
        self.grid[1][1] = 0
        
        while True:
            neighbors = []
            for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                nx, ny = curr[0] + dx, curr[1] + dy
                if 0 < nx < GRID_SIZE - 1 and 0 < ny < GRID_SIZE - 1 and self.grid[ny][nx] == 1:
                    neighbors.append((nx, ny, curr[0] + dx // 2, curr[1] + dy // 2))
            
            if neighbors:
                nx, ny, wx, wy = random.choice(neighbors)
                self.grid[wy][wx] = 0
                self.grid[ny][nx] = 0
                stack.append(curr)
                curr = (nx, ny)
            elif stack:
                curr = stack.pop()
            else:
                break
                
        self.grid[self.goal[1]][self.goal[0]] = 0
        self.reset_positions()

    def reset_positions(self):
        self.robot_f = [1, 1]
        self.robot_p = [1, 1]
        self.visited_f = {"1,1"}
        self.visited_p = {"1,1"}
        self.discovered_walls_p = set()
        
        self.steps_f = 0
        self.steps_p = 0
        
        self.discover_local_environment(1, 1)
        self.calculate_optimal_path_f()
        
        # Reset Brain AI properties for Agent P
        self.stack_p = [(1, 1)]
        
        self.update_stats()
        self.draw()

    def discover_local_environment(self, rx, ry):
        for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
            nx, ny = rx + dx, ry + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                if self.grid[ny][nx] == 1:
                    self.discovered_walls_p.add(f"{nx},{ny}")

    # --- GLOBAL SYSTEM BFS FOR MAP AWARE AGENT ---
    def calculate_optimal_path_f(self):
        queue = deque([[(1, 1)]])
        visited = {(1, 1)}
        self.path_f = []
        self.path_index_f = 0
        
        while queue:
            path = queue.popleft()
            curr = path[-1]
            
            if curr[0] == self.goal[0] and curr[1] == self.goal[1]:
                self.path_f = path
                return
                
            for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                nx, ny = curr[0] + dx, curr[1] + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                    if self.grid[ny][nx] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(path + [(nx, ny)])

    # --- CORE SIMULATION PROCESSING ENGINE STEPS ---
    def step_fully_observable(self):
        if self.robot_f == self.goal: return True
        if self.path_index_f < len(self.path_f) - 1:
            self.path_index_f += 1
            self.robot_f = list(self.path_f[self.path_index_f])
            self.steps_f += 1
            self.visited_f.add(f"{self.robot_f[0]},{self.robot_f[1]}")
        return self.robot_f == self.goal

    def step_partially_observable(self):
        if self.robot_p == self.goal: return True
        self.discover_local_environment(self.robot_p[0], self.robot_p[1])
        
        moved = False
        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
            nx, ny = self.robot_p[0] + dx, self.robot_p[1] + dy
            key = f"{nx},{ny}"
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and self.grid[ny][nx] == 0 and key not in self.visited_p:
                self.robot_p = [nx, ny]
                self.visited_p.add(key)
                self.stack_p.append((nx, ny))
                self.steps_p += 1
                moved = True
                break
                
        if not moved and len(self.stack_p) > 1:
            self.stack_p.pop()
            prev = self.stack_p[-1]
            self.robot_p = list(prev)
            self.steps_p += 1  # Physical structural move actions count penalty
            
        return self.robot_p == self.goal

    def handle_manual_move(self, dx, dy):
        if self.mode != "manual": return
        
        # Fully Observable Update
        nfx, nfy = self.robot_f[0] + dx, self.robot_f[1] + dy
        if 0 <= nfx < GRID_SIZE and 0 <= nfy < GRID_SIZE and self.grid[nfy][nfx] == 0:
            self.robot_f = [nfx, nfy]
            self.steps_f += 1
            self.visited_f.add(f"{nfx},{nfy}")

        # Partially Observable Update
        npx, npy = self.robot_p[0] + dx, self.robot_p[1] + dy
        if 0 <= npx < GRID_SIZE and 0 <= npy < GRID_SIZE:
            if self.grid[npy][npx] == 1:
                self.discovered_walls_p.add(f"{npx},{npy}")
            else:
                self.robot_p = [npx, npy]
                self.steps_p += 1
                self.visited_p.add(f"{npx},{npy}")
                self.discover_local_environment(npx, npy)
                
        self.update_stats()
        self.draw()

    def toggle_simulation(self):
        if self.mode == "manual":
            self.reset_positions()
            return
            
        if self.running:
            self.stop_simulation()
        else:
            self.running = True
            self.btn_action.config(text="Pause Simulation")
            self.simulation_loop()

    def stop_simulation(self):
        self.running = False
        self.btn_action.config(text="Start Simulation" if self.mode == "ai" else "Reset Positions")

    def simulation_loop(self):
        if not self.running: return
        
        f_done = self.step_fully_observable()
        p_done = self.step_partially_observable()
        
        self.update_stats()
        self.draw()
        
        if not (f_done and p_done):
            self.root.after(100, self.simulation_loop)
        else:
            self.stop_simulation()

    def update_stats(self):
        self.lbl_stats_f.config(text=f"Steps: {self.steps_f} | Explored: {len(self.visited_f)}")
        self.lbl_stats_p.config(text=f"Steps: {self.steps_p} | Explored: {len(self.visited_p)}")

    # --- DRAW / RENDER CANVAS CONTROLLER ---
    def draw(self):
        self.render_panel(self.canvas_f, is_fully=True)
        self.render_panel(self.canvas_p, is_fully=False)

    def render_panel(self, canvas, is_fully):
        canvas.delete("all")
        
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                is_wall = self.grid[y][x] == 1
                key = f"{x},{y}"
                
                x1, y1 = x * CELL_SIZE, y * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                if is_fully:
                    color = "#313244" if is_wall else "#181825"
                    canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#11111b")
                    if key in self.visited_f:
                        canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#45475a", outline="")
                else:
                    # Blindfolded structural rendering rule rules
                    is_visible = abs(x - self.robot_p[0]) <= 1 and abs(y - self.robot_p[1]) <= 1
                    is_discovered_wall = key in self.discovered_walls_p
                    is_visited = key in self.visited_p
                    
                    if is_visible or is_discovered_wall or is_visited:
                        color = "#313244" if is_wall else "#181825"
                        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#11111b")
                        if is_visited:
                            canvas.create_rectangle(x1+2, y1+2, x2-2, y2-2, fill="#585b70", outline="")
                    else:
                        # Completely Unexplored Fog Black
                        canvas.create_rectangle(x1, y1, x2, y2, fill="#09090d", outline="#09090d")

        # Draw Target Goal Obj
        gx, gy = self.goal[0] * CELL_SIZE, self.goal[1] * CELL_SIZE
        canvas.create_oval(gx+4, gy+4, gx+CELL_SIZE-4, gy+CELL_SIZE-4, fill="#a6e3a1", outline="")

        # Draw Robot Character Asset
        bot = self.robot_f if is_fully else self.robot_p
        bx, by = bot[0] * CELL_SIZE, bot[1] * CELL_SIZE
        bot_color = "#89b4fa" if is_fully else "#f38ba8"
        canvas.create_oval(bx+3, by+3, bx+CELL_SIZE-3, by+CELL_SIZE-3, fill=bot_color, outline="")

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeApp(root)
    root.mainloop()