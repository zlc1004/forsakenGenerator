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
import time

start = time.time()

import vision
import solver
from PIL import Image

# "-" is empty tile
# Each pair represents two wire dots that need to be connected

data = [
    [(0, 5), (4, 3)],
    [(1, 1), (4, 1)],
    [(1, 4), (1, 5)],
    [(3, 0), (5, 1)],
    [(3, 3), (4, 4)],
    [(4, 0), (5, 0)],
]


def print_grid(data):
    grid = [["-"] * 6 for _ in range(6)]
    for pair_num, [(x1, y1), (x2, y2)] in enumerate(data, 1):
        grid[x1][y1] = str(pair_num)
        grid[x2][y2] = str(pair_num)
    # grid = list(map(list, zip(*grid)))  # Transpose for correct orientation
    for row in grid:
        print(" ".join(row))
    print()


print_grid(data)

screenshot = vision.capture_screen()
screenshot.save("screenshot.png")

input_image = Image.open("input.png")
input_image = vision.to_6x6(input_image)
input_image = vision.clean_black(input_image)

print(list(input_image.getdata()))

print("non black pixels count:")
print(vision.count_non_black_pixels(input_image))

print("matched pairs:")
matched_pairs = vision.match(input_image)
print(matched_pairs)

print_grid(matched_pairs)

solve_result = solver.solve(matched_pairs)

print(solve_result)

visualized_image = vision.visualize_path(solve_result)
visualized_image.save("output.png")

end = time.time()
print(f"Execution time: {end - start} seconds")