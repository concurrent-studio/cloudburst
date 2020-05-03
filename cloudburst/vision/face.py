# -*- coding: utf-8 -*-
"""Facial feature detection and analysis"""

import os
import cv2
import dlib
import numpy as np
import face_recognition
import face_recognition_models
from PIL import Image
from imutils import face_utils
from cloudburst.core import concurrent, query
from cloudburst.math import point_in_rect
from cloudburst.vision import get_points_from_disk, write_points_to_disk

__all__ = ["crop_faces", "crop_eyes", "face_match", "get_landmarks", "get_5_landmarks", "write_landmarks_database", "average_faces"]

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
        "{}/models/haarcascade_frontalface_default.xml".format(this_folder)
    )
    eyes_cascade = cv2.CascadeClassifier("{}/models/haarcascade_eye.xml".format(this_folder))
    eyes = []

    image = cv2.imread(image_path)
    faces_detected = face_cascade.detectMultiScale(
        image, scaleFactor=1.1, minNeighbors=5
    )

    for (x, y, w, h) in faces_detected:
        i = eyes_cascade.detectMultiScale(image[y : y + h, x : x + w])
        eye_angle = np.degrees(np.arctan((i[1][1] - i[0][1]) / (i[1][0] - i[0][0])))

        rows, cols = image.shape[:2]
        M = cv2.getRotationMatrix2D((cols / 2, rows / 2), eye_angle, 1)
        image_rotated = cv2.warpAffine(image, M, (cols, rows))

        i = eyes_cascade.detectMultiScale(image_rotated[y : y + h, x : x + w])
        for (ex, ey, ew, eh) in i:
            eyes.append(image_rotated[y + ey : y + ey + eh, x + ex : x + ex + ew])

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
                    path.split("/")[-1].split(".")[-2], idx
                )
                cv2.imwrite(filename, eye)
    else:
        faces = get_eyes_from_image(image_path)
        for idx, eye in enumerate(eyes):
            filename = "{}_eye_{}.jpg".format(path.split("/")[-1].split(".")[-2], idx)
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
                    path.split("/")[-1].split(".")[-2], idx
                )
                face.save(filename)
    else:
        faces = get_faces_from_image(image_path)
        for idx, face in enumerate(faces):
            filename = "{}_face_{}.jpg".format(image_path.split("/")[-1].split(".")[-2], idx)
            face.save(filename)
    return True


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
            unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
            results.append(
                face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
            )
    else:
        unknown_image = face_recognition.load_image_file(image_path)
        unknown_encoding = face_recognition.face_encodings(unknown_image)[0]
        results.append(
            face_recognition.compare_faces([known_encoding], unknown_encoding)[0]
        )

    return results

# fix the fucking docs
def get_5_landmarks(image_path):
    """Get coordinates 5 facial landmarks from a given image

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
       for image_path in paths:
        cbv.get_5_landmarks(image_path)
    """
     
    # Configure detector
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_five_point_model_location())

    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    landmarks = []

    # Find landmarks on all given faces
    for (i, rect) in enumerate(detector(image_grayscale, 0)):
        # Make the prediction, tranferring it to numpy array
        shape = face_utils.shape_to_np(predictor(image_grayscale, rect))

        for landmark in shape:
            landmarks.append((float(landmark[0]), float(landmark[1])))

    return landmarks

# fix the fucking docs
def get_landmarks(image_path):
    """Get coordinates of 68 facial landmarks from a given image

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
       for image_path in paths:
        cbv.get_landmarks(image_path)
    """
    # Configure detector
    detector = dlib.get_frontal_face_detector()
    predictor = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())

    # Load image and convert to grayscale
    image = cv2.imread(image_path)
    image_grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
    landmarks = []

    # Find landmarks on all given faces
    for (i, rect) in enumerate(detector(image_grayscale, 0)):
        # Make the prediction, tranferring it to numpy array
        shape = face_utils.shape_to_np(predictor(image_grayscale, rect))

        for landmark in shape:
            landmarks.append((float(landmark[0]), float(landmark[1])))

    return landmarks

def write_landmarks_database(folder, delete_errors=False):
    """Go through all images in a folder and create text files with their 68 facial feature points

    Parameters
    ----------
    folder : str
        path (or list of paths) to an image(s)
    delete_errors : boolean
        if True, delete all images who fail to register landmarks

    Examples
    --------
    Get and crop the faces of all images in './images' folder

    .. code-block:: python

       import cloudburst as cb
       from cloudburst import vision as cbv

       paths = cb.query('images', 'jpg')
       cbv.crop_faces(paths)
    """
    def w2d(image_path):
        landmarks = get_landmarks(image_path)
        if landmarks != []:
            write_points_to_disk("{}.txt".format(image_path[:-1]), landmarks)
        else:
            if delete_errors:
                os.remove(image_path)

    concurrent(w2d, query(folder, "images"), executor="threadpool", progress_bar=True)

def write_5_landmarks_database(folder, delete_errors=False):
    """Go through all images in a folder and create text files with their 5 facial feature points

    Parameters
    ----------
    folder : str
        path (or list of paths) to an image(s)
    delete_errors : boolean
        if True, delete all images who fail to register landmarks

    Examples
    --------
    Get and crop the faces of all images in './images' folder

    .. code-block:: python

       import cloudburst as cb
       from cloudburst import vision as cbv

       paths = cb.query('images', 'jpg')
       cbv.crop_faces(paths)
    """
    def w2d(image_path):
        landmarks = get_5_landmarks(image_path)
        if landmarks != []:
            write_points_to_disk("{}.txt".format(image_path[:-1]), landmarks)
        else:
            if delete_errors:
                os.remove(image_path)

    concurrent(w2d, query(folder, "images"), executor="threadpool", progress_bar=True)

########################### AVERAGE FACES ###########################
"""THIS NEEDS TO BE CLEANED UP BIG TIME"""
# Read points from text files in directory
def build_point_matrix(dirname):
    points_matrix = []
    for points_file in sorted(query(dirname, "txt")):
        points_matrix.append(get_points_from_disk(points_file))

    return points_matrix


# Read all images in folder.
def build_image_matrix(dirname):
    image_matrix = []
    for image_file in sorted(query(dirname, "images")):
        # Read image found.
        img = cv2.imread(image_file)
        # Convert to floating point
        img = np.float32(img) / 255.0
        # Add to matrix of images
        image_matrix.append(img)

    return image_matrix


def similarity_transform(inPoints, outPoints):
    """Compute similarity transform given two lists of two points in form [(x, y), (x, y)]
    
    Notes
    -----
    Because OpenCV requires 3 pairs of corresponding points for a similarity transform, 
    we have to fake the third one
    """
    s60 = np.sin(60 * np.pi / 180)
    c60 = np.cos(60 * np.pi / 180)

    inPts = np.copy(inPoints).tolist()
    outPts = np.copy(outPoints).tolist()

    xin = (
        c60 * (inPts[0][0] - inPts[1][0])
        - s60 * (inPts[0][1] - inPts[1][1])
        + inPts[1][0]
    )
    yin = (
        s60 * (inPts[0][0] - inPts[1][0])
        + c60 * (inPts[0][1] - inPts[1][1])
        + inPts[1][1]
    )
    inPts.append([np.int(xin), np.int(yin)])

    xout = (
        c60 * (outPts[0][0] - outPts[1][0])
        - s60 * (outPts[0][1] - outPts[1][1])
        + outPts[1][0]
    )
    yout = (
        s60 * (outPts[0][0] - outPts[1][0])
        + c60 * (outPts[0][1] - outPts[1][1])
        + outPts[1][1]
    )
    outPts.append([np.int(xout), np.int(yout)])
    return cv2.estimateAffinePartial2D(np.array([inPts]), np.array([outPts]))[0]


def delaunay_triangulation(rect, points):
    """Given a rectangle and a list of points, calculate the delaunay triangulation"""
    subdiv = cv2.Subdiv2D(rect)
    for x, y in points:
        subdiv.insert((x, y))

    dt = []
    for t in subdiv.getTriangleList():
        pts = [(t[0], t[1]), (t[2], t[3]), (t[4], t[5])]
        if (
            point_in_rect(rect, pts[0])
            and point_in_rect(rect, pts[1])
            and point_in_rect(rect, pts[2])
        ):
            ind = []
            for j in range(3):
                for k in range(len(points)):
                    if (
                        abs(pts[j][0] - points[k][0]) < 1.0
                        and abs(pts[j][1] - points[k][1]) < 1.0
                    ):
                        ind.append(k)
            if len(ind) == 3:
                dt.append((ind[0], ind[1], ind[2]))
    return dt


def constrainPoint(p, w, h):
    return (min(max(p[0], 0), w - 1), min(max(p[1], 0), h - 1))


def apply_affine_transform(src, src_tri, dst_tri, size):
    """Apply affine transform calculated using srcTri and dstTri to src and output an image of size"""
    affine_transform = cv2.getAffineTransform(np.float32(src_tri), np.float32(dst_tri))
    return cv2.warpAffine(
        src,
        affine_transform,
        (size[0], size[1]),
        None,
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REFLECT_101,
    )


def warpTriangle(img1, img2, t1, t2):
    """Warp and alpha blend triangular regions from src images into output image"""
    r1 = cv2.boundingRect(np.float32([t1]))
    r2 = cv2.boundingRect(np.float32([t2]))
    t1Rect = []
    t2Rect = []
    t2RectInt = []
    for i in range(3):
        t1Rect.append(((t1[i][0] - r1[0]), (t1[i][1] - r1[1])))
        t2Rect.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))
        t2RectInt.append(((t2[i][0] - r2[0]), (t2[i][1] - r2[1])))

    # Get mask by filling triangle
    mask = np.zeros((r2[3], r2[2], 3), dtype=np.float32)
    cv2.fillConvexPoly(mask, np.int32(t2RectInt), (1.0, 1.0, 1.0), 16, 0)

    # Apply warpImage to small rectangular patches
    img1Rect = img1[r1[1] : r1[1] + r1[3], r1[0] : r1[0] + r1[2]]

    size = (r2[2], r2[3])
    img2Rect = apply_affine_transform(img1Rect, t1Rect, t2Rect, size)
    img2Rect = img2Rect * mask

    # Copy triangular region of the rectangular patch to the output image
    img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] = img2[
        r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]
    ] * ((1.0, 1.0, 1.0) - mask)
    img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] = (
        img2[r2[1] : r2[1] + r2[3], r2[0] : r2[0] + r2[2]] + img2Rect
    )


def average_faces(directory_path, output_filepath, output_dimensions=(600, 600)):
    w, h = output_dimensions

    # Generate point and image matrices
    point_matrix = build_point_matrix(directory_path)
    images = build_image_matrix(directory_path)

    # Eye corners
    eyecorner_dst = [(np.int(0.3 * w), np.int(h / 3)), (np.int(0.7 * w), np.int(h / 3))]

    images_norm = []
    points_norm = []

    # Add boundary points for delaunay triangulation
    boundary_pts = np.array(
        [
            (0, 0),
            (w / 2, 0),
            (w - 1, 0),
            (w - 1, h / 2),
            (w - 1, h - 1),
            (w / 2, h - 1),
            (0, h - 1),
            (0, h / 2),
        ]
    )
    # Initialize location of average points to 0s
    points_average = np.array(
        [(0, 0)] * (len(point_matrix[0]) + len(boundary_pts)), np.float32()
    )

    n = len(point_matrix[0])
    image_count = len(images)
    # Warp images and trasnform landmarks to output coordinate system,
    # and find average of transformed landmarks.
    for i in range(image_count):
        try:
            points1 = point_matrix[i]

            # Corners of the eye in input image
            eyecornerSrc = [point_matrix[i][36], point_matrix[i][45]]

            # Compute similarity transform
            st = similarity_transform(eyecornerSrc, eyecorner_dst)

            # Apply similarity transformation
            img = cv2.warpAffine(images[i], st, (w, h))

            # Apply similarity transform on points
            points2 = np.reshape(np.array(points1), (68, 1, 2))
            points = cv2.transform(points2, st)
            points = np.float32(np.reshape(points, (68, 2)))

            # Append boundary points. Will be used in Delaunay Triangulation
            points = np.append(points, boundary_pts, axis=0)

            # Calculate location of average landmark points.
            points_average = points_average + points / image_count
            points_norm.append(points)
            images_norm.append(img)
        except:
            # if empty matrix read
            pass

    # Delaunay triangulation
    rect = (0, 0, w, h)
    dt = delaunay_triangulation(rect, np.array(points_average))

    # Output image
    output = np.zeros((h, w, 3), np.float32())

    # Warp input images to average image landmarks
    for i in range(len(images_norm)):
        img = np.zeros((h, w, 3), np.float32())
        # Transform triangles one by one
        for j in range(len(dt)):
            t_in = []
            t_out = []

            for k in range(3):
                p_in = points_norm[i][dt[j][k]]
                p_in = constrainPoint(p_in, w, h)

                p_out = points_average[dt[j][k]]
                p_out = constrainPoint(p_out, w, h)

                t_in.append(p_in)
                t_out.append(p_out)

            warpTriangle(images_norm[i], img, t_in, t_out)
        # Add image intensities for averaging
        output = output + img
    # Divide by image_count to get average
    output = cv2.convertScaleAbs(output / image_count, alpha=(255.0))
    cv2.imshow("image", output)
    cv2.waitKey(0)
    cv2.imwrite(output_filepath, output, params=(cv2.IMWRITE_JPEG_QUALITY, 0))
