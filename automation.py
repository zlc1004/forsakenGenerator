import pyautogui

pyautogui.PAUSE = 0.006

def pos_to_screen_pos(pos, config):
    region_x, region_y, region_height = config[0], config[1], config[2]
    x, y = pos
    cell_height = region_height / 6
    cell_width = region_height / 6  # Assuming square grid
    screen_x = region_x + x * cell_width + cell_width / 2
    screen_y = region_y + y * cell_height + cell_height / 2
    return (int(screen_x), int(screen_y))

def complete_solve(solve, config):
    """
    Automate the solution by drawing wire paths with mouse movements.

    Args:
        solve: List of paths, each path is a list of (x,y) coordinates
        config: [region_x, region_y, region_height] for screen positioning
    """
    import time

    for path_idx, steps in enumerate(solve):
        if not steps or len(steps) < 2:
            print(f"Skipping path {path_idx + 1}: insufficient steps")
            continue

        print(f"Drawing path {path_idx + 1}: {steps}")

        # Move to starting position
        start_screen_pos = pos_to_screen_pos(steps[0], config)
        pyautogui.moveTo(start_screen_pos[0], start_screen_pos[1])
        print(f"  Moving to start: {steps[0]} -> {start_screen_pos}")

        # Small delay before starting
        

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
            step_screen_pos = pos_to_screen_pos(expanded_path[i], config)
            pyautogui.dragTo(step_screen_pos[0], step_screen_pos[1], button="left", duration=0.00001, mouseDownUp=False, tween=pyautogui.easeInOutQuart)
            print(f"  Dragging to step {i}: {expanded_path[i]} -> {step_screen_pos}")

        # Mouse up to finish drawing
        pyautogui.mouseUp()
        print(f"  Mouse up - path {path_idx + 1} complete")

        time.sleep(pyautogui.PAUSE)

    print("All paths completed!")
