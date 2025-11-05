from PIL import Image, ImageDraw
import mss
import numpy as np

def capture_screen(config):
    region_x, region_y, region_height = config[0], config[1], config[2]
    region_width = region_height  # Square region
    with mss.mss() as sct:
        screenshot = sct.grab((region_x, region_y, region_x + region_width, region_y + region_height))
        img = Image.frombytes('RGB', (screenshot.width, screenshot.height), screenshot.rgb)
        return img

def to_grid(image, grid_size=6, debug=False):
    """
    Convert square input image to NxN grid by sampling dominant colors from each cell.

    Args:
        image: Square PIL image (e.g., 60x60, 120x120, etc.)
        grid_size: Size of the grid (default 6 for 6x6)
        debug: If True, saves combined cell areas to grid.png (default False)

    Returns:
        NxN PIL image with dominant colors from each cell
    """
    # Ensure square image
    width, height = image.size
    if width != height:
        # Crop to square if not already
        size = min(width, height)
        left = (width - size) // 2
        top = (height - size) // 2
        image = image.crop((left, top, left + size, top + size))
        width = height = size

    image = image.convert("RGB")
    cell_size = width / grid_size  # Size of each cell in the input image

    # Create output NxN image
    output_image = Image.new("RGB", (grid_size, grid_size))
    pixels = []

    # For debug mode, collect all cell crops
    if debug:
        cell_crops = []

    for row in range(grid_size):
        for col in range(grid_size):
            # Calculate cell boundaries in input image - use entire cell
            left = int(col * cell_size)
            top = int(row * cell_size)
            right = int((col + 1) * cell_size)
            bottom = int((row + 1) * cell_size)

            # Crop the entire cell area
            cell_crop = image.crop((left, top, right, bottom))

            # Store for debug visualization
            if debug:
                cell_crops.append((row, col, cell_crop))

            # Get dominant color of this cell
            dominant_color = get_average_color(cell_crop)
            pixels.append(dominant_color)

    # Save debug visualization if requested
    if debug:
        save_debug_grid(cell_crops, grid_size)

    # Set all pixels in the NxN output
    output_image.putdata(pixels)
    return output_image

def save_debug_grid(cell_crops, grid_size):
    """
    Save all cell cropped areas combined into a single grid image.

    Args:
        cell_crops: List of (row, col, crop_image) tuples
        grid_size: Size of the grid
    """
    if not cell_crops:
        return

    # Get the size of individual crops (assume all are same size)
    crop_width, crop_height = cell_crops[0][2].size

    # Calculate total image size
    total_width = crop_width * grid_size
    total_height = crop_height * grid_size

    # Create combined image
    combined_image = Image.new('RGB', (total_width, total_height), 'black')

    # Paste each crop in the correct position
    for row, col, crop_image in cell_crops:
        x = col * crop_width
        y = row * crop_height
        combined_image.paste(crop_image, (x, y))

    # Save the combined image
    combined_image.save('grid.png')
    print(f"Debug: Saved cell crops grid to grid.png ({total_width}x{total_height})")

def get_average_color(image):
    """Calculate the average color of an image."""

    data = list(image.getdata())

    data_set = set(data)
    counts={}
    for color in data_set:
        counts[color]=data.count(color)

    dominant_color = max(counts, key=counts.get)
    return dominant_color

    # Convert to numpy array for easy averaging
    # img_array = np.array(image)

    # # Calculate mean for each color channel
    # if len(img_array.shape) == 3:  # RGB image
    #     avg_color = np.mean(img_array, axis=(0, 1))
    #     return tuple(int(c) for c in avg_color)
    # else:  # Grayscale or other format
    #     avg_color = np.mean(img_array)
    #     return (int(avg_color), int(avg_color), int(avg_color))



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

def image_index_to_pos(image_index, grid_size=6):
    """Convert linear image index to (x, y) coordinates."""
    x = image_index // grid_size
    y = image_index % grid_size
    return (y, x)

def count_non_black_pixels(image):
    pixels = list(image.getdata())
    black = (0, 0, 0)
    return len(pixels) - pixels.count(black)

def visualize_path(solutions, processed=None, grid_size=6, cell_size=50):
    """
    Create a visual representation of the solved paths.

    Args:
        solutions: List of paths from solver.solve()
        processed: PIL Image object of the processed NxN image (optional)
        grid_size: Size of the grid (e.g., 6 for 6x6)
        cell_size: Size of each cell in pixels

    Returns:
        PIL Image showing the solved paths
    """

    img_width = grid_size * cell_size
    img_height = grid_size * cell_size

    # Create black background
    image = Image.new('RGB', (img_width, img_height), 'black')
    draw = ImageDraw.Draw(image)

    # Draw grid lines
    for i in range(grid_size + 1):
        x = i * cell_size
        draw.line([(x, 0), (x, img_height)], fill='gray', width=1)

    for i in range(grid_size + 1):
        y = i * cell_size
        draw.line([(0, y), (img_width, y)], fill='gray', width=1)

    # Function to get color from processed image
    def get_color_from_processed(x, y):
        if processed and 0 <= x < grid_size and 0 <= y < grid_size:
            # Get pixel color from processed image
            pixel_color = processed.getpixel((x, y))
            # If the color is black, use a default color
            if pixel_color == (0, 0, 0):
                return 'white'
            return pixel_color
        else:
            # Fallback colors if no processed image
            fallback_colors = [
                'red', 'blue', 'green', 'orange', 'purple', 'brown',
                'pink', 'gray', 'olive', 'cyan', 'magenta', 'yellow'
            ]
            return fallback_colors[0]

    # Draw each path
    for path_idx, path in enumerate(solutions):
        if not path or len(path) < 2:
            continue

        # Get color from the start point of the path in the processed image
        start_x, start_y = path[0]
        color = get_color_from_processed(start_x, start_y)

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

def match(image, grid_size=6):
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
                pos1 = image_index_to_pos(pixel_index, grid_size)
                pos2 = image_index_to_pos(other_pixel_index, grid_size)
                matched_pairs.append([pos1, pos2])
                used_indices.add(i)
                used_indices.add(j)
                break

    return matched_pairs
