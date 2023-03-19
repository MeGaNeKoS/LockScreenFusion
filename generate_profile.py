import json

from PIL import Image


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

    # Save the output image
    output_img.save(output)
