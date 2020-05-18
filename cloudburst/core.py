# -*- coding: utf-8 -*-
"""
Core
====
A variety of general, reusable functions for cloudburst

.. autosummary::
    :toctree: generated/

    concurrent
    mkdir
    query
    write_list_to_file
    get_list_from_file
    write_dict_to_file
    get_dict_from_file
    line_coeff_from_segment
    tri_centroid
    quad_centroid
    point_in_rect
"""
import json
import multiprocessing
from glob import glob
from pathlib import Path
from tqdm.contrib.concurrent import thread_map, process_map
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

__all__ = [
    "concurrent",
    "query",
    "write_list_to_file",
    "get_list_from_file",
    "write_dict_to_file",
    "get_dict_from_file",
    "mkdir",
    "line_coeff_from_segment",
    "tri_centroid",
    "quad_centroid",
    "point_in_rect",
]


def concurrent(func, input_list, executor="threadpool", progress_bar=False, desc=""):
    """Concurrently execute a function on a list

    Parameters
    ----------
    func : function
        function to execute

    input_list : list
        list to execute function upon

    executor : string
        select between processpool (default) and threadpool
    
    progress_bar : boolean
        display progress bar to show status

    Returns
    -------
    results : list
        list of results returned from function

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    
    >>> import cloudburst as cb
    >>> def is_even(number):
    >>>     if number%2 == 0:
    >>>         return True
    >>>     else:
    >>>         return False
    >>> numbers = [0, 5, 12, 57, 8654]      
    >>> result = cb.concurrent(is_even, numbers)
    >>> print(result)
    """
    # Get CPU count to use for max workers
    max_workers_count = multiprocessing.cpu_count() - 2

    # MultiThreading
    if executor == "threadpool":
        if progress_bar == False:
            results = []
            with ThreadPoolExecutor(max_workers=max_workers_count) as executor:
                futures = {executor.submit(func, i): i for i in input_list}
                for future in as_completed(futures):
                    val = futures[future]
                    try:
                        data = future.result()
                        results.append(data)
                    except Exception as exc:
                        print("{} generated an exception: {}".format(val, exc))
            return results
        else:
            return thread_map(
                func, input_list, max_workers=max_workers_count, desc=desc
            )

    # MultiProcessing
    elif executor == "processpool":
        if progress_bar == False:
            results = []
            with ProcessPoolExecutor(max_workers=max_workers_count) as executor:
                futures = {executor.submit(func, i): i for i in input_list}
                for future in as_completed(futures):
                    val = futures[future]
                    try:
                        data = future.result()
                        results.append(data)
                    except Exception as exc:
                        print("{} generated an exception: {}".format(val, exc))
            return results
        else:
            return process_map(
                func, input_list, max_workers=max_workers_count, desc=desc
            )

    # Invalid executor given
    else:
        raise ('Error: please use executor "processpool" (default) or "threadpool"')


def query(folder, filetypes):
    """Query folder by filetype

    Parameters
    ----------
    folder : str
        the folder to search within

    filetypes : str
        extension to locate files by ("images", "videos", "audio", or custom entries)

    Returns
    -------
    filepaths : list
        a list of filepaths to query matches

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    
    >>> import cloudburst as cb
    >>> matches = cb.query("images", "jpg")
    >>> print(matches)
    """
    matches = []

    # pre allocated lists of types
    image_types = ["jpg", "jpeg", "png", "gif", "tif", "tiff", "webp", "bmp"]
    video_types = [
        "webm",
        "ogg",
        "mp4",
        "m4p",
        "m4v",
        "mpg",
        "mp2",
        "mpeg",
        "mpe",
        "mpv",
        "avi",
        "wmv",
        "mov",
        "qt",
        "flv",
        "swf",
        "avchd",
    ]
    audio_types = ["aac", "aiff", "alac", "flac", "m4a", "m4p", "mp3", "ogg", "wav"]
    if filetypes == "images":
        extensions = image_types
    elif filetypes == "videos":
        extensions = video_types
    elif filetypes == "audio":
        extensions = audio_types
    else:
        if isinstance(filetypes, list):
            extensions = filetypes
        else:
            extensions = [filetypes]

    # Search for all matches in a list of file extensions
    for ext in extensions:
        # Correct for common potential error of entering extension with dot at the beginning
        if ext.startswith("."):
            ext = ext[1:]

        matches.extend(glob("{}/*.{}".format(folder, ext)))

    return matches


def write_list_to_file(filename, input_list):
    """Write a list to a text file with each element on a new line

    Parameters
    ----------
    filename : str
        the filename that the list will be saved to

    input_list : list
        list to save

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    
    >>> import cloudburst as cb
    >>> some_numbers = [i for i in range(50)]
    >>> cb.write_list_to_file("numbers.txt", some_numbers)
    """

    with open(filename, "w") as f:
        for item in input_list:
            f.write("{}\n".format(item))


def get_list_from_file(filename):
    """Get a list from a text file with each element on a new line

    Parameters
    ----------
    filename : str
        the filename that the list was be saved to

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    
    >>> import cloudburst as cb
    >>> some_numbers = [i for i in range(50)]
    >>> cb.write_list_to_file("numbers.txt", some_numbers)
    >>> print(cb.get_list_from_file("numbers.txt"))
    """
    return [line.rstrip("\n") for line in open(filename)]


def write_dict_to_file(filename, input_dict, minimize=False):
    """Write a dictionary to a json file

    Parameters
    ----------
    filename : str
        the filename that the list will be saved to

    input_dict : dictionary
        dictionary to save

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    
    >>> import cloudburst as cb
    >>> tesla_cars = {
    >>>     "roadster": {
    >>>         "year": 2008,
    >>>         "cost_usd": 98950
    >>>     },
    >>>     "model s": {
    >>>         "year": 2012,
    >>>         "cost_usd": 79990
    >>>     },
    >>>     "model x": {
    >>>         "year": 2016,
    >>>         "cost_usd": 84900
    >>>     },
    >>>     "model 3": {
    >>>         "year": 2017,
    >>>         "cost_usd": 39990
    >>>     },
    >>>     "model y": {
    >>>         "year": 2020,
    >>>         "cost_usd": 52990
    >>>     },
    >>>     "cybertruck": {
    >>>         "year": 2021,
    >>>         "cost_usd": 39900
    >>>     }
    >>> }
    >>> cb.write_dict_to_file("tesla.json", tesla_cars)
    """
    with open(filename, "w") as f:
        if minimize:
            f.write(json.dumps(input_dict, separators=(",", ":")))
        else:
            f.write(json.dumps(input_dict, indent=4))


def get_dict_from_file(filename):
    try:
        with open(filename) as f:
            return json.load(f)
    except:
        return None


def mkdir(dirname):
    """Make a directory given a directory name (or path), ignore if directory already exists

    Parameters
    ----------
    dirname : str
        name/path of the directory to write

    Returns
    -------
    path : path
        path to created directory

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
        
    >>> import cloudburst as cb
    >>> cb.mkdir("test_directory")
    """
    dirpath = Path.cwd().joinpath(dirname)
    if not dirpath.exists():
        dirpath.mkdir()
    return dirpath


def line_coeff_from_segment(point_a, point_b):
    """Given a line segment (two points), find the slope (m) and y-intercept (b) of line y=mx+b

    Parameters
    ----------
    point_a : tuple
        coordinates of the first point
    
    point_b : tuple
        coordinates of the second point

    Returns
    -------
    m : float
        the line's slope

    b : float
        the line's y-intercept

    Examples
    --------
    Find the slope and y-intercept of a line defined by points (8, 3) and (-1, 10)

    >>> import cloudburst as cb
    >>> (m, b) = cb.line_coeff_from_segment((8, 3), (-1, 10))
    >>> print("line: y={}x+{}".format(m, b))
    """
    # slope of line
    m = (point_b[1] - point_a[1]) / (point_b[0] - point_a[0])
    # y-intercept of line
    b = point_a[1] - (m * point_a[0])

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

    Returns
    -------
    centroid : tuple
        the triangle's centroid

    Examples
    --------
    Find the centroid of the traingle formed by points (2, 4), (6, 1), (8, 10)

    >>> import cloudburst as cb
    >>> centroid = cb.tri_centroid((2, 4), (6, 1), (8, 10))
    >>> print(centroid)
    """
    # average x coords
    centroid_x = (vertex_a[0] + vertex_b[0] + vertex_c[0]) / 3
    # average y coords
    centroid_y = (vertex_a[1] + vertex_b[1] + vertex_c[1]) / 3

    return (centroid_x, centroid_y)


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

    Returns
    -------
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
    centroids = sorted(centroids, key=lambda x: x[1])
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
    centroid_x = (b2 - b1) / (m1 - m2)
    # Plug the x coordinate into the first line
    centroid_y = m1 * centroid_x + b1

    # Set centroid as tuple of two points, integers if specified
    if integer:
        centroid = (int(round(centroid_x)), int(round(centroid_y)))
    else:
        centroid = (centroid_x, centroid_y)
    return centroid


def point_in_rect(rect, point):
    ### NEEDS WORK
    """Given a rectangle and a point, check if the point is inside the rectangle

    Parameters
    ----------
    rectangle : list
        coordinates of rectangle vertices
    
    point : tuple
        coordinates of point to check 

    Returns
    -------
    within_rectangle : boolean
        whether or not the point is in the rectangle

    Examples
    --------
    Check whether or not a point exists within a rectangle 
        
    >>> import cloudburst as cb
    >>> rect = [(1, 4), (1, 8), (2, 8), (2, 4)]
    >>> print(cb.point_in_rect(rect, (1,1)))
    """
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[2]:
        return False
    elif point[1] > rect[3]:
        return False
    else:
        return True
