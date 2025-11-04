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
    return (x, y)

def count_non_black_pixels(image):
    pixels = list(image.getdata())
    black = (0, 0, 0)
    return len(pixels) - pixels.count(black)

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
