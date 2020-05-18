# -*- coding: utf-8 -*-
import os
import cloudburst as cb
import numpy as np
import tensorflow.compat.v1 as tf
from pathlib import Path
from PIL import Image
from scipy.io import loadmat

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
this_folder = os.path.abspath(os.path.dirname(__file__))

# BFM 3D face model
class BFM:
    def __init__(self, bfm_model_path):
        model = loadmat(bfm_model_path)
        self.meanshape = tf.constant(model["meanshape"])
        self.idBase = tf.constant(model["idBase"])
        self.exBase = tf.constant(model["exBase"].astype(np.float32))
        self.meantex = tf.constant(model["meantex"])
        self.texBase = tf.constant(model["texBase"])
        self.point_buf = tf.constant(model["point_buf"])
        self.face_buf = tf.constant(model["tri"])
        self.keypoints = tf.squeeze(tf.constant(model["keypoints"]))


# Analytic 3D face reconstructor
class FaceTo3D:
    def __init__(self, bfm_model_path):
        facemodel = BFM(bfm_model_path)
        self.facemodel = facemodel

    # analytic 3D face reconstructions with coefficients from R-Net
    def Reconstruction_Block(self, coeff, batchsize):
        # coeff: [batchsize,257] reconstruction coefficients
        id_coeff, ex_coeff, tex_coeff, angles, translation, gamma = self.Split_coeff(
            coeff
        )

        # [batchsize,N,3] canonical face shape in BFM space
        face_shape = self.Shape_formation_block(id_coeff, ex_coeff, self.facemodel)

        # # [batchsize,N,3] vertex texture (in RGB order)
        face_texture = self.Texture_formation_block(tex_coeff, self.facemodel)
        self.face_texture = face_texture

        # [batchsize,3,3] rotation matrix for face shape
        rotation = self.Compute_rotation_matrix(angles)

        # [batchsize,N,3] vertex normal
        face_norm = self.Compute_norm(face_shape, self.facemodel)
        norm_r = tf.matmul(face_norm, rotation)

        # do rigid transformation for face shape using predicted rotation and translation
        face_shape_t = self.Rigid_transform_block(face_shape, rotation, translation)
        self.face_shape_t = face_shape_t

        # [batchsize,N,3] vertex color (in RGB order)
        face_color = self.Illumination_block(face_texture, norm_r, gamma)
        self.face_color = face_color

    def Split_coeff(self, coeff):
        id_coeff = coeff[:, :80]  # identity
        ex_coeff = coeff[:, 80:144]  # expression
        tex_coeff = coeff[:, 144:224]  # texture
        angles = coeff[:, 224:227]  # euler angles for pose
        gamma = coeff[:, 227:254]  # lighting
        translation = coeff[:, 254:257]  # translation

        return id_coeff, ex_coeff, tex_coeff, angles, translation, gamma

    def Shape_formation_block(self, id_coeff, ex_coeff, facemodel):
        face_shape = (
            tf.einsum("ij,aj->ai", facemodel.idBase, id_coeff)
            + tf.einsum("ij,aj->ai", facemodel.exBase, ex_coeff)
            + facemodel.meanshape
        )
        # reshape face shape to [batchsize,N,3], re-centering the face shape with mean shape
        return tf.reshape(face_shape, [tf.shape(face_shape)[0], -1, 3]) - tf.reshape(
            tf.reduce_mean(tf.reshape(facemodel.meanshape, [-1, 3]), 0), [1, 1, 3]
        )

    def Compute_norm(self, face_shape, facemodel):
        face_id = tf.cast(facemodel.face_buf - 1, tf.int32)

        # compute normal for each face
        v1 = tf.gather(face_shape, face_id[:, 0], axis=1)
        v2 = tf.gather(face_shape, face_id[:, 1], axis=1)
        v3 = tf.gather(face_shape, face_id[:, 2], axis=1)

        face_norm = tf.concat(
            [
                tf.nn.l2_normalize(tf.cross(v1 - v2, v2 - v3), axis=2),
                tf.zeros([tf.shape(face_shape)[0], 1, 3]),
            ],
            axis=1,
        )

        # compute normal for each vertex using one-ring neighborhood
        return tf.nn.l2_normalize(
            tf.reduce_sum(
                tf.gather(
                    face_norm, tf.cast(facemodel.point_buf - 1, tf.int32), axis=1
                ),
                axis=2,
            ),
            axis=2,
        )

    def Texture_formation_block(self, tex_coeff, facemodel):
        face_texture = (
            tf.einsum("ij,aj->ai", facemodel.texBase, tex_coeff) + facemodel.meantex
        )

        # reshape face texture to [batchsize,N,3], note that texture is in RGB order
        return tf.reshape(face_texture, [tf.shape(face_texture)[0], -1, 3])

    def Compute_rotation_matrix(self, angles):
        n_data = tf.shape(angles)[0]

        # compute rotation matrix for X-axis, Y-axis, Z-axis respectively
        rotation_X = tf.concat(
            [
                tf.ones([n_data, 1]),
                tf.zeros([n_data, 3]),
                tf.reshape(tf.cos(angles[:, 0]), [n_data, 1]),
                -tf.reshape(tf.sin(angles[:, 0]), [n_data, 1]),
                tf.zeros([n_data, 1]),
                tf.reshape(tf.sin(angles[:, 0]), [n_data, 1]),
                tf.reshape(tf.cos(angles[:, 0]), [n_data, 1]),
            ],
            axis=1,
        )

        rotation_Y = tf.concat(
            [
                tf.reshape(tf.cos(angles[:, 1]), [n_data, 1]),
                tf.zeros([n_data, 1]),
                tf.reshape(tf.sin(angles[:, 1]), [n_data, 1]),
                tf.zeros([n_data, 1]),
                tf.ones([n_data, 1]),
                tf.zeros([n_data, 1]),
                -tf.reshape(tf.sin(angles[:, 1]), [n_data, 1]),
                tf.zeros([n_data, 1]),
                tf.reshape(tf.cos(angles[:, 1]), [n_data, 1]),
            ],
            axis=1,
        )

        rotation_Z = tf.concat(
            [
                tf.reshape(tf.cos(angles[:, 2]), [n_data, 1]),
                -tf.reshape(tf.sin(angles[:, 2]), [n_data, 1]),
                tf.zeros([n_data, 1]),
                tf.reshape(tf.sin(angles[:, 2]), [n_data, 1]),
                tf.reshape(tf.cos(angles[:, 2]), [n_data, 1]),
                tf.zeros([n_data, 3]),
                tf.ones([n_data, 1]),
            ],
            axis=1,
        )

        rotation = tf.transpose(
            tf.matmul(
                tf.matmul(
                    tf.reshape(rotation_Z, [n_data, 3, 3]),
                    tf.reshape(rotation_Y, [n_data, 3, 3]),
                ),
                tf.reshape(rotation_X, [n_data, 3, 3]),
            ),
            perm=[0, 2, 1],
        )

        return rotation

    def Illumination_block(self, face_texture, norm_r, gamma):
        n_data = tf.shape(gamma)[0]
        n_point = tf.shape(norm_r)[1]
        gamma = tf.reshape(gamma, [n_data, 3, 9])
        # set initial lighting with an ambient lighting
        init_lit = tf.constant([0.8, 0, 0, 0, 0, 0, 0, 0, 0])
        gamma = gamma + tf.reshape(init_lit, [1, 1, 9])

        # compute vertex color using SH function approximation
        a0 = np.pi
        a1 = 2 * np.pi / tf.sqrt(3.0)
        a2 = 2 * np.pi / tf.sqrt(8.0)
        c1 = tf.sqrt(3.0) / tf.sqrt(4 * np.pi)
        c2 = 3 * tf.sqrt(5.0) / tf.sqrt(12 * np.pi)

        Y = tf.concat(
            [
                tf.tile(
                    tf.reshape(a0 * 1 / tf.sqrt(4 * np.pi), [1, 1, 1]),
                    [n_data, n_point, 1],
                ),
                tf.expand_dims(-a1 * c1 * norm_r[:, :, 1], 2),
                tf.expand_dims(a1 * c1 * norm_r[:, :, 2], 2),
                tf.expand_dims(-a1 * c1 * norm_r[:, :, 0], 2),
                tf.expand_dims(a2 * c2 * norm_r[:, :, 0] * norm_r[:, :, 1], 2),
                tf.expand_dims(-a2 * c2 * norm_r[:, :, 1] * norm_r[:, :, 2], 2),
                tf.expand_dims(
                    a2 * c2 * 0.5 / tf.sqrt(3.0) * (3 * tf.square(norm_r[:, :, 2]) - 1),
                    2,
                ),
                tf.expand_dims(-a2 * c2 * norm_r[:, :, 0] * norm_r[:, :, 2], 2),
                tf.expand_dims(
                    a2
                    * c2
                    * 0.5
                    * (tf.square(norm_r[:, :, 0]) - tf.square(norm_r[:, :, 1])),
                    2,
                ),
            ],
            axis=2,
        )

        # [batchsize,N,3] vertex color in RGB order
        return tf.stack(
            [
                tf.squeeze(tf.matmul(Y, tf.expand_dims(gamma[:, 0, :], 2)), axis=2)
                * face_texture[:, :, 0],
                tf.squeeze(tf.matmul(Y, tf.expand_dims(gamma[:, 1, :], 2)), axis=2)
                * face_texture[:, :, 1],
                tf.squeeze(tf.matmul(Y, tf.expand_dims(gamma[:, 2, :], 2)), axis=2)
                * face_texture[:, :, 2],
            ],
            axis=2,
        )

    def Rigid_transform_block(self, face_shape, rotation, translation):
        return tf.matmul(face_shape, rotation) + tf.reshape(
            translation, [tf.shape(face_shape)[0], 1, 3]
        )


# resize and crop input images before sending to the R-Net
def preprocess(img, lm, lm3D, target_size=224.0):
    w0, h0 = img.size
    xp = np.stack([lm[:, 0], h0 - 1 - lm[:, 1]], axis=1).transpose()
    x = lm3D.transpose()
    npts = xp.shape[1]
    A = np.zeros([2 * npts, 8])
    A[0 : 2 * npts - 1 : 2, 0:3] = x.transpose()
    A[0 : 2 * npts - 1 : 2, 3] = 1
    A[1 : 2 * npts : 2, 4:7] = x.transpose()
    A[1 : 2 * npts : 2, 7] = 1
    k, _, _, _ = np.linalg.lstsq(A, np.reshape(xp.transpose(), [2 * npts, 1]), rcond=-1)
    s = (np.linalg.norm(k[0:3]) + np.linalg.norm(k[4:7])) / 2
    t = np.stack([k[3], k[7]], axis=0)

    # processing the image
    w = (w0 / s * 102).astype(np.int32)
    h = (h0 / s * 102).astype(np.int32)
    img_new = img.resize((w, h), resample=Image.BICUBIC)

    left = (w / 2 - target_size / 2 + float((t[0] - w0 / 2) * 102 / s)).astype(np.int32)
    right = left + target_size
    up = (h / 2 - target_size / 2 + float((h0 / 2 - t[1]) * 102 / s)).astype(np.int32)
    below = up + target_size

    img_new = np.expand_dims(
        np.array(img_new.crop((left, up, right, below)))[:, :, ::-1], 0
    )
    lm_new = (
        np.stack([lm[:, 0] - t[0] + w0 / 2, lm[:, 1] - t[1] + h0 / 2], axis=1) / s * 102
    ) - np.reshape(
        np.array([(w / 2 - target_size / 2), (h / 2 - target_size / 2)]), [1, 2]
    )

    lm_new = np.stack([lm_new[:, 0], 223 - lm_new[:, 1]], axis=1)
    trans_params = np.array([w0, h0, 102.0 / s, t[0], t[1]])

    return img_new, lm_new, trans_params


# save 3D face to obj file
def save_obj(path, v, f, c):
    with open(path, "w") as file:
        for i in range(len(v)):
            file.write(
                "v {} {} {} {} {} {}\n".format(
                    v[i, 0], v[i, 1], v[i, 2], c[i, 0], c[i, 1], c[i, 2]
                )
            )
        file.write("\n")

        for i in range(len(f)):
            file.write("f {} {} {}\n".format(int(f[i, 0]), int(f[i, 1]), int(f[i, 2])))

    file.close()


def face_to_3d(
    input_images,
    output_path="",
    bfm_model_path="~/.cloudburst/BFM_model_front.mat",
    face_reconstruction_model_path="~/.cloudburst/FaceReconModel.pb",
):
    """Download an image or video from a URL

    Parameters
    ----------
    input_images : str
        path(s) to images to tranform
    output_path : str
        directory to write files to
    bfm_model_path : str
        path to model BFM model used for transform, can be found at https://concurrent.studio/face-to-3d
    face_reconstruction_model_path : str
        path to model face reconstruction model used for transform, can be found at https://concurrent.studio/face-to-3d

    Examples
    --------
    Convert an image of a face to a 3D wavefron object

    >>> from cloudburst import vision as cbv
    >>> # Assumes models are downloaded and stored in ~/.cloudburst
    >>> cbv.face_to_3d("./some_face.jpg")
    """
    # Expand user path on models
    bfm_model_path = Path(bfm_model_path).expanduser()
    face_reconstruction_model_path = Path(face_reconstruction_model_path).expanduser()

    if not bfm_model_path.exists() and face_reconstruction_model_path.exists():
        print(
            "\033[31mTo run this script, you must pass it the path to valid pre-trained models\nThese can be dowloaded at https://concurrent.studio/face-to-3d\033[0m"
        )
        exit(1)
    else:
        bfm_model_path = str(bfm_model_path)
        face_reconstruction_model_path = str(face_reconstruction_model_path)

    if not isinstance(input_images, list):
        input_images = [input_images]
    output_path = cb.mkdir(output_path)
    Lm3D = loadmat(f"{this_folder}/models/similarity_Lm3D_all.mat")["lm"]
    lm_idx = np.array([31, 37, 40, 43, 46, 49, 55]) - 1
    lm3d = np.stack(
        [
            Lm3D[lm_idx[0], :],
            np.mean(Lm3D[lm_idx[[1, 2]], :], 0),
            np.mean(Lm3D[lm_idx[[3, 4]], :], 0),
            Lm3D[lm_idx[5], :],
            Lm3D[lm_idx[6], :],
        ],
        axis=0,
    )[[1, 2, 0, 3, 4], :]

    # build reconstruction model
    with tf.Graph().as_default() as graph, tf.device("/cpu:0"):
        FaceReconstructor = FaceTo3D(bfm_model_path)
        images = tf.placeholder(
            name="input_imgs", shape=[1, 224, 224, 3], dtype=tf.float32
        )
        # images = tf.Variable(name="input_imgs", tf.ones(shape=[1, 224, 224, 3]), dtype=tf.float32)

        with tf.gfile.GFile(face_reconstruction_model_path, "rb") as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())

        tf.import_graph_def(
            graph_def, name="resnet", input_map={"input_imgs:0": images}
        )

        # output coefficients of R-Net (dim = 257)
        coeff = graph.get_tensor_by_name("resnet/coeff:0")

        # reconstructing faces
        FaceReconstructor.Reconstruction_Block(coeff, 1)
        face_shape = FaceReconstructor.face_shape_t  # need this
        face_texture = FaceReconstructor.face_texture
        face_color = FaceReconstructor.face_color  # need this
        tri = FaceReconstructor.facemodel.face_buf  # need this

        with tf.Session() as sess:
            for file in input_images:
                file = Path(file)

                try:
                    # load images and corresponding 5 facial landmarks
                    img = Image.open(file)
                    lm = np.loadtxt(file.with_suffix(".txt"))

                    # preprocess input image
                    input_img, lm_new, transform_params = preprocess(img, lm, lm3d)

                    (coeff_, face_shape_, face_texture_, face_color_, tri_) = sess.run(
                        [coeff, face_shape, face_texture, face_color, tri],
                        feed_dict={images: input_img},
                    )

                    # save output file
                    save_obj(
                        output_path.joinpath(Path(file).with_suffix(".obj").name),
                        np.squeeze(face_shape_, (0)),
                        tri_,
                        np.clip(np.squeeze(face_color_, (0)), 0, 255) / 255,
                    )

                except Exception as e:
                    print(e)
