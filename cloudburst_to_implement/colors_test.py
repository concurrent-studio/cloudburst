# -*- coding: utf-8 -*-
from cloudburst import vision as cbv

# Test get colors
colorlist = cbv.get_colors("test.jpg", 1)
print(colorlist)

# Test color delta on accurate values
difference = cbv.color_delta((223, 42, 5), (47, 156, 89))
print(difference)

# Test color delta on inaccurate values
difference = cbv.color_delta((223, 2138, 5), (47, 156, 89))