# Lock Screen Wallpaper Generator

This project generates a custom wallpaper for your lock screen that matches the appearance of your password screen. It consists of four Python scripts and a configuration file.

## Prerequisites

- Python 3 or higher
- Pillow library

Install the required library using:

```sh
pip install pillow
```

## Usage
1. Replace the images in the input folder with your own images. Make sure to name them correctly:
   * `source/original.jpg`: The source image you want to use as a wallpaper.
   * `lockscreen/lockscreen.png`: A screenshot of your lock screen without the password prompt.
   * `lockscreen/password.png`: A screenshot of your lock screen with the password prompt visible.

2. Run the following scripts in order:
   * Generate the calibration pattern
      ```sh
      python generate_pattern.py
      ```
     1. Replace your lock screen wallpaper with the generated image. Default location: `backgrounds/background_pattern.jpg`
     2. Replace your profile picture with the black image. Default location: `backgrounds/black.jpg`
     3. Take a screenshot of your lock screen. The plain and with password prompt. Save them as `lockscreen/lockscreen.png` and `lockscreen/password.png` respectively.
        * To take screenshots, you can use snipping tool on `Windows`. Set it as `Rectagle mode` then add some delay.
        * Then click new and lock your screen.
   * Calculate the difference between the lock screen and the password prompt
      If your windows doesn't have Zoom effect, you can skip this step.
      ```sh
      python diff.py
      ```
     This will calculate the difference between the lock screen and the password prompt.
   * Generate the profile image
      ```sh
      python generate_profile.py
      ```
     Let the magic happen. This will generate the profile image.

3. The generated profile will be saved in `result/result.jpg`. Apply this image as your lock screen wallpaper.
4. During the process, there are additional images created :
    * `backgrounds/pattern_lock_screen.png`: A patterned image that mimics the border design of the lock screen.
    * `source/cropped.jpg`: The cropped source image.
    * `source/resized.jpg`: The resized source image.
## Configuration
You can customize the input and output paths of your project in the config.json file. Modify the paths as needed.
```JSON
{
  "input": {
    "source": "source/original.jpg",
    "lockscreen": "lockscreen/lockscreen.png",
    "password": "lockscreen/password.png"
  },
  "output": {
    "pattern": "backgrounds/pattern_lock_screen.png",
    "result": "result/result.jpg",
    "source_cropped": "source/cropped.jpg",
    "source_resized": "source/resized.jpg"
  }
}
```
## How it works
1. `generate_pattern.py`: This script creates a reference pattern image based on the source image dimensions. 
2. `diff.py`: This script finds the differences between the lock screen and password screen images and resizes the source image accordingly. 
3. `generate_profile.py`: This script creates a mask from the lock screen password image and applies it to the resized source image to generate the final wallpaper.

## License
This project is licensed under the MIT License. See the `LICENSE` file for more information.