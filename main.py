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
from pynput import keyboard
from pynput.keyboard import Key, KeyCode

# Get config from user input
config_input = input("Enter config (i|x|y|size or b<base64>): ")

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
print("Press Left Alt to start solving...")

def execute_solve():
    """Execute the complete solve pipeline."""
    print("\n🚀 Starting solve process...")

    # Capture screenshot and process
    print("Taking screenshot...")
    screenshot = vision.capture_screen(config)
    screenshot.save("screenshot.png")

    print("Processing image...")
    processed_image = vision.to_6x6(screenshot)
    processed_image = vision.clean_black(processed_image)
    processed_image.save("processed.png")
    print("Saved processed image to processed.png")

    print("Matching wire pairs...")
    matched_pairs = vision.match(processed_image)
    print(f"Found {len(matched_pairs)} wire pairs: {matched_pairs}")

    print("Solving puzzle...")
    solutions = solver.solve(matched_pairs)
    print("Solution paths:")
    for i, path in enumerate(solutions):
        if path:
            print(f"  Pair {i+1}: {path}")
        else:
            print(f"  Pair {i+1}: No solution found")

    print("Creating visualization...")
    visualization = vision.visualize_path(solutions)
    visualization.save("output.png")
    print("Saved solution visualization to output.png")

    print("Executing solution...")
    automation.complete_solve(solutions, config)
    print("✅ Done! Press Left Alt again to solve another puzzle.\n")

# Track pressed keys for hotkey combination
pressed_keys = set()

def on_key_press(key):
    """Handle key press events."""
    pressed_keys.add(key)

    # Check for Left Alt key
    if key == Key.alt_l:
        execute_solve()

def on_key_release(key):
    """Handle key release events."""
    try:
        pressed_keys.discard(key)
    except KeyError:
        pass

# Set up keyboard listener
with keyboard.Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    try:
        listener.join()
    except KeyboardInterrupt:
        print("\nExiting...")
        pass
