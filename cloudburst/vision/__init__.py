# -*- coding: utf-8 -*-
from .color import *
from .face import *
from .face3d import *
from .io import *
from .transform import *

"""
Vision
======
A collection of functions related to computer vision

Color
-----
.. autosummary::
    :toctree: generated/

    color_delta
    get_colors

Face
----
Image transformations and manipulations

.. autosummary::
    :toctree: generated/

    get_faces
    get_eyes
    get_landmarks
    average_faces

Face3D
------
.. autosummary::
    :toctree: generated/

    face_to_3d

I/O
---
Image retrieval and reading from / writing to disk

.. autosummary::
    :toctree: generated/

    download
    write_points_to_disk
    get_points_from_disk
    load_png

Transform
---------
Image transformations and manipulations

.. autosummary::
    :toctree: generated/

    draw_points_on_image
    draw_rect_on_image
    create_collage
"""
