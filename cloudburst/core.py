#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Core Functions
==============
A variety of general, reusable functions for cloudburst

.. autosummary::
    :toctree: generated/

    query
    sort_tuples
"""

from glob import glob
from urllib.parse import urlparse, parse_qs

__all__ = ["query", "query_decode", "sort_tuples", "line_coeff_from_segment", "tri_centroid", "quad_centroid"]


def query(folder, ext):
    """Query folder by filetype

    Parameters
    ----------
    folder : str
        the folder to search within

    ext : str
        extension to locate files by

    Return
    ------
    filepaths : list
        a list of filepaths to query matches

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    >>> import cloudburst as cb
    >>> matches = cb.query("images", "jpg")
    >>> print(matches)
    """
    filepaths = glob("{}/*.{}".format(folder, ext))
    return filepaths

def query_decode(url):
    """Given a URL, return its decoded query info

    Parameters
    ----------
    url : str
        the url to decode

    Return
    ------
    query : dict
        json of query

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    >>> import cloudburst as cb
    >>> result = cb.query_decode("https://www.instagram.com/graphql/query/?query_hash=04334405dbdef91f2c4e207b84c204d7&variables=%7B%22only_stories%22%3Atrue%2C%22stories_prefetch%22%3Atrue%2C%22stories_video_dash_manifest%22%3Afalse%7D")
    >>> print(result)
    """
    result = parse_qs(urlparse(url)[4])
    return result


def sort_tuples(tuple_list):
    """Sort a list of tuples by their second elements

    Parameters
    ----------
    tuple_list : list
        an unsorted list of tuples

    Return
    ------
    tuple_list : list
        a list of tuples sorted by their 2nd term

    Examples
    --------
    Sort a list of (key, value) by their values
    >>> import cloudburst as cb
    >>> tl = [("CONCURRENT", 5), ("STUDIO", 2), ("TEST", 8)]
    >>> tl = cb.tuple_list(tl)
    >>> print(tl)
    """
    list_length = len(tuple_list)
    for i in range(0, list_length):
        for j in range(0, list_length - i - 1):
            if tuple_list[j][1] > tuple_list[j + 1][1]:
                tmp = tuple_list[j]
                tuple_list[j] = tuple_list[j + 1]
                tuple_list[j + 1] = tmp
    return tuple_list

def line_coeff_from_segment(point_a, point_b):
    """Given a line segment (two points), find the slope (m) and y-intercept (b) of line y=mx+b

    Parameters
    ----------
    point_a : tuple
        coordinates of the first point
    
    point_b : tuple
        coordinates of the second point

    Return
    ------
    m : float
        the line's slope

    b : float
        the line's y-intercept

    Examples
    --------
    Find the 
    >>> import cloudburst as cb
    >>> (m, b) = cb.line_coeff_from_segment((8, 3), (-1, 10))
    >>> print("line: y={}x+{}".format(m, b))
    """
    m = (point_b[1] - point_a[1])/(point_b[0] - point_a[0])
    b = point_a[1] - (m*point_a[0])

    return m, b

def tri_centroid(vertex_a, vertex_b, vertex_c):
    """Find the centroid of any triangle given its vertices

    Parameters
    ----------
    vertex_a : tuple
        coordinates of the first vertex
    
    vertex_b : tuple
        coordinates of the second vertex
    
    vertex_c : tuple
        coordinates of the third vertex

    Return
    ------
    centroid : tuple
        the triangle's centroid

    Examples
    --------
    Find the centroid of the traingle formed by points (2, 4), (6, 1), (8, 10)
    >>> import cloudburst as cb
    >>> centroid = cb.tri_centroid((2, 4), (6, 1), (8, 10))
    >>> print(centroid)
    """
    centroid_x = (vertex_a[0] + vertex_b[0] + vertex_c[0])/3
    centroid_y = (vertex_a[1] + vertex_b[1] + vertex_c[1])/3
    centroid = (centroid_x, centroid_y)
    return centroid

def quad_centroid(vertex_a, vertex_b, vertex_c, vertex_d, integer=False):
    """Find the centroid of any quadrilateral given its vertices

    Parameters
    ----------
    vertex_a : tuple
        coordinates of the first vertex
    
    vertex_b : tuple
        coordinates of the second vertex
    
    vertex_c : tuple
        coordinates of the third vertex
    
    vertex_d : tuple
        coordinates of the fourth vertex

    Return
    ------
    centroid : tuple
        the quadrilateral's centroid

    Examples
    --------
    Find the centroid of the quadrilateral formed by vertices (1, 0), (2, 8), (9, -1), (10, 2)
    >>> import cloudburst as cb
    >>> centroid = cb.quad_centroid((1, 0), (2, 8), (9, -1), (10, 2))
    >>> print(centroid)
    """
    # Break quadrilateral into component triangles
    triangles = []
    triangle_a = (vertex_a, vertex_b, vertex_c)
    triangle_b = (vertex_a, vertex_d, vertex_c)
    triangle_c = (vertex_a, vertex_d, vertex_b)
    triangle_d = (vertex_b, vertex_d, vertex_c)
    triangles.extend((triangle_a, triangle_b, triangle_c, triangle_d))

    # Calculate centroids of triangles
    centroids = []
    for triangle in triangles:
        centroids.append(tri_centroid(triangle[0], triangle[1], triangle[2]))
    # Sort centroids by y value to ensure correct calculation
    centroids = sort_tuples(centroids)
    # Ensure that vertex a has a lower x value than vertex b
    if centroids[0][0] > centroids[1][0]:
        centroids = [centroids[1], centroids[0], centroids[2], centroids[3]]
    
    # Ensure that vertex d has a lower x value than vertex c
    if centroids[3][0] > centroids[2][0]:
        centroids = [centroids[0], centroids[1], centroids[3], centroids[2]]

    # Equation of line running between abc's centroid and adc's centroid
    (m1, b1) = line_coeff_from_segment(centroids[0], centroids[2])
    # Equation of line running between adb's centroid and bdc's centroid
    (m2, b2) = line_coeff_from_segment(centroids[1], centroids[3])

    # Calculate centroid x coordinate by setting the two lines equal to each other
    centroid_x = (b2 - b1)/(m1 - m2)
    # Plug the x coordinate into the first line
    centroid_y = m1 * centroid_x + b1

    # Set centroid as tuple of two points, integers if specified
    if integer:
        centroid = (int(round(centroid_x)), int(round(centroid_y)))
    else:
        centroid = (centroid_x, centroid_y)
    return centroid