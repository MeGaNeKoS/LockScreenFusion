import json
from PIL import Image


def create_reference_image(width, height):
    ref_img = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    border_size = int(width * 0.05)
    checker_size = 1

    for y in range(height):
        for x in range(width):
            if x < border_size or x >= width - border_size or y < border_size or y >= height - border_size:
                if (x // checker_size) % 2 == (y // checker_size) % 2:
                    ref_img.putpixel((x, y), (255, 0, 0, 255))
                else:
                    ref_img.putpixel((x, y), (0, 255, 255, 255))

    return ref_img


if __name__ == "__main__":
    with open("config.json") as f:
        config = json.load(f)

    source_image_path = config["input"]["source"]
    output_path = config["output"]["pattern"]

    source_image = Image.open(source_image_path)

    reference_image = create_reference_image(*source_image.size)
    reference_image.save(output_path)
