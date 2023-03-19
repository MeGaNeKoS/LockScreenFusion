import json

from PIL import Image


def paste_center(bg_img, fg_img):
    """
    This function is to copy an image to a new resolution where the image keep it original size and positioned
    in the center of the new image.
    The new image is filled with black pixels.
    :param bg_img:
    :param fg_img:
    :return:
    """
    x = (bg_img.width - fg_img.width) // 2
    y = (bg_img.height - fg_img.height) // 2
    bg_img.paste(fg_img, (x, y))


def is_same_color(color1, color2):
    """
    This function to determine if a pixel is the same color with the next pixel.
    Since our pattern is a checkoard of non-black color at the border 5% of the image, we can use this thechnique.
    :param color1:
    :param color2:
    :return:
    """
    # color1[:3] == color2[:3] != (0,0,0) is not working.
    # This hack is fine as the pixel we're looking is from a white color, and since windows dimmed the color
    # Those RGB will be reduced by the same amount.
    return color1[0] == color1[1] == color1[2] == color2[0] == color2[1] == color2[2] != 0


def find_white_pixel_distances(ref_img):
    """
    This function is to find the distance between the white, solid color pixel on the left, right, top and bottom side.
    :param ref_img:
    :return:
    """
    width, height = ref_img.size
    center_y = height // 2
    center_x = width // 2
    left_distance, right_distance, top_distance, bottom_distance = None, None, None, None

    # Search for white pixel on the left side
    for x in range(width // 2):
        pixel_color = ref_img.getpixel((x, center_y))
        next_pixel_color = ref_img.getpixel((x + 1, center_y))
        if is_same_color(pixel_color, next_pixel_color):
            left_distance = x
            break

    # Search for white pixel on the right side
    for x in range(width - 1, width // 2, -1):
        pixel_color = ref_img.getpixel((x, center_y))
        next_pixel_color = ref_img.getpixel((x - 1, center_y))
        if is_same_color(pixel_color, next_pixel_color):
            right_distance = x - (width // 2)
            break

    # search for white pixel on the top side
    for y in range(height // 2):
        pixel_color = ref_img.getpixel((center_x, y))
        next_pixel_color = ref_img.getpixel((center_x, y + 1))
        if is_same_color(pixel_color, next_pixel_color):
            top_distance = y
            break

    # search for white pixel on the bottom side
    for y in range(height - 1, height // 2, -1):
        pixel_color = ref_img.getpixel((center_x, y))
        next_pixel_color = ref_img.getpixel((center_x, y - 1))
        if is_same_color(pixel_color, next_pixel_color):
            bottom_distance = y - (height // 2)
            break

    return left_distance, right_distance, top_distance, bottom_distance


def cut_edges_and_resize(ref_img, target_distances, ref_distances):
    # this need trial and error
    # But let's set an initial value
    left_diff = ref_distances[0] - target_distances[0]
    right_diff = ref_img.width - (ref_distances[1] - target_distances[1])
    top_diff = ref_distances[2] - target_distances[2]
    bottom_diff = ref_img.height - (ref_distances[3] - target_distances[3])
    while True:
        print(f"left_diff: {left_diff}, right_diff: {right_diff}, top_diff: {top_diff}, bottom_diff: {bottom_diff}")
        crop_ref_img = ref_img.crop((left_diff, top_diff, right_diff, bottom_diff))
        res_ref_img = crop_ref_img.resize(ref_img.size)
        cropped_white_distances = find_white_pixel_distances(res_ref_img)
        if zoomed_distances == cropped_white_distances:
            break
        print(f"cropped_white_distances: {cropped_white_distances}")
        print(f"zoomed_distances: {zoomed_distances}")
        if cropped_white_distances[0] < zoomed_distances[0]:
            left_diff -= 1
        elif cropped_white_distances[0] > zoomed_distances[0]:
            left_diff += 1
        if cropped_white_distances[1] < zoomed_distances[1]:
            right_diff -= 1
        elif cropped_white_distances[1] > zoomed_distances[1]:
            right_diff += 1
        if cropped_white_distances[2] < zoomed_distances[2]:
            top_diff -= 1
        elif cropped_white_distances[2] > zoomed_distances[2]:
            top_diff += 1
        if cropped_white_distances[3] < zoomed_distances[3]:
            bottom_diff -= 1
        elif cropped_white_distances[3] > zoomed_distances[3]:
            bottom_diff += 1
    return left_diff, top_diff, right_diff, bottom_diff


if __name__ == '__main__':
    with open("config.json") as f:
        config = json.load(f)

    lockscreen_image_path = config["input"]["lockscreen"]
    password_screen_image_path = config["input"]["password"]
    source_image_path = config["input"]["source"]
    source_cropped_path = config["output"]["source_cropped"]
    source_resized_path = config["output"]["source_resized"]

    lockscreen_img = Image.open(lockscreen_image_path)
    password_img = Image.open(password_screen_image_path)
    source_img = Image.open(source_image_path)

    ref_distances = find_white_pixel_distances(lockscreen_img)
    zoomed_distances = find_white_pixel_distances(password_img)

    crop_box = cut_edges_and_resize(lockscreen_img, zoomed_distances, ref_distances)
    resized_img = source_img.resize(lockscreen_img.size)
    resized_img.save(source_resized_path)
    cropped_img = resized_img.crop(crop_box)
    resized_img = cropped_img.resize(lockscreen_img.size)

    resized_img.save(source_cropped_path)
