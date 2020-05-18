# -*- coding: utf-8 -*-
import cv2
from pathlib import Path
from PIL import Image, ImageDraw
from datetime import datetime

__all__ = ["draw_points_on_image", "draw_rect_on_image", "create_collage"]


def draw_points_on_image(image, point_list, radius=1, color=(0, 0, 255)):
    """Draw points on an image

    Parameters
    ----------
    image_path : str
        path to image
    point_list : list
        list of points in form (x, y) to draw on image
    radius : int
        radius of points to draw in pixels
    color : tuple
        color of points to draw

    Examples
    --------
    Calculate facial landmarks of an image and draw them on the imate

    .. code-block:: python

        from cloudburst import vision as cbv

        landmarks = cbv.get_landmarks("bella-hadid.jpg")
        cbv.draw_points_on_image("bella-hadid.jpg", landmarks)
    """
    draw = ImageDraw.Draw(image)

    for x, y in point_list:
        draw.ellipse(
            (int(x - radius), int(y - radius), int(x + radius), int(y + radius)),
            fill=color,
        )

    return image


def draw_rect_on_image(image, xy, radius=1, color=(255, 0, 0)):
    """Draw points on an image

    Parameters
    ----------
    image_path : str
        path to image
    point_list : list
        list of points in form (x, y) to draw on image
    radius : int
        radius of points to draw in pixels
    color : tuple
        color of points to draw

    Examples
    --------
    Calculate facial landmarks of an image and draw them on the imate

    .. code-block:: python

        from cloudburst import vision as cbv

        landmarks = cbv.get_landmarks("bella-hadid.jpg")
        cbv.draw_points_on_image("bella-hadid.jpg", landmarks)
    """
    draw = ImageDraw.Draw(image)
    draw.rectangle(xy, fill=None, outline=color, width=1)
    return image


def create_collage(
    width, height, min_size, image_list, func=None, blank_color=(255, 255, 255)
):
    """Create a collage from a list of images

    Parameters
    ----------
    width : int
        width of collage
    height : int
        height of collage
    min_size : int
        minimum allowable size of grid image
    image_list : list
        list of images for collage
    func : function, optional
        custom function to operate on each image
    blank_color : tuple, optional
        color for blank image

    Examples
    --------
    Create collage of dimensions (1920, 1080) of images from './images' directory

    .. code-block:: python

        from cloudburst import vision as cbv
        import cloudburst as cb

        image_paths = cb.query("test_dir", "images")
        cbv.create_collage(1920, 1080, 10, image_paths)
    """
    image_count = len(image_list)

    min_dimension = width if width < height else height
    squares = []
    for s in range(min_size, min_dimension):
        if width % s == height % s == 0:
            squares.append(s)

    sizes = []
    for size in get_squares(width, height):
        images_per_collage = int((width * height) / (size * size))
        if image_count > images_per_collage:
            unused_image_count = image_count
            collage_count = 0
            while unused_image_count > images_per_collage:
                unused_image_count -= images_per_collage
                collage_count += 1
            sizes.append((size, unused_image_count, images_per_collage, collage_count))

    ideal_size = sorted(sizes, key=lambda x: x[1])[0]

    collage_count = ideal_size[3]
    for c in range(collage_count):
        print("Create collage {} of {}".format(c + 1, collage_count))
        timestamp = int(datetime.utcnow().timestamp())
        count_scale_value = c * ideal_size[2]
        collage = Image.new("RGB", (width, height))
        x = 0
        y = 0

        for image_path in image_list[
            count_scale_value : count_scale_value + ideal_size[2]
        ]:
            if not func:
                if func(image_path):
                    image = Image.open(image_path)
                    image = image.resize((ideal_size[0], ideal_size[0]))
                else:
                    image = Image.new(
                        "RGB", (ideal_size[0], ideal_size[0]), blank_color
                    )
            else:
                image = Image.open(image_path)
                image = image.resize((ideal_size[0], ideal_size[0]))

            collage.paste(image, (x, y))

            if x < width - ideal_size[0]:
                x += ideal_size[0]
            else:
                x = 0
                y += ideal_size[0]

        collage.save("collage_{}.jpg".format(timestamp))
    print("{} images unused".format(ideal_size[2]))
