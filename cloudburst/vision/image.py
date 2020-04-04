#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" image generation module for cloudburst """

import requests
from PIL import Image
from datetime import datetime
from cloudburst import sort_tuples

"""
download_image
Download an image from a url

arguments:
    url         image to a url
    filename    filename to save image to
"""
def download_image(url, filename):
    with open(filename, "wb") as f:
        f.write(requests.get(url).content)

"""
create_collage
Create a collage from a list of images

arguments:
    width       width of each collage
    height      height of each collage
    min_size    minimum size of images on canvas
    image_list  list of images for canvas

optional arguments:
    func        custom function to operate on each image
    blank_color color for blank image
"""
def create_collage(width, height, min_size, image_list, func=None, blank_color=(255, 255, 255)):
    image_count = len(image_list)

    min_dimension = width if width < height else height
    squares = []
    for s in range(min_size, min_dimension):
        if width%s == height%s == 0:
            squares.append(s)
          
    sizes = []
    for size in get_squares(width, height):
        images_per_collage = int((width*height)/(size*size))
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
        print("Create collage {} of {}".format(c+1, collage_count))
        timestamp = int(datetime.utcnow().timestamp())
        count_scale_value = c*ideal_size[2]
        collage = Image.new('RGB', (width, height))
        x = 0
        y = 0

        for image_path in image_list[count_scale_value:count_scale_value+ideal_size[2]]:
            if not func:
                if func(image_path):
                    image = Image.open(image_path)
                    image = image.resize((ideal_size[0], ideal_size[0]))
                else:
                    image = Image.new('RGB', (ideal_size[0], ideal_size[0]), blank_color)
            else:
                image = Image.open(image_path)
                image = image.resize((ideal_size[0], ideal_size[0]))

            collage.paste(image, (x, y))

            if x < width-ideal_size[0]:
                x += ideal_size[0]
            else:
                x = 0
                y += ideal_size[0]

        collage.save("collage_{}.jpg".format(timestamp))
    print("{} images unused".format(ideal_size[2]))

