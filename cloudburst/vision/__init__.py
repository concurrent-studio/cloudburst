#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Vision
======
Manipulate, scrape, and analyze visual media

Image
-----
.. autosummary::
    :toctree: generated/

    download_image
    create_collage

Face
----
.. autosummary::
    :toctree: generated/

    crop_faces
    crop_eyes
    face_match
"""

from .image import (
    download_image,
    create_collage
)

from .face import (
    crop_faces,
    crop_eyes,
    face_match
)
