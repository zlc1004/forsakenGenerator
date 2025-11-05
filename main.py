"""
When working on the generator,
the player(s) are forced into a 6x6 minigame similar
to the mobile game "Flow Free", where randomly
generated (1-13) amount of wire dots of matching
color labeled with numbers must be connected to
each other in a grid to complete the minigame.
The repairing Player can't wire through other wires,
and must make space for other ones.
The Player can also reset a specific cable by
clicking the start, or can move the wire backwards
by clicking on a tile that the wire is on.
"""

import vision
import solver
import automation
import time
import base64
import argparse
from pynput import keyboard
from pynput.keyboard import Key, KeyCode
import tkinter as tk
from tkinter import Canvas
import threading

# Parse command line arguments
parser = argparse.ArgumentParser(description='Roblox Forsaken Generator Puzzle Solver')
parser.add_argument('-c', '--config', required=True,
                    help='Config string: i|x|y|size or b<base64>')
parser.add_argument('-a', '--auto', action='store_true',
                    help='Enable automation (if not set, only shows overlay)')
parser.add_argument('-s', '--size', type=int, default=6,
                    help='Size of the puzzle grid (default: 6 for 6x6)')

args = parser.parse_args()
puzzle_size = args.size

# Parse config
config_input = args.config
if config_input.startswith('i'):
    # Parse integer config: i|1227|700|916
    config_str = config_input[1:]  # Remove 'i'
    config = list(map(int, config_str.split('|')))
elif config_input.startswith('b'):
    # Parse base64 config: b<encoded>
    config_str = config_input[1:]  # Remove 'b'
    decoded = base64.b64decode(config_str).decode('utf-8')
    config = list(map(int, decoded.split('|')))
else:
    print("Invalid config format. Use 'i|x|y|size' or 'b<base64>'")
    exit(1)

print(f"Using config: {config}")
if args.auto:
    print("Auto mode enabled. Press Left Alt to start solving...")
else:
    print("Overlay mode only. Automation disabled.")

# Create overlay window
root = None
overlay = None
auto_mode = False

class OverlayWindow(tk.Toplevel):
    """Overlay window class that inherits from tk.Toplevel."""

    def __init__(self, parent):
        super().__init__(parent)

        # Configure window attributes as requested
        self.overrideredirect(True)
        self.overrideredirect(False)  # Set back to False to keep window decorations
        self.wm_attributes("-alpha", 0.8)
        self.wm_attributes("-topmost", "true")

        self.title("Flow Free Solver")
        self.configure(bg='black')

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate overlay size (20% of screen height for both width and height - double the original size)
        self.overlay_size = int(screen_height * 0.2)

        # Position at top right
        x_position = screen_width - self.overlay_size - 20  # 20px margin from edge
        y_position = 20  # 20px from top

        self.geometry(f"{self.overlay_size}x{self.overlay_size}+{x_position}+{y_position}")
        self.resizable(False, False)

        # Create canvas for drawing
        self.canvas = Canvas(self, width=self.overlay_size, height=self.overlay_size, bg='#0a0a0a', highlightthickness=0)
        self.canvas.pack()

        # Add status text
        self.status_text = self.canvas.create_text(self.overlay_size//2, 20, text="Ready", fill="white", font=("Arial", 8))

        print(f"📱 Overlay created: {self.overlay_size}x{self.overlay_size} at ({x_position}, {y_position})")

def create_overlay():
    """Create a small overlay window for displaying solutions."""
    global root, overlay, canvas, status_text

    # Create root window (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Create overlay as Toplevel window
    overlay = OverlayWindow(root)

    # Set global references for backwards compatibility
    canvas = overlay.canvas
    status_text = overlay.status_text

def update_overlay_status(message):
    """Update the status text in overlay."""
    if overlay and canvas:
        canvas.itemconfig(status_text, text=message)
        overlay.update()

def draw_solution_in_overlay(solutions, processed_image=None, grid_size=6):
    """Draw the solution paths in the overlay."""
    if not overlay or not canvas:
        return

    # Clear canvas
    canvas.delete("path")
    canvas.delete("dot")

    overlay_size = overlay.overlay_size
    cell_size = overlay_size // grid_size

    # Function to get color from processed image
    def get_color_from_processed(x, y):
        if processed_image and 0 <= x < grid_size and 0 <= y < grid_size:
            # Get pixel color from processed image
            pixel_color = processed_image.getpixel((x, y))
            # If the color is black, use a default color
            if pixel_color == (0, 0, 0):
                return 'white'
            # Convert RGB tuple to hex color for tkinter
            return f"#{pixel_color[0]:02x}{pixel_color[1]:02x}{pixel_color[2]:02x}"
        else:
            # Fallback colors if no processed image
            fallback_colors = ['red', 'blue', 'green', 'orange', 'purple', 'brown', 'pink', 'cyan']
            return fallback_colors[0]

    # Draw grid lines
    for i in range(grid_size + 1):
        x = i * cell_size
        y = i * cell_size
        canvas.create_line(x, 0, x, overlay_size, fill='gray', width=1, tags="grid")
        canvas.create_line(0, y, overlay_size, y, fill='gray', width=1, tags="grid")

    # Draw solution paths
    for i, path in enumerate(solutions):
        if not path or len(path) < 2:
            continue

        # Get color from the start point of the path in the processed image
        start_x, start_y = path[0]
        color = get_color_from_processed(start_x, start_y)

        # Draw path lines
        for j in range(len(path) - 1):
            x1, y1 = path[j]
            x2, y2 = path[j + 1]

            pixel_x1 = x1 * cell_size + cell_size // 2
            pixel_y1 = y1 * cell_size + cell_size // 2
            pixel_x2 = x2 * cell_size + cell_size // 2
            pixel_y2 = y2 * cell_size + cell_size // 2

            canvas.create_line(pixel_x1, pixel_y1, pixel_x2, pixel_y2,
                             fill=color, width=2, tags="path")

        # Draw start and end points
        start_x, start_y = path[0]
        end_x, end_y = path[-1]

        start_pixel_x = start_x * cell_size + cell_size // 2
        start_pixel_y = start_y * cell_size + cell_size // 2
        end_pixel_x = end_x * cell_size + cell_size // 2
        end_pixel_y = end_y * cell_size + cell_size // 2

        # Draw dots
        radius = 3
        canvas.create_oval(start_pixel_x - radius, start_pixel_y - radius,
                         start_pixel_x + radius, start_pixel_y + radius,
                         fill=color, outline='white', width=1, tags="dot")
        canvas.create_oval(end_pixel_x - radius, end_pixel_y - radius,
                         end_pixel_x + radius, end_pixel_y + radius,
                         fill=color, outline='white', width=1, tags="dot")

        # Add pair number
        canvas.create_text(start_pixel_x - 8, start_pixel_y - 8, text=str(i+1),
                         fill='white', font=("Arial", 6), tags="dot")

    overlay.update()



def execute_solve():
    """Execute the complete solve pipeline."""
    print("\n🚀 Starting solve process...")
    update_overlay_status("Starting...")

    # Capture screenshot and process
    print("Taking screenshot...")
    update_overlay_status("Capturing...")
    screenshot = vision.capture_screen(config)
    screenshot.save("screenshot.png")

    print("Processing image...")
    update_overlay_status("Processing...")
    processed_image = vision.to_grid(screenshot, grid_size=puzzle_size)
    processed_image = vision.clean_black(processed_image)
    processed_image.save("processed.png")
    print("Saved processed image to processed.png")

    print("Matching wire pairs...")
    update_overlay_status("Matching...")
    matched_pairs = vision.match(processed_image, grid_size=puzzle_size)
    print(f"Found {len(matched_pairs)} wire pairs: {matched_pairs}")

    print("Solving puzzle...")
    update_overlay_status("Solving...")
    solutions = solver.solve(matched_pairs, grid_size=puzzle_size)
    print("Solution paths:")
    for i, path in enumerate(solutions):
        if path:
            print(f"  Pair {i+1}: {path}")
        else:
            print(f"  Pair {i+1}: No solution found")

    print("Creating visualization...")
    update_overlay_status("Visualizing...")
    visualization = vision.visualize_path(solutions, processed=processed_image, grid_size=puzzle_size)
    visualization.save("output.png")
    print("Saved solution visualization to output.png")

    # Display solution in overlay
    draw_solution_in_overlay(solutions, processed_image, grid_size=puzzle_size)

    if auto_mode:
        update_overlay_status("Executing...")
        print("Executing solution...")
        automation.complete_solve(solutions, config, grid_size=puzzle_size)
        print("✅ Done! Press Left Alt again to solve another puzzle.\n")
        update_overlay_status("Ready")
    else:
        update_overlay_status("Solved")
        print("✅ Solution displayed! Press Left Alt again to solve another puzzle.\n")

# Track pressed keys for hotkey combination
pressed_keys = set()

def on_key_press(key):
    """Handle key press events."""
    pressed_keys.add(key)

    # Check for Left Alt key - always work, but behavior depends on auto mode
    if key == Key.alt_l:
        # Schedule execute_solve to run on main thread
        if overlay:
            overlay.after(0, execute_solve)

def on_key_release(key):
    """Handle key release events."""
    try:
        pressed_keys.discard(key)
    except KeyError:
        pass

def run_keyboard_listener():
    """Run keyboard listener in background thread."""
    with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
        try:
            listener.join()
        except KeyboardInterrupt:
            print("\nExiting...")

def main():
    """Main function that runs overlay on main thread."""
    global root, overlay, canvas, status_text, auto_mode

    # Set auto mode from command line arguments
    auto_mode = args.auto

    # Create overlay on main thread
    create_overlay()

    # Always start keyboard listener since Alt hotkey works in both modes
    keyboard_thread = threading.Thread(target=run_keyboard_listener, daemon=True)
    keyboard_thread.start()

    if auto_mode:
        print("🎮 System ready! Press Left Alt to solve and execute puzzles.")
    else:
        print("🎮 System ready! Press Left Alt to solve and display puzzles (no automation).")

    # Run root window mainloop on main thread (this will block until window is closed)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\nExiting...")

# Run the main function
if __name__ == "__main__":
    main()
