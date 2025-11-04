from collections import deque
import copy

def solve(pairs, grid_size=(6, 6)):
    """
    Solves Flow Free puzzle using backtracking to ensure all pairs can be connected.

    Args:
        pairs: List of coordinate pairs [[(x1,y1), (x2,y2)], ...]
        grid_size: Tuple (width, height) of the grid

    Returns:
        List of paths, where each path is a list of turning points from start to end
    """
    width, height = grid_size
    grid = [[0 for _ in range(width)] for _ in range(height)]

    # Mark start and end points
    for i, [(x1, y1), (x2, y2)] in enumerate(pairs):
        grid[y1][x1] = i + 1  # Pair number
        grid[y2][x2] = i + 1

    # Use backtracking to find solution for all pairs
    solutions = [None] * len(pairs)
    if backtrack_solve(grid, pairs, solutions, 0, grid_size):
        # Convert solutions to simplified paths
        simplified_solutions = []
        for path in solutions:
            if path:
                simplified_solutions.append(simplify_path(path))
            else:
                simplified_solutions.append([])
        return simplified_solutions
    else:
        # No solution found for all pairs
        return [[] for _ in pairs]

def backtrack_solve(grid, pairs, solutions, pair_index, grid_size):
    """
    Backtracking function to solve all pairs.
    """
    # Base case: all pairs solved
    if pair_index == len(pairs):
        return True

    start, end = pairs[pair_index]
    start_x, start_y = start
    end_x, end_y = end

    # Find all possible paths for this pair
    possible_paths = find_all_paths(grid, start, end, pair_index + 1, grid_size)

    # Try each possible path
    for path in possible_paths:
        # Make a copy of the grid to test this path
        grid_copy = copy.deepcopy(grid)

        # Mark the path in the grid (except start and end which are already marked)
        for x, y in path[1:-1]:
            grid_copy[y][x] = pair_index + 1

        # Store this solution
        solutions[pair_index] = path

        # Recursively try to solve remaining pairs
        if backtrack_solve(grid_copy, pairs, solutions, pair_index + 1, grid_size):
            # Update the original grid with this successful path
            for x, y in path[1:-1]:
                grid[y][x] = pair_index + 1
            return True

    # No path worked, backtrack
    solutions[pair_index] = None
    return False

def find_all_paths(grid, start, end, pair_id, grid_size, max_paths=100):
    """
    Find multiple possible paths between start and end using BFS.
    Limits the number of paths to avoid infinite search.
    """
    width, height = grid_size
    start_x, start_y = start
    end_x, end_y = end

    all_paths = []

    # BFS queue: (x, y, path, visited_set)
    queue = deque([(start_x, start_y, [(start_x, start_y)], {(start_x, start_y)})])

    directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]  # up, down, right, left

    while queue and len(all_paths) < max_paths:
        x, y, path, visited = queue.popleft()

        # If we reached the end
        if x == end_x and y == end_y:
            all_paths.append(path)
            continue

        # Explore neighbors
        for dx, dy in directions:
            nx, ny = x + dx, y + dy

            # Check bounds
            if 0 <= nx < width and 0 <= ny < height:
                # Check if cell is available
                if (nx, ny) not in visited:
                    cell_value = grid[ny][nx]
                    # Can move to empty cell (0) or the target cell (same pair_id)
                    if cell_value == 0 or (nx == end_x and ny == end_y and cell_value == pair_id):
                        new_visited = visited.copy()
                        new_visited.add((nx, ny))
                        new_path = path + [(nx, ny)]
                        queue.append((nx, ny, new_path, new_visited))

    # Sort paths by length (prefer shorter paths)
    all_paths.sort(key=len)
    return all_paths



def simplify_path(path):
    """
    Simplify path to only include turning points (where direction changes).
    """
    if len(path) <= 2:
        return path

    simplified = [path[0]]  # Always include start

    for i in range(1, len(path) - 1):
        prev_x, prev_y = path[i - 1]
        curr_x, curr_y = path[i]
        next_x, next_y = path[i + 1]

        # Calculate directions
        dir1 = (curr_x - prev_x, curr_y - prev_y)
        dir2 = (next_x - curr_x, next_y - curr_y)

        # If direction changes, this is a turning point
        if dir1 != dir2:
            simplified.append((curr_x, curr_y))

    simplified.append(path[-1])  # Always include end
    return simplified

def print_grid_with_paths(pairs, solutions, grid_size=(6, 6)):
    """
    Debug function to visualize the solved grid.
    """
    width, height = grid_size
    grid = [["." for _ in range(width)] for _ in range(height)]

    # Mark paths
    for i, (pair, path) in enumerate(zip(pairs, solutions)):
        pair_char = str(i + 1)
        if path:
            for x, y in path:
                grid[y][x] = pair_char

    # Print grid
    for row in grid:
        print(" ".join(row))
    print()
