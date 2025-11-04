from PIL import Image
import mss
import numpy as np

def capture_screen(region=None):
    with mss.mss() as sct:
        screenshot = sct.grab(region) if region else sct.grab(sct.monitors[0])
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        return img
def to_6x6(image):
    return image.resize((12,12)).convert("RGB").resize((6,6))

def clean_black(image, allowance=10):
    pixels = list(image.getdata())
    output_pixels = []
    black = 10
    for r, g, b in pixels:
        if abs(r - black) <= allowance and abs(g - black) <= allowance and abs(b - black) <= allowance:
            output_pixels.append((0, 0, 0))
        else:
            output_pixels.append((r, g, b))
    output_image = Image.new("RGB", image.size)
    output_image.putdata(output_pixels)
    return output_image

def closest(colors,color):
    colors = np.array(colors)
    color = np.array(color)
    distances = np.sqrt(np.sum((colors-color)**2,axis=1))
    index_of_smallest = np.where(distances==np.amin(distances))[0][0]
    smallest_distance = colors[index_of_smallest]
    return tuple(smallest_distance)

def image_index_to_pos(image_index, image_size=(6, 6)):
    """Convert linear image index to (x, y) coordinates."""
    width, height = image_size
    x = image_index // height
    y = image_index % height
    return (y, x)

def count_non_black_pixels(image):
    pixels = list(image.getdata())
    black = (0, 0, 0)
    return len(pixels) - pixels.count(black)

def visualize_path(solutions, grid_size=(6, 6), cell_size=50):
    """
    Create a visual representation of the solved paths.

    Args:
        solutions: List of paths from solver.solve()
        grid_size: Tuple (width, height) of the grid
        cell_size: Size of each cell in pixels

    Returns:
        PIL Image showing the solved paths
    """
    from PIL import ImageDraw

    width, height = grid_size
    img_width = width * cell_size
    img_height = height * cell_size

    # Create white background
    image = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(image)

    # Draw grid lines
    for i in range(width + 1):
        x = i * cell_size
        draw.line([(x, 0), (x, img_height)], fill='lightgray', width=1)

    for i in range(height + 1):
        y = i * cell_size
        draw.line([(0, y), (img_width, y)], fill='lightgray', width=1)

    # Define colors for different paths
    colors = [
        'red', 'blue', 'green', 'orange', 'purple', 'brown',
        'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow',
        'darkred', 'darkblue', 'darkgreen'
    ]

    # Draw each path
    for path_idx, path in enumerate(solutions):
        if not path or len(path) < 2:
            continue

        color = colors[path_idx % len(colors)]

        # Draw start and end points as circles
        start_x, start_y = path[0]
        end_x, end_y = path[-1]

        start_pixel_x = start_x * cell_size + cell_size // 2
        start_pixel_y = start_y * cell_size + cell_size // 2
        end_pixel_x = end_x * cell_size + cell_size // 2
        end_pixel_y = end_y * cell_size + cell_size // 2

        # Draw start point (larger circle)
        draw.ellipse([
            start_pixel_x - 8, start_pixel_y - 8,
            start_pixel_x + 8, start_pixel_y + 8
        ], fill=color, outline='black', width=2)

        # Draw end point (larger circle)
        draw.ellipse([
            end_pixel_x - 8, end_pixel_y - 8,
            end_pixel_x + 8, end_pixel_y + 8
        ], fill=color, outline='black', width=2)

        # Draw path lines between turning points
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]

            pixel_x1 = x1 * cell_size + cell_size // 2
            pixel_y1 = y1 * cell_size + cell_size // 2
            pixel_x2 = x2 * cell_size + cell_size // 2
            pixel_y2 = y2 * cell_size + cell_size // 2

            draw.line([(pixel_x1, pixel_y1), (pixel_x2, pixel_y2)],
                     fill=color, width=4)

        # Draw turning points as small circles
        for i in range(1, len(path) - 1):  # Skip start and end
            x, y = path[i]
            pixel_x = x * cell_size + cell_size // 2
            pixel_y = y * cell_size + cell_size // 2

            draw.ellipse([
                pixel_x - 4, pixel_y - 4,
                pixel_x + 4, pixel_y + 4
            ], fill=color, outline='black', width=1)

        # Add path number label
        label_x = start_pixel_x + 12
        label_y = start_pixel_y - 12
        draw.text((label_x, label_y), str(path_idx + 1), fill='black')

    return image

def match(image):
    """Matches non-black pixels in pairs of closest colors and returns their positions."""
    pixels = list(image.getdata())

    # Create list of (index, color) for non-black pixels
    non_black_data = [(i, pixels[i]) for i in range(len(pixels)) if pixels[i] != (0, 0, 0)]

    matched_pairs = []
    used_indices = set()

    for i, (pixel_index, color) in enumerate(non_black_data):
        if i in used_indices:
            continue

        # Get available colors and their data
        available_data = [(j, non_black_data[j]) for j in range(len(non_black_data))
                         if j not in used_indices and j != i]

        if not available_data:
            continue

        available_colors = [data[1][1] for data in available_data]  # Extract colors
        closest_color = closest(available_colors, color)

        # Find the index in non_black_data that has this closest color
        for j, (other_pixel_index, other_color) in enumerate(non_black_data):
            if j not in used_indices and j != i and other_color == closest_color:
                # Convert indices to positions
                pos1 = image_index_to_pos(pixel_index)
                pos2 = image_index_to_pos(other_pixel_index)
                matched_pairs.append([pos1, pos2])
                used_indices.add(i)
                used_indices.add(j)
                break

    return matched_pairs
