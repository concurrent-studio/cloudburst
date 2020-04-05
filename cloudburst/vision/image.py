#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" image generation module for cloudburst """

import requests
from PIL import Image
from datetime import datetime
from cloudburst import sort_tuples

__all__ = [
    'download_image',
    'create_collage'
]


def download_image(url, filename):
    """Download an image from a URL

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

       cbv.download_image(url, 'brilliance.jpg')
    """
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)


def create_collage(
    width,
    height,
    min_size,
    image_list,
    func=None,
    blank_color=(
        255,
        255,
        255)):
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
            sizes.append(
                (size,
                 unused_image_count,
                 images_per_collage,
                 collage_count))

    ideal_size = sort_tuples(sizes)[0]

    collage_count = ideal_size[3]
    for c in range(collage_count):
        print("Create collage {} of {}".format(c + 1, collage_count))
        timestamp = int(datetime.utcnow().timestamp())
        count_scale_value = c * ideal_size[2]
        collage = Image.new('RGB', (width, height))
        x = 0
        y = 0

        for image_path in image_list[count_scale_value:
                                     count_scale_value + ideal_size[2]]:
            if not func:
                if func(image_path):
                    image = Image.open(image_path)
                    image = image.resize((ideal_size[0], ideal_size[0]))
                else:
                    image = Image.new(
                        'RGB', (ideal_size[0], ideal_size[0]), blank_color)
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
