# -*- coding: utf-8 -*-
from numpy import sqrt
from colorthief import ColorThief
from PIL import Image

__all__ = ["color_delta", "get_colors"]


def color_delta(color1, color2):
    """Percentage difference between two colors

    Parameters
    ----------
    color1 : tuple
        color in the format of (r, g, b)

    color2 : str
        color in the format of (r, g, b)

    Return
    ------
    difference : float
        the percent difference between the two colors
        None if input value out of range

    Examples
    --------
    Find the difference between (223, 42, 5) and (47, 156, 89)

    >>> from cloudburst import vision as cbv
    >>> difference = cbv.color_delta((223, 42, 5), (47, 156, 89))
    >>> print(difference)
    """
    r1, g1, b1 = color1
    r2, g2, b2 = color2
    if all(0 <= i <= 255 for i in [r1, g1, b1, r2, g2, b2]):
        distance = sqrt((r2 - r1) ** 2 + (g2 - g1) ** 2 + (b2 - b1) ** 2)
        max_distance = sqrt(195075)

        return distance / max_distance
    else:
        print(
            "Error: colors must be entered in RGB values with each value being on the interval [0,255]"
        )

        return None


def get_colors(image_path, color_count=1, exclude_color=None, exclude_range=0.0):
    """Get predominant color(s) in a given image

    Parameters
    ----------
    image_path : string
        path to image to query

    color_count : int
        number of colors to return
    
    exclude_color : tuple
        color to exclude from search

    exclude_range : float
        percentage variance from exclude_color to block

    Return
    ------
    colors : list
        a list of predominant color(s) in image

    Examples
    --------
    Find the predominant colors in "./test.jpg"
        
    >>> from cloudburst import vision as cbv
    >>> colorlist = cbv.get_colors("./test.jpg", 2)
    >>> print(colorlist)
    """
    if color_count == 1:
        image = Image.open(image_path)
        w, h = image.size
        all_colors = image.getcolors(w * h)

        top_color = all_colors[0]
        for count, color in all_colors:
            if exclude_color is not None:
                if (
                    count > top_color[0]
                    and color_delta(color, exclude_color) < exclude_range
                ):
                    top_color = (count, color)
            else:
                if count > top_color[0]:
                    top_color = (count, color)

        return top_color[1]

    else:
        return ColorThief(image_path).get_palette(color_count=color_count)
