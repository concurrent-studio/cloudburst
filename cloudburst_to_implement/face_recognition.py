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

       from cloudburst import vision as cbv
       import cloudburst as cb

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

# https://github.com/ageitgey/face_recognition/blob/d34c622bf42e2c619505a4884017051ecf61ac77/face_recognition/api.py#L92