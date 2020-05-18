# -*- coding: utf-8 -*-
import cv2
import requests
from cloudburst import get_list_from_file, write_list_to_file

__all__ = ["download", "write_points_to_disk", "get_points_from_disk", "load_png"]

# https://developer.here.com/blog/getting-started-with-geocoding-exif-image-metadata-in-python3
# this one's good •.•
# https://pypi.org/project/piexif/

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

    >>> from cloudburst import vision as cbv
    >>> url = 'https://s3.amazonaws.com/thebrilliance/posts/images/000/001/136/square/LV_BRILL.jpg?1529759316'
    >>> cbv.download(url, 'brilliance.jpg')
    """
    with open(filename, "wb") as f:
        try:
            f.write(requests.get(url).content)
        except Exception as e:
            print(
                f"\033[31mError occured during download of content at \033[4m{url}\033[31m\n{e}\033[0m"
            )


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

    >>> from cloudburst import vision as cbv
    >>> landmarks = cbv.get_landmarks("bella-hadid.jpg")
    >>> cbv.write_points_to_disk("bella-hadid.txt", landmarks)
    """
    point_list = ["{}\t{}".format(int(x), int(y)) for x, y in input_list]
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
    
    >>> from cloudburst import vision as cbv
    >>> landmarks = cbv.get_landmarks("bella-hadid.jpg")
    >>> cbv.write_points_to_disk("bella-hadid.txt", landmarks)
    >>> landmarks_from_disk = cbv.get_points_from_disk("bella-hadid.txt")
    >>> print(landmarks_from_disk)
    """
    input_list = get_list_from_file(filename)
    split_list = [i.split("\t") for i in input_list]
    return [(int(float(x)), int(float(y))) for x, y in split_list]


def load_png(image_path, alpha_color=(255, 255, 255)):
    """Load a png file into PIL Image

    Parameters
    ----------
    image_path : str
        path to image file
    alpha_color : tuple
        RGB Color to replace alpha channel with

    Examples
    --------
    Load test.jpg with white as alpha channel color
    
    >>> from cloudburst import vision as cbv
    >>> im = cbv.load_png("test.jpg")
    >>> im.show()
    """
    png = Image.open(image_path)
    png.load()
    image = Image.new("RGB", png.size, (255, 255, 255))
    image.paste(png, mask=png.split()[3])

    return image
