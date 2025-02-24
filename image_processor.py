import numpy as np
from PIL import Image, ImageEnhance
import cv2

class ImageProcessor:
    def __init__(self):
        self.enhancers = {
            'brightness': ImageEnhance.Brightness,
            'contrast': ImageEnhance.Contrast,
            'sharpness': ImageEnhance.Sharpness,
        }

    def adjust_brightness(self, image, factor):
        """Adjust image brightness"""
        enhancer = self.enhancers['brightness'](image)
        factor = 1 + (factor / 100)
        return enhancer.enhance(factor)

    def adjust_contrast(self, image, factor):
        """Adjust image contrast"""
        enhancer = self.enhancers['contrast'](image)
        factor = 1 + (factor / 100)
        return enhancer.enhance(factor)

    def adjust_sharpness(self, image, factor):
        """Adjust image sharpness"""
        enhancer = self.enhancers['sharpness'](image)
        factor = 1 + (factor / 100)
        return enhancer.enhance(factor)

    def rotate_image(self, image, angle):
        """Rotate image by specified angle
        Args:
            image: PIL Image object
            angle: Rotation angle in degrees
        Returns:
            Rotated PIL Image object
        """
        # Use PIL's rotate method with expand=True to prevent cropping
        return image.rotate(angle, expand=True, resample=Image.Resampling.BICUBIC)

    def adjust_color_balance(self, image, red=0, green=0, blue=0):
        """Adjust RGB color balance"""
        # Convert to numpy array
        img_array = np.array(image)

        # Adjust each channel
        r, g, b = cv2.split(img_array)
        r = cv2.add(r, red)
        g = cv2.add(g, green)
        b = cv2.add(b, blue)

        # Merge channels back
        adjusted = cv2.merge([r, g, b])
        return Image.fromarray(adjusted)

    def resize_image(self, image, width_percent, height_percent=None):
        """Resize image maintaining aspect ratio if height_percent is None"""
        width = int(image.size[0] * width_percent / 100)
        if height_percent is None:
            height = int(image.size[1] * width_percent / 100)
        else:
            height = int(image.size[1] * height_percent / 100)
        return image.resize((width, height), Image.Resampling.LANCZOS)

    def merge_app_screenshot(self, template, screenshot, scale_factor=0.8, x_offset=0, y_offset=0):
        """Merge an app screenshot with a phone template"""
        # Convert images to RGBA to handle transparency
        template = template.convert('RGBA')
        screenshot = screenshot.convert('RGBA')

        # Create a new blank image with template size
        result = Image.new('RGBA', template.size, (0, 0, 0, 0))

        # Calculate dimensions to ensure screenshot fills the frame
        template_width, template_height = template.size
        screenshot_width, screenshot_height = screenshot.size

        # Calculate scaling factors for both dimensions
        width_scale = template_width / screenshot_width * scale_factor
        height_scale = template_height / screenshot_height * scale_factor

        # Use the larger scale to ensure complete coverage
        final_scale = max(width_scale, height_scale)

        # Calculate new dimensions
        new_width = int(screenshot_width * final_scale)
        new_height = int(screenshot_height * final_scale)

        # Resize screenshot to fill frame
        resized_screenshot = screenshot.resize((new_width, new_height), Image.Resampling.LANCZOS)

        # Calculate paste position (centered by default)
        paste_x = (template_width - new_width) // 2 + x_offset
        paste_y = (template_height - new_height) // 2 + y_offset

        # First paste the screenshot (background)
        result.paste(resized_screenshot, (paste_x, paste_y))

        # Then paste the template frame on top
        result.paste(template, (0, 0), template)

        return result

    def process_image(self, image, brightness=0, contrast=0, sharpness=0,
                     red=0, green=0, blue=0, width_percent=100, height_percent=None,
                     rotation=0):
        """Apply all processing steps to the image
        Args:
            image: PIL Image object
            brightness: Brightness adjustment (-100 to 100)
            contrast: Contrast adjustment (-100 to 100)
            sharpness: Sharpness adjustment (-100 to 100)
            red: Red channel adjustment (-100 to 100)
            green: Green channel adjustment (-100 to 100)
            blue: Blue channel adjustment (-100 to 100)
            width_percent: Width resize percentage (default: 100)
            height_percent: Height resize percentage (optional)
            rotation: Rotation angle in degrees (default: 0)
        Returns:
            Processed PIL Image object
        """
        # Create a copy to avoid modifying original
        processed = image.copy()

        # Apply rotation if needed
        if rotation != 0:
            processed = self.rotate_image(processed, rotation)

        # Apply basic adjustments
        if brightness != 0:
            processed = self.adjust_brightness(processed, brightness)
        if contrast != 0:
            processed = self.adjust_contrast(processed, contrast)
        if sharpness != 0:
            processed = self.adjust_sharpness(processed, sharpness)

        # Apply color adjustments
        if any([red != 0, green != 0, blue != 0]):
            processed = self.adjust_color_balance(processed, red, green, blue)

        # Resize if needed
        if width_percent != 100 or height_percent is not None:
            processed = self.resize_image(processed, width_percent, height_percent)

        return processed