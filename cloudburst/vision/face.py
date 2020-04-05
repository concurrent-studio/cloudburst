#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Facial feature detection and analysis"""

import os
import cv2
import face_recognition
import numpy as np
from PIL import Image

__all__ = [
    'crop_faces',
    'crop_eyes',
    'face_match'
]

this_folder = os.path.abspath(os.path.dirname(__file__))


def get_eyes_from_image(image_path):
    """Get all eyes within an image

    Parameters
    ----------
    image_path : str
        filepath to an image file

    Returns
    -------
    eyes : list
        list of images of eyes in the given image
    """
    face_cascade = cv2.CascadeClassifier(
        "{}/haarcascade_frontalface_default.xml".format(this_folder))
    eyes_cascade = cv2.CascadeClassifier(
        "{}/haarcascade_eye.xml".format(this_folder))
    eyes = []

    image = cv2.imread(image_path)
    faces_detected = face_cascade.detectMultiScale(
        image, scaleFactor=1.1, minNeighbors=5)

    for (x, y, w, h) in faces_detected:
        i = eyes_cascade.detectMultiScale(image[y:y + h, x:x + w])
        eye_angle = np.degrees(
            np.arctan((i[1][1] - i[0][1]) / (i[1][0] - i[0][0])))

        rows, cols = image.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), eye_angle, 1)
        image_rotated = cv2.warpAffine(image, M, (cols, rows))

        i = eyes_cascade.detectMultiScale(image_rotated[y:y + h, x:x + w])
        for (ex, ey, ew, eh) in i:
            eyes.append(image_rotated[y + ey:y + ey + eh, x + ex:x + ex + ew])

    return eyes


def crop_eyes(image_path):
    """Crop and save all eyes within a given image

    Parameters
    ----------
    image_path : str
        path (or list of paths) to an image(s)

    Examples
    --------
    Get and crop the eyes of all images in './images' folder

    .. code-block:: python

       import cloudburst as cb
       from cloudburst import vision as cbv

       paths = cb.query('images', 'jpg')
       cbv.crop_eyes(paths)
    """
    if isinstance(image_path, list):
        for path in image_path:
            eyes = get_eyes_from_image(path)
            for idx, eye in enumerate(eyes):
                filename = "{}_eye_{}.jpg".format(
                    path.split("/")[-1].split(".")[-2], idx)
                cv2.imwrite(filename, eye)
    else:
        faces = get_eyes_from_image(image_path)
        for idx, eye in enumerate(eyes):
            filename = "{}_eye_{}.jpg".format(
                path.split("/")[-1].split(".")[-2], idx)
            cv2.imwrite(filename, eye)


def get_faces_from_image(image_path):
    """Get all faces within an image

    Parameters
    ----------
    image_path : str
        filepath to an image file

    Returns
    -------
    faces : list
        list of images of faces in the given image
    """
    faces = []

    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)

    for face_location in face_locations:
        top, right, bottom, left = face_location
        face_image = image[top:bottom, left:right]
        faces.append(Image.fromarray(face_image))

    return faces


def crop_faces(image_path):
    """Crop and save all faces within a given image

    Parameters
    ----------
    image_path : str
        path (or list of paths) to an image(s)

    Examples
    --------
    Get and crop the faces of all images in './images' folder

    .. code-block:: python

       import cloudburst as cb
       from cloudburst import vision as cbv

       paths = cb.query('images', 'jpg')
       cbv.crop_faces(paths)
    """
    if isinstance(image_path, list):
        for path in image_path:
            faces = get_faces_from_image(path)
            for idx, face in enumerate(faces):
                filename = "{}_face_{}.jpg".format(
                    path.split("/")[-1].split(".")[-2], idx)
                face.save(filename)
    else:
        faces = get_faces_from_image(image_path)
        for idx, face in enumerate(faces):
            filename = "{}_face_{}.jpg".format(
                path.split("/")[-1].split(".")[-2], idx)
            face.save(filename)


"""
face_match
Facial recognition matching

arguments:
    known_image_path        path to image of known identity
    unknown_image_path      path(s) to unknown images

returns:
    results                 list of results (True/False)
"""


def face_match(known_image_path, unknown_image_path):
    """Find matched faces in an image or list of images

    Parameters
    ----------
    known_image_path : str
        filepath to image of known identity

    unknown_image_path : str
        path(s) to unknown images

    Returns
    -------
    results : list
        list of match results (True/False)

    Examples
    --------
    Compare faces of all images in './images' folder to face of './obama.jpg'

    .. code-block:: python

       import cloudburst as cb
       from cloudburst import vision as cbv

       known = './obama.jpg'
       paths = cb.query('images', 'jpg')
       results = cbv.face_match(known, paths)
       print(results)
    """
    known_image = face_recognition.load_image_file(known_image_path)
    known_encoding = face_recognition.face_encodings(known_image)[0]

    results = []
    if isinstance(unknown_image_path, list):
        for image_path in unknown_image_path:
            unknown_image = face_recognition.load_image_file(image_path)
            unknown_encoding = face_recognition.face_encodings(unknown_image)[
                0]
            results.append(
                face_recognition.compare_faces(
                    [known_encoding],
                    unknown_encoding)[0])
    else:
        unknown_image = face_recognition.load_image_file(image_path)
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results.append(
            face_recognition.compare_faces(
                [known_encoding],
                unknown_encoding)[0])

    return results
