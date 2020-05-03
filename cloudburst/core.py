# -*- coding: utf-8 -*-
"""
Core Functions
==============
A variety of general, reusable functions for cloudburst

.. autosummary::
    :toctree: generated/

    concurrent
    mkdir
    query
    write_list_to_file
    get_list_from_file
    write_dict_to_file
    sort_tuples
"""

import json
import multiprocessing
from glob import glob
from pathlib import Path
from tqdm import tqdm
from tqdm.contrib.concurrent import thread_map, process_map
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

__all__ = ["concurrent", "query", "write_list_to_file", "get_list_from_file", "write_dict_to_file", "mkdir", "sort_tuples"]


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

    Return
    ------
    results : list
        list of results returned from function

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    .. code-block:: python
       import cloudburst as cb

        def is_even(number):
            if number%2 == 0:
                return True
            else:
                return False

        numbers = [0, 5, 12, 57, 8654]      
        result = cb.concurrent(is_even, numbers)
        print(result)
    """
    # https://docs.python.org/3/library/concurrent.futures.html

    # Get CPU count to use for max workers
    max_workers_count = multiprocessing.cpu_count()

    # MultiThreading
    if executor == "threadpool":
        if not progress_bar:
            results = []
            with ThreadPoolExecutor(max_workers=max_workers_count) as executor:
                futures = {executor.submit(func, i): i for i in input_list}
                for future in tqdm(as_completed(futures), total=len(futures)):
                    val = futures[future]
                    try:
                        data = future.result()
                        results.append(data)
                    except Exception as exc:
                        print("{} generated an exception: {}".format(val, exc))
            return results
        else:
            return thread_map(func, input_list, max_workers=max_workers_count, desc=desc)
    
    # MultiProcessing
    elif executor == "processpool":
        if not progress_bar:
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
            return process_map(func, input_list, max_workers=max_workers_count, desc=desc)
    
    # Invalid executor given
    else:
        raise("Error: please use executor \"processpool\" (default) or \"threadpool\"")

def query(folder, filetypes):
    """Query folder by filetype

    Parameters
    ----------
    folder : str
        the folder to search within

    filetypes : str
        extension to locate files by ("images", "videos", "audio", or custom entries)

    Return
    ------
    filepaths : list
        a list of filepaths to query matches

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    .. code-block:: python
        import cloudburst as cb
        matches = cb.query("images", "jpg")
        print(matches)
    """

    matches = []

    # pre allocated lists of types
    image_types = ["jpg", "jpeg", "png", "gif", "tif", "tiff", "webp", "bmp"]
    video_types = ["webm", "ogg", "mp4", "m4p", "m4v", "mpg", "mp2", "mpeg", "mpe", "mpv", "avi", "wmv", "mov", "qt", "flv", "swf", "avchd"]
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
    .. code-block:: python
        import cloudburst as cb

        some_numbers = [i for i in range(50)]
        cb.write_list_to_file("numbers.txt", some_numbers)
    """

    with open(filename, 'w') as f:
        for item in input_list:
            f.write('{}\n'.format(item))


def get_list_from_file(filename):
    """Get a list from a text file with each element on a new line

    Parameters
    ----------
    filename : str
        the filename that the list was be saved to

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    .. code-block:: python
        import cloudburst as cb

        some_numbers = [i for i in range(50)]
        cb.write_list_to_file("numbers.txt", some_numbers)
        print(cb.get_list_from_file("numbers.txt"))
    """

    return [line.rstrip('\n') for line in open(filename)]

def write_dict_to_file(filename, input_dict):
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
    .. code-block:: python
        import cloudburst as cb

        tesla_cars = {
            "roadster": {
                "year": 2008,
                "cost_usd": 98950
            },
            "model s": {
                "year": 2012,
                "cost_usd": 79990
            },
            "model x": {
                "year": 2016,
                "cost_usd": 84900
            },
            "model 3": {
                "year": 2017,
                "cost_usd": 39990
            },
            "model y": {
                "year": 2020,
                "cost_usd": 52990
            },
            "cybertruck": {
                "year": 2021,
                "cost_usd": 39900
            }
        }
        cb.write_dict_to_file("tesla.json", tesla_cars)
    """

    with open(filename, 'w') as f:
        f.write(json.dumps(input_dict, indent=4))

def mkdir(dirname):
    """Make a directory given a directory name (or path), ignore if directory already exists

    Parameters
    ----------
    dirname : str
        name/path of the directory to write

    Return
    ------
    path : path
        path to created directory

    Examples
    --------
    Find all images ending in ".jpg" in "./images" folder
    .. code-block:: python
        import cloudburst as cb

        cb.mkdir("test_directory")
    """

    dirpath = Path.cwd().joinpath(dirname)
    if not dirpath.exists():
        dirpath.mkdir()
    return dirpath


def sort_tuples(tuple_list, element_to_sort_by=1):
    """Sort a list of tuples by a given element (default 1 (second element))

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
    .. code-block:: python
        import cloudburst as cb
        tl = [("CONCURRENT", 5), ("STUDIO", 2), ("TEST", 8)]
        tl = cb.tuple_list(tl)
        print(tl)
    """
    
    list_length = len(tuple_list)
    for i in range(0, list_length):
        for j in range(0, list_length - i - 1):
            if tuple_list[j][element_to_sort_by] > tuple_list[j + 1][element_to_sort_by]:
                tmp = tuple_list[j]
                tuple_list[j] = tuple_list[j + 1]
                tuple_list[j + 1] = tmp
    return tuple_list
