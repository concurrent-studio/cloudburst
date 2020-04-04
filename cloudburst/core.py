#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" core functions of cloudburst """

from glob import glob

"""
query
Query a folder by filetype

arguments:
    folder      folder to query
    ext         extension to query for

returns:
    filepaths   list of filepaths matching query
"""
def query(folder, ext):
    filepaths = glob("{}/*.{}".format(folder, ext))
    return filepaths

"""
sort_tuples
Sort a list of tuples by the second element in each tuple

arguments:
    tuple_list      a list of tuples

returns:
    tuple_list      sorted list of tuples
"""
def sort_tuples(tuple_list):
    list_length = len(tuple_list)
    for i in range(0, list_length):
        for j in range(0, list_length-i-1):
            if (tuple_list[j][1] > tuple_list[j+1][1]):
                tmp = tuple_list[j]
                tuple_list[j] = tuple_list[j+1]
                tuple_list[j+1] = tmp
    return tuple_list
    