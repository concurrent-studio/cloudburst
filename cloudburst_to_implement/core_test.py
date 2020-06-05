#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""cloudburst core testing"""

import cloudburst as cb


# def test_query():
#     assert cb.query(".", "jpg") == []

def is_even(number):
    if number%2 == 0:
        return True
    else:
        return False

numbers = [0, 5, 12, 57, 8654]      
result = cb.concurrent(is_even, numbers)
print(result)

result = cb.concurrent(is_even, numbers, progress_bar=True)
print(result)