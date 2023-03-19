import argparse
import json

from PIL import Image


def apply_tint(img, tint_percentage):
    # Convert tint_percentage to a value between 0 and 1
    tint_factor = 1 - tint_percentage / 100

    # Apply the tint to each pixel
    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            new_pixel = tuple(int(c * tint_factor) for c in pixel[:3]) + pixel[3:]
            img.putpixel((x, y), new_pixel)

    return img


def detect_tint_percentage(img, sample_area):
    x1, y1, x2, y2 = sample_area
    total_pixels = (x2 - x1) * (y2 - y1)
    total_tint_percentage = 0

    # Iterate through the pixels in the sample area
    for y in range(y1, y2):
        for x in range(x1, x2):
            pixel = img.getpixel((x, y))
            r, g, b = pixel[:3]

            # Calculate the tint percentage for each channel and average them
            r_tint = 1 - r / 255
            g_tint = 1 - g / 255
            b_tint = 1 - b / 255
            tint_percentage = (r_tint + g_tint + b_tint) / 3

            # Add the tint percentage to the total
            total_tint_percentage += tint_percentage

    # Calculate the average tint percentage for the sample area
    average_tint_percentage = (total_tint_percentage / total_pixels) * 100

    return average_tint_percentage


def create_mask_from_images(lock_screen_image):
    # Create a mask with black pixels from the circle image that are not black in the original image
    width, height = lock_screen_image.size
    mask = Image.new("L", (width, height), 0)
    min_x, min_y, max_x, max_y = width, height, 0, 0
    border_size = int(width * 0.05)
    for y in range(int(width * 0.05), height - int(width * 0.05)):
        for x in range(border_size, width - border_size):
            circle_pixel = lock_screen_image.getpixel((x, y))
            if circle_pixel[:3] == (0, 0, 0):
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)

    # make mask square
    for y in range(min_y, max_y):
        for x in range(min_x, max_x):
            mask.putpixel((x, y), 255)

    return mask


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)

    lock_screen_password = config["input"]["password"]
    original = config["output"]["source_cropped"]
    output = config["output"]["result"]

    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Apply tint to the source image.')
    parser.add_argument('--tint', type=float, default=0, help='Tint percentage (float) to apply (default: 0)')
    parser.add_argument('--auto-tint', action='store_true', help='Automatically detect tint percentage from the source image')
    parser.add_argument('--sample-area', nargs=4, type=int, default=[200, 200, 400, 400], help='Sample area for automatic tint detection (default: 200, 200, 400, 400)')

    # Parse the arguments and call the main function
    args = parser.parse_args()
    tint_percentage = args.tint
    lock_screen_img = Image.open(lock_screen_password)
    original_img = Image.open(original)
    original_img = original_img.resize(lock_screen_img.size)

    mask = create_mask_from_images(lock_screen_img)
    output_img = Image.new("RGB", original_img.size, (0, 0, 0))
    output_img.paste(original_img, (0, 0), mask)

    # Find the bounding box of the mask
    bbox = mask.getbbox()

    # Crop the output image to the bounding box
    output_img = output_img.crop(bbox)

    if args.auto_tint or args.sample_area:
        if args.tint:
            print("Warning: tint percentage will be ignored when using automatic tint detection")
        password_screen_image_path = config["input"]["password"]
        password_img = Image.open(password_screen_image_path)
        tint_percentage = detect_tint_percentage(password_img, args.sample_area)

    if tint_percentage:
        output_img = apply_tint(output_img, tint_percentage)

    # Save the output image
    output_img.save(output)
