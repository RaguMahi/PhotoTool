import numpy as np
from PIL import Image
import cv2

def get_image_info(image):
    """Get basic information about the image"""
    return {
        "Format": image.format,
        "Mode": image.mode,
        "Size": f"{image.size[0]}x{image.size[1]}",
        "Resolution": f"{image.info.get('dpi', 'N/A')}",
    }

def convert_to_cv2(pil_image):
    """Convert PIL Image to CV2 format"""
    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

def convert_to_pil(cv2_image):
    """Convert CV2 image to PIL format"""
    return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))
