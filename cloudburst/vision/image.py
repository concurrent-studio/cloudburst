# -*- coding: utf-8 -*-
""" image generation module for cloudburst """

import cv2
import requests
from pathlib import Path
from PIL import Image
from datetime import datetime
from cloudburst.core import sort_tuples, get_list_from_file, write_list_to_file

__all__ = ["download", "draw_points_on_image", "write_points_to_disk", "get_points_from_disk", "create_collage"]


def download(url, filename):
    """Download an image or video from a URL

    Parameters
    ----------
    url : str
        URL to image
    filename : str
        filename to save image to

    Examples
    --------
    Download an image from www.thebrilliance.com and save as 'brilliance.jpg'

    .. code-block:: python

        from cloudburst import vision as cbv

        url = 'https://s3.amazonaws.com/thebrilliance/posts/images/000/001/136/square/LV_BRILL.jpg?1529759316'
        cbv.download(url, 'brilliance.jpg')
    """
    with open(filename, "wb") as f:
        try:
            f.write(requests.get(url).content)
        except:
            pass

def draw_points_on_image(image_path, point_list, radius=2, color=(255, 0, 0)):
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
    img = cv2.imread(image_path, 1)

    for x, y in point_list:
        cv2.circle(img, (int(x), int(y)), radius, color, -1)

    cv2.imshow(Path(image_path).name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def write_points_to_disk(filename, input_list):
    """Write a list of points in form (x, y) to disk

    Parameters
    ----------
    filename : str
        filename to save list to
    input_list : list
        list of points to save

    Examples
    --------
    Calculate facial landmarks on an image and write to disk

    .. code-block:: python

        from cloudburst import vision as cbv

        landmarks = cbv.get_landmarks("bella-hadid.jpg")
        cbv.write_points_to_disk("bella-hadid.txt", landmarks)
    """
    print([i for i in input_list])
    point_list = ["{}\t{}".format(x, y) for x, y in input_list]
    write_list_to_file(filename, point_list)

def get_points_from_disk(filename):
    """Get a list of points in form (x, y) from saved  file

    Parameters
    ----------
    filename : str
        filename to save list to
    input_list : list
        list of points to save

    Examples
    --------
    Calculate facial landmarks on an image and write to disk, then load it back into another list

    .. code-block:: python
    
        from cloudburst import vision as cbv

        landmarks = cbv.get_landmarks("bella-hadid.jpg")
        cbv.write_points_to_disk("bella-hadid.txt", landmarks)
        landmarks_from_disk = cbv.get_points_from_disk("bella-hadid.txt)
        print(landmarks_from_disk)
    """
    input_list = get_list_from_file(filename)
    split_list = [i.split("\t") for i in input_list]
    return [(int(float(x)), int(float(y))) for x, y in split_list]

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

        import cloudburst as cb
        from cloudburst import vision as cbv

        image_paths = cb.query('images', 'jpg')
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

    ideal_size = sort_tuples(sizes)[0]

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
