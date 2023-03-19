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


def create_mask_from_images(lock_screen_image, as_circle=False, scale_percentage=100, transform=(0, 0)):
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

    center_x = (min_x + max_x) // 2 + transform[0]
    center_y = (min_y + max_y) // 2 + transform[1]
    mask_width = max_x - min_x
    mask_height = max_y - min_y
    new_width = int(mask_width * (scale_percentage / 100))
    new_height = int(mask_height * (scale_percentage / 100))
    min_x = max(center_x - new_width // 2, 0)
    max_x = min(center_x + new_width // 2, width)
    min_y = max(center_y - new_height // 2, 0)
    max_y = min(center_y + new_height // 2, height)

    if as_circle:
        # Fill the circle mask
        for y in range(height):
            for x in range(width):
                dx = x - center_x
                dy = y - center_y
                distance = (dx * dx + dy * dy) ** 0.5
                if distance <= new_width // 2:
                    mask.putpixel((x, y), 255)
    else:
        # Fill the square mask
        for y in range(min_y, max_y):
            for x in range(min_x, max_x):
                mask.putpixel((x, y), 255)

    return mask


def main():
    with open("config.json") as f:
        config = json.load(f)

    lock_screen_password = config["input"]["password"]
    original = config["output"]["source_cropped"]
    output = config["output"]["result"]

    # Set up the argument parser
    parser = argparse.ArgumentParser(description='Automate blending images')
    parser.add_argument('--tint', type=float, default=0,
                        help='Tint percentage (float) to apply (default: 0)')
    parser.add_argument('--auto-tint', action='store_true', default=False,
                        help='Automatically detect tint percentage from the source image')
    parser.add_argument('--sample-area', nargs=4, type=int, default=None,
                        help='Sample area for automatic tint detection (default: 200, 200, 400, 400)')
    parser.add_argument('--mask', action='store_true', default=False,
                        help='Create a mask from the lock screen image')
    parser.add_argument('--circle', action='store_true', default=False,
                        help='Create a mask as a circle from the lock screen image')
    parser.add_argument('--scale', type=int, default=100,
                        help='Increase or decrease the size of the mask scale percentage (default: 100)')
    # Parse the arguments and call the main function
    args = parser.parse_args()
    tint_percentage = args.tint
    sample_area = args.sample_area or [200, 200, 400, 400]
    lock_screen_img = Image.open(lock_screen_password)
    original_img = Image.open(original)
    original_img = original_img.resize(lock_screen_img.size)

    mask = create_mask_from_images(lock_screen_img, as_circle=args.circle, scale_percentage=args.scale)
    output_img = Image.new("RGBA", original_img.size, (0, 0, 0, 0))
    output_img.paste(original_img, (0, 0), mask)

    # Find the bounding box of the mask
    bbox = mask.getbbox()
    if args.mask:
        # Save the mask
        mask_layer = config["output"]["mask_layer"]
        try:
            mask.save(mask_layer)
        except OSError:
            mask.convert("RGB").save(mask_layer)

    # Crop the output image to the bounding box
    output_img = output_img.crop(bbox)

    if args.auto_tint or args.sample_area:
        if args.tint:
            print("Warning: tint percentage will be ignored when using automatic tint detection")
        password_screen_image_path = config["input"]["password"]
        password_img = Image.open(password_screen_image_path)
        tint_percentage = detect_tint_percentage(password_img, sample_area)

    if tint_percentage:
        output_img = apply_tint(output_img, tint_percentage)

    # Save the output image
    try:
        output_img.save(output)
    except OSError:
        output_img.convert("RGB").save(output)


if __name__ == "__main__":
    main()
