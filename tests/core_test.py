#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cloudburst core testing"""

import cloudburst as cb

def test_query():
    assert cb.query(".", "jpg") == []

def is_even(number):
    if number%2 == 0:
        return 1
    else:
        return 0

def test_concurrent():
    numbers = [0, 5, 12, 57, 8654]      
    assert sum(cb.concurrent(is_even, numbers)) == 3
