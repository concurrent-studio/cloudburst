# -*- coding: utf-8 -*-
"""
Vision
======
Manipulate, scrape, and analyze visual media

Color
-----
.. autosummary::
    :toctree: generated/

    color_delta
    get_colors

Image
-----
.. autosummary::
    :toctree: generated/

    download
    draw_points_on_image
    write_points_to_disk
    get_points_from_disk
    create_collage

Face
----
.. autosummary::
    :toctree: generated/

    crop_faces
    crop_eyes
    face_match
    get_landmarks
    get_5_landmarks
    write_landmarks_database
    average_faces
"""

from .colors import *
from .image import *
from .face import *
