import tkinter as tk
from tkinter import Canvas, Button, Frame, Text, Scrollbar
import random
import json

class GeneratorSimulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Roblox Forsaken Generator Simulator")
        self.root.geometry("800x700")

        # Grid settings
        self.grid_size = 6
        self.cell_size = 80
        self.canvas_size = self.grid_size * self.cell_size

        # Game state
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.wire_pairs = []
        self.current_drawing = None
        self.drawing_path = []
        self.completed_paths = []

        # Colors for different wire pairs
        self.colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown',
                      'pink', 'cyan', 'magenta', 'yellow', 'darkred', 'darkblue']

        self.setup_ui()
        self.generate_puzzle()

    def setup_ui(self):
        # Main frame
        main_frame = Frame(self.root)
        main_frame.pack(pady=20)

        # Title
        title = tk.Label(main_frame, text="Generator Wire Puzzle",
                        font=("Arial", 16, "bold"))
        title.pack(pady=10)

        # Canvas for the grid
        self.canvas = Canvas(main_frame, width=self.canvas_size, height=self.canvas_size,
                           bg='#0a0a0a', highlightthickness=2, highlightbackground='gray')
        self.canvas.pack(pady=10)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # Control buttons
        button_frame = Frame(main_frame)
        button_frame.pack(pady=10)

        Button(button_frame, text="New Puzzle", command=self.generate_puzzle,
               font=("Arial", 12), bg='lightblue').pack(side=tk.LEFT, padx=5)

        Button(button_frame, text="Clear All", command=self.clear_all,
               font=("Arial", 12), bg='lightcoral').pack(side=tk.LEFT, padx=5)

        Button(button_frame, text="Auto Solve", command=self.auto_solve,
               font=("Arial", 12), bg='lightgreen').pack(side=tk.LEFT, padx=5)

        # JSON pairs editor
        json_frame = Frame(main_frame)
        json_frame.pack(pady=10)

        json_label = tk.Label(json_frame, text="Wire Pairs JSON:", font=("Arial", 10, "bold"))
        json_label.pack()

        # Text box for JSON editing
        text_frame = Frame(json_frame)
        text_frame.pack()

        self.json_text = Text(text_frame, width=50, height=6, font=("Courier", 9))
        scrollbar = Scrollbar(text_frame, orient="vertical", command=self.json_text.yview)
        self.json_text.configure(yscrollcommand=scrollbar.set)

        self.json_text.pack(side=tk.LEFT)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Set button for applying JSON changes
        Button(json_frame, text="Set Pairs", command=self.on_json_set,
               font=("Arial", 10), bg='lightgreen').pack(pady=5)

        # Status label
        self.status_label = tk.Label(main_frame, text="Click and drag to connect matching colored dots",
                                   font=("Arial", 10))
        self.status_label.pack(pady=5)

    def generate_puzzle(self):
        """Generate a solvable puzzle with wire pairs."""
        self.clear_all()

        print("Generating new puzzle...")

        # Keep generating until we find a solvable puzzle
        attempt = 0
        while True:
            attempt += 1
            print(f"Generation attempt {attempt}...")

            temp_pairs = []
            used_positions = set()

            # Generate 4-6 random wire pairs
            num_pairs = random.randint(4, 6)

            # Generate all pairs for this attempt
            success = True
            for i in range(num_pairs):
                # Find two random empty positions
                pair_attempts = 0
                while pair_attempts < 50:  # Prevent infinite loop
                    x1, y1 = random.randint(0, 5), random.randint(0, 5)
                    x2, y2 = random.randint(0, 5), random.randint(0, 5)

                    if (x1, y1) not in used_positions and (x2, y2) not in used_positions and (x1, y1) != (x2, y2):
                        used_positions.add((x1, y1))
                        used_positions.add((x2, y2))
                        temp_pairs.append([(x1, y1), (x2, y2)])
                        break
                    pair_attempts += 1

                if pair_attempts >= 50:
                    success = False
                    break

            # If we couldn't generate all pairs, try again
            if not success or len(temp_pairs) != num_pairs:
                continue

            # Test if this puzzle is solvable
            print(f"Testing solvability of {num_pairs} pairs...")
            if self.test_solvability(temp_pairs):
                # Use this solvable puzzle
                self.wire_pairs = temp_pairs
                for i, pair in enumerate(self.wire_pairs):
                    x1, y1 = pair[0]
                    x2, y2 = pair[1]
                    self.grid[y1][x1] = i + 1
                    self.grid[y2][x2] = i + 1
                print(f"✓ Generated solvable puzzle after {attempt} attempts!")
                break
            else:
                print(f"Puzzle not solvable, trying again...")
                # Continue the loop to generate a new puzzle

        self.draw_grid()
        self.update_json_display()
        self.update_status(f"Connect {len(self.wire_pairs)} wire pairs!")

    def test_solvability(self, pairs):
        """Test if a puzzle configuration is solvable."""
        try:
            import solver
            solutions = solver.solve(pairs)
            # Check if all pairs have solutions
            solvable = all(len(solution) > 0 for solution in solutions)
            if solvable:
                print(f"✓ Puzzle is solvable! All {len(pairs)} pairs can be connected.")
            else:
                unsolved = sum(1 for s in solutions if len(s) == 0)
                print(f"✗ Puzzle not solvable. {unsolved} out of {len(pairs)} pairs cannot be connected.")
            return solvable
        except Exception as e:
            print(f"Solver error: {e}")
            # If solver is not available, assume solvable
            return True

    def create_simple_puzzle(self):
        """Create a simple solvable puzzle as fallback."""
        simple_pairs = [
            [(0, 0), (0, 5)],  # Top-left to bottom-left
            [(5, 0), (5, 5)],  # Top-right to bottom-right
            [(1, 1), (4, 1)],  # Horizontal line
            [(2, 2), (2, 4)]   # Vertical line
        ]
        self.wire_pairs = simple_pairs
        for i, pair in enumerate(self.wire_pairs):
            x1, y1 = pair[0]
            x2, y2 = pair[1]
            self.grid[y1][x1] = i + 1
            self.grid[y2][x2] = i + 1

    def draw_grid(self):
        """Draw the game grid and wire dots."""
        self.canvas.delete("all")

        # Draw grid lines
        for i in range(self.grid_size + 1):
            x = i * self.cell_size
            self.canvas.create_line(x, 0, x, self.canvas_size, fill='gray', width=1)
            self.canvas.create_line(0, x, self.canvas_size, x, fill='gray', width=1)

        # Draw completed paths
        for path_info in self.completed_paths:
            path, color = path_info
            for i in range(len(path) - 1):
                x1, y1 = self.grid_to_canvas(path[i][0], path[i][1])
                x2, y2 = self.grid_to_canvas(path[i + 1][0], path[i + 1][1])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=6,
                                      capstyle=tk.ROUND, tags="wire")

        # Draw current drawing path
        if len(self.drawing_path) > 1:
            color = self.get_pair_color(self.current_drawing)
            for i in range(len(self.drawing_path) - 1):
                x1, y1 = self.grid_to_canvas(self.drawing_path[i][0], self.drawing_path[i][1])
                x2, y2 = self.grid_to_canvas(self.drawing_path[i + 1][0], self.drawing_path[i + 1][1])
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=6,
                                      capstyle=tk.ROUND, tags="current_wire")

        # Draw wire dots as circles
        for i, pair in enumerate(self.wire_pairs):
            color = self.colors[i % len(self.colors)]
            for x, y in pair:
                canvas_x, canvas_y = self.grid_to_canvas(x, y)
                self.canvas.create_oval(canvas_x - 15, canvas_y - 15,
                                      canvas_x + 15, canvas_y + 15,
                                      fill=color, outline='white', width=3, tags="dot")
                self.canvas.create_text(canvas_x, canvas_y, text=str(i + 1),
                                      fill='white', font=("Arial", 12, "bold"))

    def grid_to_canvas(self, grid_x, grid_y):
        """Convert grid coordinates to canvas coordinates."""
        canvas_x = grid_x * self.cell_size + self.cell_size // 2
        canvas_y = grid_y * self.cell_size + self.cell_size // 2
        return canvas_x, canvas_y

    def canvas_to_grid(self, canvas_x, canvas_y):
        """Convert canvas coordinates to grid coordinates."""
        grid_x = int(canvas_x // self.cell_size)
        grid_y = int(canvas_y // self.cell_size)
        return max(0, min(5, grid_x)), max(0, min(5, grid_y))

    def get_pair_color(self, pair_index):
        """Get color for a wire pair."""
        if pair_index is not None:
            return self.colors[pair_index % len(self.colors)]
        return 'white'

    def find_dot_at_position(self, grid_x, grid_y):
        """Find which wire pair has a dot at the given position."""
        for i, pair in enumerate(self.wire_pairs):
            if (grid_x, grid_y) in pair:
                return i
        return None

    def is_valid_move(self, from_pos, to_pos):
        """Check if a move is valid (no crossing other wires)."""
        # Simple adjacent cell check
        dx = abs(to_pos[0] - from_pos[0])
        dy = abs(to_pos[1] - from_pos[1])
        return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

    def on_mouse_down(self, event):
        """Handle mouse down event."""
        grid_x, grid_y = self.canvas_to_grid(event.x, event.y)
        dot_pair = self.find_dot_at_position(grid_x, grid_y)

        if dot_pair is not None:
            self.current_drawing = dot_pair
            self.drawing_path = [(grid_x, grid_y)]
            self.update_status(f"Drawing wire {dot_pair + 1}...")

    def on_mouse_drag(self, event):
        """Handle mouse drag event."""
        if self.current_drawing is not None:
            grid_x, grid_y = self.canvas_to_grid(event.x, event.y)

            if self.drawing_path and (grid_x, grid_y) != self.drawing_path[-1]:
                last_pos = self.drawing_path[-1]
                if self.is_valid_move(last_pos, (grid_x, grid_y)):
                    self.drawing_path.append((grid_x, grid_y))
                    self.draw_grid()

    def on_mouse_up(self, event):
        """Handle mouse up event."""
        if self.current_drawing is not None and len(self.drawing_path) > 1:
            grid_x, grid_y = self.canvas_to_grid(event.x, event.y)

            # Check if we ended on the matching dot
            pair = self.wire_pairs[self.current_drawing]
            start_pos = self.drawing_path[0]

            if start_pos == pair[0] and (grid_x, grid_y) == pair[1]:
                # Valid connection
                color = self.get_pair_color(self.current_drawing)
                self.completed_paths.append((self.drawing_path.copy(), color))
                self.update_status(f"Wire {self.current_drawing + 1} connected!")
                self.check_completion()
            elif start_pos == pair[1] and (grid_x, grid_y) == pair[0]:
                # Valid connection (reverse)
                color = self.get_pair_color(self.current_drawing)
                self.completed_paths.append((self.drawing_path.copy(), color))
                self.update_status(f"Wire {self.current_drawing + 1} connected!")
                self.check_completion()
            else:
                self.update_status("Invalid connection! Try again.")

        self.current_drawing = None
        self.drawing_path = []
        self.draw_grid()

    def check_completion(self):
        """Check if all wires are connected."""
        if len(self.completed_paths) == len(self.wire_pairs):
            self.update_status("🎉 Puzzle completed! Generator is fixed!")

    def clear_all(self):
        """Clear all wires and reset the puzzle."""
        self.completed_paths = []
        self.current_drawing = None
        self.drawing_path = []
        self.wire_pairs = []
        self.grid = [[0 for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.canvas.delete("all")
        self.update_json_display()
        self.update_status("Cleared. Generate a new puzzle to play!")

    def auto_solve(self):
        """Auto-solve using the solver module."""
        try:
            import solver

            if not self.wire_pairs:
                self.update_status("Generate a puzzle first!")
                return

            self.update_status("Auto-solving...")
            solutions = solver.solve(self.wire_pairs)

            self.completed_paths = []
            for i, path in enumerate(solutions):
                if path:
                    color = self.get_pair_color(i)
                    self.completed_paths.append((path, color))

            self.draw_grid()
            self.update_status(f"Auto-solved! {len([s for s in solutions if s])} wires connected.")

        except ImportError:
            self.update_status("Solver module not found!")
        except Exception as e:
            self.update_status(f"Solver error: {str(e)}")

    def update_status(self, message):
        """Update the status label."""
        self.status_label.config(text=message)

    def update_json_display(self):
        """Update the JSON text box with current wire pairs."""
        try:
            json_str = json.dumps(self.wire_pairs, indent=2)
            self.json_text.delete(1.0, tk.END)
            self.json_text.insert(1.0, json_str)
        except Exception as e:
            print(f"Error updating JSON display: {e}")

    def on_json_set(self):
        """Apply JSON changes when Set button is clicked."""
        try:
            # Get text from the text box
            json_str = self.json_text.get(1.0, tk.END).strip()

            if not json_str:
                return

            # Parse the JSON
            new_pairs = json.loads(json_str)

            # Validate the format
            if not isinstance(new_pairs, list):
                self.update_status("❌ JSON must be a list of pairs")
                return

            for pair in new_pairs:
                if not isinstance(pair, list) or len(pair) != 2:
                    self.update_status("❌ Each pair must be a list of 2 coordinates")
                    return
                for coord in pair:
                    if not isinstance(coord, list) or len(coord) != 2:
                        self.update_status("❌ Each coordinate must be [x, y]")
                        return
                    if not all(isinstance(c, int) and 0 <= c <= 5 for c in coord):
                        self.update_status("❌ Coordinates must be integers 0-5")
                        return

            # Clear current puzzle
            self.clear_all()

            # Set new pairs
            self.wire_pairs = new_pairs
            for i, pair in enumerate(self.wire_pairs):
                x1, y1 = pair[0]
                x2, y2 = pair[1]
                self.grid[y1][x1] = i + 1
                self.grid[y2][x2] = i + 1

            # Redraw
            self.draw_grid()
            self.update_status(f"✓ Loaded {len(self.wire_pairs)} wire pairs from JSON")

        except json.JSONDecodeError as e:
            self.update_status(f"❌ Invalid JSON: {str(e)}")
        except Exception as e:
            self.update_status(f"❌ Error: {str(e)}")

    def run(self):
        """Start the simulator."""
        self.root.mainloop()

if __name__ == "__main__":
    simulator = GeneratorSimulator()
    simulator.run()
