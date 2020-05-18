# -*- coding: utf-8 -*-
import os
import cv2
import dlib
import cloudburst as cb
import numpy as np
import face_recognition
import face_recognition_models
from glob import glob
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from imutils import face_utils
from cloudburst.core import concurrent
from .io import load_png, get_points_from_disk, write_points_to_disk
from .transform import draw_points_on_image, draw_rect_on_image

# nose = landmarks[27:36]
# mouth = landmarks[48:68] haarcascade_mcs_mouth
# haarcascade_fullbody.xml

__all__ = ["get_faces", "get_eyes", "get_landmarks", "average_faces"]

this_folder = os.path.abspath(os.path.dirname(__file__))


def _bounding_box(points):
    x = [x for x, y in points]
    y = [y for x, y in points]
    return min(x), min(y), max(x) - min(x), max(y) - min(y)


def _box_padding(box_x, box_y, box_w, box_h, image_w, image_h, w_padding, h_padding):
    top = 0 if int(box_y - h_padding) < 0 else int(box_y - h_padding)
    bottom = (
        image_h
        if int(box_y + box_h + h_padding) > image_h
        else int(box_y + box_h + h_padding)
    )
    left = 0 if int(box_x - w_padding) < 0 else int(box_x - w_padding)
    right = (
        image_w
        if int(box_x + box_w + w_padding) > image_w
        else int(box_x + box_w + w_padding)
    )
    return top, bottom, left, right


# Function to deconstruct rectangle into its vertices
def _dlib_rect_deconstruct(rect):
    return rect.top(), rect.right(), rect.bottom(), rect.left()


def _get_face(args):
    # Unpack tuple
    (
        path,
        mode,
        output_dir,
        padding,
        model,
        face_detector,
        shape_predictor,
        upsample_factor,
        landmarks,
        only_landmarked,
        overwrite,
    ) = args

    # Image results
    image_results = []

    # Check for existing landmark files unless overwrite active
    if not overwrite:
        landmark_file = glob("{}*.txt".format(Path(path).with_suffix("")))

    source_filename = Path(path).with_suffix("").name

    if landmark_file == []:
        try:
            # Load file
            filetype = Path(path).suffix.lower()
            if filetype == ".jpg" or ".jpeg":
                image_array = np.array(Image.open(path).convert("RGB"))
            elif filetype == ".png":
                image_array = np.array(load_png(path))
            else:
                print(f"Filetype {filetype} not currently supported, skipping {path}")
                pass

            # Get face locations
            if model == "cnn":
                face_locations = face_detector(image_array, upsample_factor)
            elif model == "hog":
                face_locations = face_detector(image_array, upsample_factor)
            elif model == "haar_front":
                face_cascade = cv2.CascadeClassifier(
                    "{}/models/haarcascade_frontalface_default.xml".format(this_folder)
                )
                face_locations = face_cascade.detectMultiScale(
                    image_array, scaleFactor=1.1, minNeighbors=5
                )
            elif model == "haar_profile":
                face_cascade = cv2.CascadeClassifier(
                    "{}/models/haarcascade_profileface.xml".format(this_folder)
                )
                face_locations = face_cascade.detectMultiScale(
                    image_array, scaleFactor=1.1, minNeighbors=5
                )

            # Crop faces with padding
            h, w, _ = image_array.shape
            for idx, face_location in enumerate(face_locations):
                if model == "cnn":
                    t, r, b, l = _dlib_rect_deconstruct(face_location.rect)
                elif model == "haar":
                    x, y, w, h = face_location
                    t, r, b, l = y, x + w, y + h, x
                elif model == "hog":
                    t, r, b, l = _dlib_rect_deconstruct(face_location)

                top, bottom, left, right = _box_padding(
                    l, t, r - l, b - t, w, h, padding * (r - l), padding * (b - t)
                )

                cropped_face_array = image_array[top:bottom, left:right]
                cropped_face = Image.fromarray(cropped_face_array)
                outfile = Path(output_dir).joinpath(
                    Path("{}_face{}.jpg".format(source_filename, idx))
                )

                face_landmarks = []
                if landmarks:
                    pass
                    # Load image and convert to grayscale
                    image_grayscale = np.asarray(
                        Image.fromarray(cropped_face_array).convert(mode="L")
                    )
                    # Find landmarks on all given faces
                    for (i, rect) in enumerate(face_detector(image_grayscale, 0)):
                        # Make the prediction, tranferring it to numpy array
                        for landmark in face_utils.shape_to_np(
                            shape_predictor(image_grayscale, rect)
                        ):
                            face_landmarks.append(
                                (float(landmark[0]), float(landmark[1]))
                            )

                image_results.append(
                    (source_filename, outfile, cropped_face, face_landmarks)
                )
        except:
            print("Error occured at {}".format(path))
            pass
    else:
        cropped_face = Image.open(path)

        face_landmarks = get_points_from_disk(landmark_file)

        jpg = Path(landmark_file).with_suffix(".jpg")
        jpeg = Path(landmark_file).with_suffix(".jpeg")
        png = Path(landmark_file).with_suffix(".png")
        if jpg.exists:
            outfile = jpg
        elif jpeg.exists:
            outfile = jpeg
        elif png.exists:
            outfile = png
        else:
            outfile = "File not found"

        image_results.append((landmark_file, outfile, cropped_face, face_landmarks))

    if mode == "show":
        for result in image_results:
            if result[3] != []:
                draw_points_on_image(result[2], result[3]).show()
            elif result[3] == [] and landmarks:
                pass
            else:
                result[2].show()

    if mode == "save":
        for result in image_results:
            if result[0].endswith(".txt"):
                print("Save not required, landmark file already exists")
            else:
                if only_landmarked:
                    if result[3] != []:
                        result[2].save(result[1])
                        write_points_to_disk(result[1].with_suffix(".txt"), result[3])
                    else:
                        pass
                else:
                    result[2].save(result[1])

    return image_results


def get_faces(
    image_path,
    mode="save",
    output_dir="faces",
    padding=0.5,
    model="hog",
    upsample_factor=1,
    landmarks=True,
    only_landmarked=True,
    overwrite=False,
):
    """Get all faces within an image

    Parameters
    ----------
    image_path : str
        filepath to an image file
    padding : float
        pecentage of padding to expand
    upsample_factor : int
        number of times to upsample image

    Returns
    -------
    faces : list
        list of images of faces in the given image
    """
    
    # Print Errors
    if mode not in ["save", "show", "return"]:
        print("Error: mode must be save (default), show, or return")
        quit()
    if model not in ["cnn", "hog", "haar_front", "haar_profile"]:
        print("Error: mode must be save (default), show, or return")
        quit()

    # Load face detectors
    if model == "cnn":
        face_detector = dlib.cnn_face_detection_model_v1(
            face_recognition_models.cnn_face_detector_model_location()
        )
    elif model == "hog":
        face_detector = dlib.get_frontal_face_detector()
    shape_predictor = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # Ensure list of image paths passed
    image_paths = [image_path] if isinstance(image_path, str) else image_path
    faces_to_threadpool = []
    for image_path in image_paths:
        faces_to_threadpool.append(
            (
                image_path,
                mode,
                output_dir,
                padding,
                model,
                face_detector,
                shape_predictor,
                upsample_factor,
                landmarks,
                only_landmarked,
                overwrite,
            )
        )

    # Create output directory
    if mode == "save":
        cb.mkdir(output_dir)

    return concurrent(
        _get_face,
        faces_to_threadpool,
        executor="threadpool",
        progress_bar=True,
        desc="Getting faces",
    )


def get_eyes(
    image_path,
    mode="save_with_progress",
    output_dir="eyes",
    padding=0.2,
    model="landmarks",
):
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

    if mode == "save_with_progress":
        face_mode = "save"
        mode = "save"
    else:
        face_mode = "return"

    # Create output directory
    if mode == "save":
        cb.mkdir(output_dir)

    # Convert to list if a single path is given
    image_paths = [image_path] if isinstance(image_path, str) else image_path

    wp = padding
    hp = padding

    landmarks = False
    eyes_cascade = cv2.CascadeClassifier(
        "{}/models/haarcascade_eye.xml".format(this_folder)
    )
    if model == "landmarks":
        landmarks = True
        wp += 0.5
        hp += 1
    elif model == "haar2":
        eyes_cascade = cv2.CascadeClassifier(
            "{}/models/haarcascade_eye_tree_eyeglasses.xml".format(this_folder)
        )
    else:
        print(
            "Error: either landmarks (default) haar1 or haar2 model type must be specified"
        )
        exit(1)

    print(output_dir)
    results = []
    for landmark_file, filename, face, face_landmarks in get_faces(
        image_paths,
        mode=face_mode,
        landmarks=landmarks,
        output_dir="{}_faces".format(output_dir),
    ):
        face_array = np.array(face)
        if landmarks:
            if face_landmarks != []:
                eyes = [
                    _bounding_box(face_landmarks[36:42]),
                    _bounding_box(face_landmarks[42:48]),
                ]
            else:
                continue
        else:
            eyes = eyes_cascade.detectMultiScale(face_array)
            try:
                eye_angle = np.degrees(
                    np.arctan((eyes[1][1] - eyes[0][1]) / (eyes[1][0] - eyes[0][0]))
                )
                rows, cols = face_array.shape[:2]
                face_array = cv2.warpAffine(
                    face_array,
                    cv2.getRotationMatrix2D((cols / 2, rows / 2), eye_angle, 1),
                    (cols, rows),
                )
            except:
                pass

        eyes_on_face = []
        for idx, (ex, ey, ew, eh) in enumerate(eyes):
            h, w, _ = face_array.shape
            top, bottom, left, right = _box_padding(
                ex, ey, ew, eh, w, h, wp * ew, hp * eh
            )
            height = bottom - top
            width = right - left
            if width > height:
                extra_padding = int((width - height) / 2)
                top -= extra_padding
                bottom = top + width
            else:
                extra_padding = int((height - width) / 2)
                left -= extra_padding
                right = left + height

            print(bottom - top, right - left)
            try:
                cropped_eye = Image.fromarray(face_array[top:bottom, left:right])
                outfile = Path(output_dir).joinpath(
                    "{}_eye{}.jpg".format(Path(filename).with_suffix("").name, idx)
                )

                if mode == "save":
                    cropped_eye.save(outfile)
                elif mode == "show":
                    eyes_on_face.extend([(left, top), (right, bottom)])
                elif mode == "return":
                    results.append((str(outfile), cropped_eye))
                else:
                    print("Error: mode must be save (default), show, or return")
                    exit(1)
            except:
                print("FUCK")
                pass

        if mode == "show":
            if landmarks:
                face = draw_points_on_image(face, landmarks[36:48])
            draw_rect_on_image(
                draw_rect_on_image(face, eyes_on_face[0:2]), eyes_on_face[2:4]
            ).show()

    return results


def get_landmarks(image_path, model="68", mode="save"):
    """Get coordinates of 68 facial landmarks from a given image

    Parameters
    ----------
    image_path : str
        path (or list of paths) to an image(s)

    Examples
    --------
    Get and crop the faces of all images in './images' folder

    .. code-block:: python

        from cloudburst import vision as cbv
        import cloudburst as cb

        paths = cb.query('images', 'jpg')
        for image_path in paths:
            cbv.get_landmarks(image_path)
    """

    # Configure detector
    if model == "68":
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            face_recognition_models.pose_predictor_model_location()
        )
    elif model == "5":
        detector = dlib.get_frontal_face_detector()
        predictor = dlib.shape_predictor(
            face_recognition_models.pose_predictor_five_point_model_location()
        )
    else:
        print("Error: choose a valid model: 68 (default) or 5")
        exit(1)

    image_array = np.asarray(Image.open(image_path))

    # Load image and convert to grayscale
    image_grayscale = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    landmarks = []
    # Find landmarks on all given faces
    for (i, rect) in enumerate(detector(image_grayscale, 0)):
        # Make the prediction, tranferring it to numpy array
        shape = face_utils.shape_to_np(predictor(image_grayscale, rect))

        for landmark in shape:
            landmarks.append((float(landmark[0]), float(landmark[1])))

    if mode == "save":
        write_points_to_disk(Path(image_path).with_suffix(".txt"), landmarks)

    return landmarks


########################### AVERAGE FACES ###########################
"""THIS NEEDS TO BE CLEANED UP BIG TIME"""
# Read points from text files in directory
def build_point_matrix(dirname):
    points_matrix = []
    for points_file in sorted(cb.query(dirname, "txt")):
        points_matrix.append(get_points_from_disk(points_file))

    return points_matrix


# Read all images in folder.
def build_image_matrix(dirname):
    image_matrix = []
    for image_file in sorted(cb.query(dirname, "images")):
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
            cb.point_in_rect(rect, pts[0])
            and cb.point_in_rect(rect, pts[1])
            and cb.point_in_rect(rect, pts[2])
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
    """Average a set of faces into a single composite image

    Parameters
    ----------
    directory_path : str
        path to directory inside which all images will be averaged
    output_filepath : str
        path that the image will be saved to
    output_dimensions : tuple
        size of output image

    Examples
    --------
    Average all faces in './faces' folder

    .. code-block:: python
    
        from cloudburst import vision as cbv

        cbv.average_faces("./test_dir", "average.jpg")
    """

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
    # cv2.imshow("image", output)
    cv2.waitKey(0)
    cv2.imwrite(str(output_filepath), output)
