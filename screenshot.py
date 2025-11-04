#!/usr/bin/env python3
"""
Simple script to take a screenshot of the entire screen.
"""

from PIL import Image
import mss
import datetime
import os

def take_screenshot(filename=None):
    """
    Take a screenshot of the entire screen.

    Args:
        filename: Optional filename to save the screenshot.
                 If None, generates a timestamp-based filename.

    Returns:
        PIL Image object of the screenshot
    """
    # Take screenshot of entire screen using mss
    with mss.mss() as sct:
        # Capture the entire screen (monitor 1)
        monitor = sct.monitors[1]  # monitors[0] is all monitors combined, monitors[1] is primary
        screenshot_mss = sct.grab(monitor)

        # Convert to PIL Image
        screenshot = Image.frombytes('RGB', (screenshot_mss.width, screenshot_mss.height), screenshot_mss.rgb)

    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"

    # Save screenshot
    screenshot.save(filename)
    print(f"Screenshot saved as: {filename}")
    print(f"Image resolution: {screenshot.size[0]}x{screenshot.size[1]}")

    return screenshot

def main():
    """Main function for command line usage."""
    import argparse

    parser = argparse.ArgumentParser(description='Take a screenshot of the entire screen')
    parser.add_argument('-o', '--output',
                        help='Output filename (default: screenshot_TIMESTAMP.png)')

    args = parser.parse_args()

    # Take screenshot
    take_screenshot(args.output)

if __name__ == "__main__":
    main()
