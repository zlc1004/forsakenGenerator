import time

start = time.time()

import vision
import solver
from PIL import Image

input_image = Image.open("input.png")
input_image = vision.to_6x6(input_image)
input_image = vision.clean_black(input_image)
matched_pairs = vision.match(input_image)
solve_result = solver.solve(matched_pairs)
print(solve_result)

end = time.time()
print(f"Execution time: {end - start} seconds")