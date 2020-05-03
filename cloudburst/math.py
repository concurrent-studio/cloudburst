# -*- coding: utf-8 -*-
"""
Math Functions
==============
A variety of math-related functions for cloudburst

.. autosummary::
    :toctree: generated/

    line_coeff_from_segment
    tri_centroid
    quad_centroid
    point_in_rect
"""

__all__ = ["line_coeff_from_segment", "tri_centroid", "quad_centroid", "point_in_rect"]


def line_coeff_from_segment(point_a, point_b):
    """Given a line segment (two points), find the slope (m) and y-intercept (b) of line y=mx+b

    Parameters
    ----------
    point_a : tuple
        coordinates of the first point
    
    point_b : tuple
        coordinates of the second point

    Return
    ------
    m : float
        the line's slope

    b : float
        the line's y-intercept

    Examples
    --------
    Find the 
    .. code-block:: python
        import cloudburst as cb
        (m, b) = cb.line_coeff_from_segment((8, 3), (-1, 10))
        print("line: y={}x+{}".format(m, b))
    """
    # slope of line
    m = (point_b[1] - point_a[1])/(point_b[0] - point_a[0])
    # y-intercept of line
    b = point_a[1] - (m*point_a[0])

    return m, b

def tri_centroid(vertex_a, vertex_b, vertex_c):
    """Find the centroid of any triangle given its vertices

    Parameters
    ----------
    vertex_a : tuple
        coordinates of the first vertex
    
    vertex_b : tuple
        coordinates of the second vertex
    
    vertex_c : tuple
        coordinates of the third vertex

    Return
    ------
    centroid : tuple
        the triangle's centroid

    Examples
    --------
    Find the centroid of the traingle formed by points (2, 4), (6, 1), (8, 10)
    .. code-block:: python
        import cloudburst as cb
        centroid = cb.tri_centroid((2, 4), (6, 1), (8, 10))
        print(centroid)
    """
    # average x coords
    centroid_x = (vertex_a[0] + vertex_b[0] + vertex_c[0])/3
    # average y coords
    centroid_y = (vertex_a[1] + vertex_b[1] + vertex_c[1])/3
    
    return (centroid_x, centroid_y)

def quad_centroid(vertex_a, vertex_b, vertex_c, vertex_d, integer=False):
    """Find the centroid of any quadrilateral given its vertices

    Parameters
    ----------
    vertex_a : tuple
        coordinates of the first vertex
    
    vertex_b : tuple
        coordinates of the second vertex
    
    vertex_c : tuple
        coordinates of the third vertex
    
    vertex_d : tuple
        coordinates of the fourth vertex

    Return
    ------
    centroid : tuple
        the quadrilateral's centroid

    Examples
    --------
    Find the centroid of the quadrilateral formed by vertices (1, 0), (2, 8), (9, -1), (10, 2)
    .. code-block:: python    
        import cloudburst as cb
        centroid = cb.quad_centroid((1, 0), (2, 8), (9, -1), (10, 2))
        print(centroid)
    """
    # Break quadrilateral into component triangles
    triangles = []
    triangle_a = (vertex_a, vertex_b, vertex_c)
    triangle_b = (vertex_a, vertex_d, vertex_c)
    triangle_c = (vertex_a, vertex_d, vertex_b)
    triangle_d = (vertex_b, vertex_d, vertex_c)
    triangles.extend((triangle_a, triangle_b, triangle_c, triangle_d))

    # Calculate centroids of triangles
    centroids = []
    for triangle in triangles:
        centroids.append(tri_centroid(triangle[0], triangle[1], triangle[2]))
    # Sort centroids by y value to ensure correct calculation
    centroids = sort_tuples(centroids)
    # Ensure that vertex a has a lower x value than vertex b
    if centroids[0][0] > centroids[1][0]:
        centroids = [centroids[1], centroids[0], centroids[2], centroids[3]]
    
    # Ensure that vertex d has a lower x value than vertex c
    if centroids[3][0] > centroids[2][0]:
        centroids = [centroids[0], centroids[1], centroids[3], centroids[2]]

    # Equation of line running between abc's centroid and adc's centroid
    (m1, b1) = line_coeff_from_segment(centroids[0], centroids[2])
    # Equation of line running between adb's centroid and bdc's centroid
    (m2, b2) = line_coeff_from_segment(centroids[1], centroids[3])

    # Calculate centroid x coordinate by setting the two lines equal to each other
    centroid_x = (b2 - b1)/(m1 - m2)
    # Plug the x coordinate into the first line
    centroid_y = m1 * centroid_x + b1

    # Set centroid as tuple of two points, integers if specified
    if integer:
        centroid = (int(round(centroid_x)), int(round(centroid_y)))
    else:
        centroid = (centroid_x, centroid_y)
    return centroid

def point_in_rect(rect, point):
    ### NEEDS WORK
    """Given a rectangle and a point, check if the point is inside the rectangle

    Parameters
    ----------
    rectangle : list
        coordinates of rectangle vertices
    
    point : tuple
        coordinates of point to check 

    Return
    ------
    within_rectangle : boolean
        whether or not the point is in the rectangle

    Examples
    --------
    Find the 
    .. code-block:: python
        import cloudburst as cb

        rect = [(1, 4), (1, 8), (2, 8), (2, 4)]
        print(cb.point_in_rect(rect, (1,1)))
    """    
    if point[0] < rect[0]:
        return False
    elif point[1] < rect[1]:
        return False
    elif point[0] > rect[2]:
        return False
    elif point[1] > rect[3]:
        return False
    else:
        return True
