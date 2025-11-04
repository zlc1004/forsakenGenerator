try:
    from z3 import Solver, Sum, Int, If, And, Or, sat
    Z3_AVAILABLE = True
except ImportError:
    Z3_AVAILABLE = False
    print("⚠️  Z3 solver not available. Install with: pip install z3-solver")

def solve(pairs, grid_size=(6, 6)):
    """
    Solve Flow Free puzzle using Z3 constraint solver approach.

    Args:
        pairs: List of coordinate pairs [[(x1,y1), (x2,y2)], ...]
        grid_size: Tuple (width, height) of the grid

    Returns:
        List of paths, where each path is a list of turning points from start to end
    """
    if not Z3_AVAILABLE:
        print("❌ Z3 solver not available, falling back to DFS solver")
        return solve_with_dfs(pairs, grid_size)

    width, height = grid_size
    print(f"🔍 Z3 constraint solving {len(pairs)} pairs...")

    # Create board with pair endpoints
    board = [[0 for _ in range(width)] for _ in range(height)]
    for i, [(x1, y1), (x2, y2)] in enumerate(pairs):
        pair_id = i + 1
        board[y1][x1] = pair_id
        board[y2][x2] = pair_id

    print("📋 Initial board:")
    for row in board:
        print("   ", row)

    # Solve using Z3 constraints
    solved_board = solve_with_z3(board, height, width)

    if solved_board:
        print("✅ Z3 solved the puzzle!")
        print("📋 Solved board:")
        for row in solved_board:
            print("   ", row)

        # Extract paths from solved board
        paths = extract_paths_from_solution(solved_board, pairs, grid_size)
        return paths
    else:
        print("❌ Z3 could not find a solution")
        return [[] for _ in pairs]

def solve_with_z3(board, M, N):
    """
    Use Z3 constraint solver to solve the Flow Free puzzle.
    Based on the algorithm from FlowFree.py
    """
    print("🔧 Setting up Z3 constraints...")

    # Create Z3 variables for each cell
    B = [[Int(f'B_{i}_{j}') for j in range(N)] for i in range(M)]

    s = Solver()

    # Constraint 1: Each cell either keeps its original value or gets assigned a valid color
    # Fixed: Allow cells to be 0 (empty) as well
    s.add([If(board[i][j] != 0,
              B[i][j] == board[i][j],
              And(B[i][j] >= 0, B[i][j] <= len([cell for row in board for cell in row if cell != 0]) // 2))
           for j in range(N) for i in range(M)])

    print(f"🎯 Added basic constraints for {M}x{N} grid")

    # Constraint 2: Flow connectivity rules
    for i in range(M):
        for j in range(N):
            # Count neighbors with same color (Manhattan distance = 1)
            neighbors = []
            for k in range(M):
                for l in range(N):
                    if abs(k - i) + abs(l - j) == 1:  # Adjacent cells only
                        neighbors.append((k, l))

            same_neighs_ij = Sum([If(And(B[i][j] != 0, B[i][j] == B[k][l]), 1, 0)
                                 for k, l in neighbors])

            if board[i][j] != 0:  # Endpoint cells
                s.add(same_neighs_ij == 1)  # Exactly one neighbor with same color
            else:  # Empty cells
                s.add(Or(
                    B[i][j] == 0,  # Cell remains empty
                    same_neighs_ij == 2  # Or has exactly 2 neighbors (path cell)
                ))

    print("🔧 Solving with Z3...")

    # Solve the constraints
    result = s.check()
    print(f"🔍 Z3 result: {result}")

    if result == sat:
        print("✅ Z3 found a solution!")
        m = s.model()
        solution = [[m[B[i][j]].as_long() for j in range(N)] for i in range(M)]
        return solution
    else:
        print("❌ Z3 says no solution exists")
        # Debug: show why it's unsat
        if hasattr(s, 'unsat_core'):
            print("🔍 Unsat core:", s.unsat_core())
        return None

def extract_paths_from_solution(solved_board, pairs, grid_size):
    """
    Extract paths from the Z3 solution by tracing connected components.
    """
    paths = []

    for i, [(x1, y1), (x2, y2)] in enumerate(pairs):
        pair_id = i + 1

        # Find path using DFS from start to end
        path = find_path_in_solution(solved_board, (x1, y1), (x2, y2), pair_id, grid_size)

        if path:
            simplified = simplify_path(path)
            paths.append(simplified)
        else:
            paths.append([])

    return paths

def find_path_in_solution(board, start, end, target_value, grid_size):
    """
    Find path between start and end points in the solved board.
    """
    width, height = grid_size
    start_x, start_y = start
    end_x, end_y = end

    visited = set()

    def dfs(x, y, path):
        if x == end_x and y == end_y:
            return path + [(x, y)]

        visited.add((x, y))

        # Check all 4 directions
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = x + dx, y + dy

            if (0 <= nx < width and 0 <= ny < height and
                (nx, ny) not in visited and
                board[ny][nx] == target_value):

                result = dfs(nx, ny, path + [(x, y)])
                if result:
                    return result

        visited.remove((x, y))
        return None

    return dfs(start_x, start_y, [])

def solve_with_dfs(pairs, grid_size):
    """
    Fallback DFS solver when Z3 is not available.
    """
    # Simple DFS implementation as fallback
    print("🔄 Using DFS fallback solver...")
    # This would be a simpler implementation
    return [[] for _ in pairs]





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
