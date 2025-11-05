import pyautogui
import time

pyautogui.PAUSE = 0.01
pyautogui.PAUSE = 0.008
# pyautogui.PAUSE = 0.004
# pyautogui.PAUSE = 0.001
# pyautogui.PAUSE = 0

def pos_to_screen_pos(pos, config, grid_size=6):
    region_x, region_y, region_height = config[0], config[1], config[2]
    x, y = pos
    cell_height = region_height / grid_size
    cell_width = region_height / grid_size  # Assuming square grid
    screen_x = region_x + x * cell_width + cell_width / 2
    screen_y = region_y + y * cell_height + cell_height / 2
    return (int(screen_x), int(screen_y))

def complete_solve(solve, config, grid_size=6):
    """
    Automate the solution by drawing wire paths with mouse movements.

    Args:
        solve: List of paths, each path is a list of (x,y) coordinates
        config: [region_x, region_y, region_height] for screen positioning
        grid_size: Size of the puzzle grid (default 6 for 6x6)
    """
    time.sleep(pyautogui.PAUSE*3)  # Initial delay before starting
    for path_idx, steps in enumerate(solve):
        if not steps or len(steps) < 2:
            print(f"Skipping path {path_idx + 1}: insufficient steps")
            continue

        print(f"Drawing path {path_idx + 1}: {steps}")

        # Move to starting position
        start_screen_pos = pos_to_screen_pos(steps[0], config, grid_size)
        pyautogui.moveTo(start_screen_pos[0], start_screen_pos[1])
        print(f"  Moving to start: {steps[0]} -> {start_screen_pos}")

        # Small delay before starting

        time.sleep(pyautogui.PAUSE)
        # Mouse down to start drawing
        pyautogui.mouseDown()
        time.sleep(pyautogui.PAUSE)
        print(f"  Mouse down at {start_screen_pos}")

        # Create expanded path with intermediate points
        expanded_path = []
        for i in range(len(steps)):
            expanded_path.append(steps[i])

            # Add intermediate points between this step and the next
            if i < len(steps) - 1:
                current = steps[i]
                next_step = steps[i + 1]

                # Calculate intermediate points
                dx = next_step[0] - current[0]
                dy = next_step[1] - current[1]

                # Add points every cell if the distance is greater than 1
                distance = max(abs(dx), abs(dy))
                if distance > 1:
                    for j in range(1, distance):
                        intermediate_x = current[0] + (dx * j // distance)
                        intermediate_y = current[1] + (dy * j // distance)
                        expanded_path.append((intermediate_x, intermediate_y))

        # Drag through all expanded steps
        for i in range(1, len(expanded_path)):
            step_screen_pos = pos_to_screen_pos(expanded_path[i], config, grid_size)
            pyautogui.dragTo(step_screen_pos[0], step_screen_pos[1], button="left", duration=0.00001, mouseDownUp=False, tween=pyautogui.easeInOutQuart)
            print(f"  Dragging to step {i}: {expanded_path[i]} -> {step_screen_pos}")

        # Mouse up to finish drawing
        time.sleep(pyautogui.PAUSE)
        pyautogui.mouseUp()
        print(f"  Mouse up - path {path_idx + 1} complete")

        time.sleep(pyautogui.PAUSE*2)

    print("All paths completed!")
