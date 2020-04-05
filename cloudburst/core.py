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

__all__ = [
    'query',
    'sort_tuples'
]


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
            if (tuple_list[j][1] > tuple_list[j + 1][1]):
                tmp = tuple_list[j]
                tuple_list[j] = tuple_list[j + 1]
                tuple_list[j + 1] = tmp
    return tuple_list
