import cv2
import numpy as np
from PIL import Image
import io

def detect_fill_level(image_bytes):
    """
    Takes image bytes, returns fill level percentage (0-100)
    Uses color + edge detection to estimate how full a bin is
    """
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        return 0

    # Resize for consistency
    img = cv2.resize(img, (300, 400))
    height, width = img.shape[:2]

    # Convert to HSV for better color detection
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Detect dark regions (waste is usually darker)
    lower_dark = np.array([0, 0, 0])
    upper_dark = np.array([180, 255, 100])
    dark_mask = cv2.inRange(hsv, lower_dark, upper_dark)

    # Detect brown/green waste colors
    lower_waste = np.array([10, 30, 30])
    upper_waste = np.array([80, 255, 200])
    waste_mask = cv2.inRange(hsv, lower_waste, upper_waste)

    # Combine masks
    combined_mask = cv2.bitwise_or(dark_mask, waste_mask)

    # Find fill level by scanning from bottom up
    fill_rows = 0
    for row in range(height - 1, -1, -1):
        row_pixels = combined_mask[row, :]
        if np.sum(row_pixels) > width * 0.3 * 255:
            fill_rows += 1
        else:
            break

    fill_percentage = (fill_rows / height) * 100

    # Edge detection for additional accuracy
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = np.sum(edges) / (height * width * 255)
    
    # Combine both signals
    final_fill = min(100, (fill_percentage * 0.7) + (edge_density * 100 * 0.3))
    
    return round(final_fill, 2)


def analyze_bin_image(image_bytes):
    """
    Full analysis — returns fill level + status + recommendation
    """
    fill_level = detect_fill_level(image_bytes)

    if fill_level >= 90:
        status = "CRITICAL"
        color = "red"
        action = "Immediate collection required"
    elif fill_level >= 75:
        status = "HIGH"
        color = "orange"
        action = "Schedule collection today"
    elif fill_level >= 50:
        status = "MEDIUM"
        color = "yellow"
        action = "Monitor closely"
    else:
        status = "LOW"
        color = "green"
        action = "No action needed"

    return {
        "fill_level": fill_level,
        "status": status,
        "color": color,
        "action": action
    }