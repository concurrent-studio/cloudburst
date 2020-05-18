# cloudburst ⛈
[![CircleCI](https://circleci.com/gh/concurrent-studio/cloudburst.svg?style=shield)](https://circleci.com/gh/concurrent-studio/cloudburst) [![Documentation](https://img.shields.io/badge/docs-reference-brightgreen.svg)](https://concurrent-studio.github.io/cloudburst/) [![License: MIT](https://img.shields.io/badge/packager-pypak-dbd3cd.svg)](https://github.com/concurrent-studio/pypak) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![PyPI](https://img.shields.io/pypi/v/cloudburst)

A python package for computational design by [CONCURRENT STUDIO™](https://www.concurrent.studio)


## ⏳ Installation
### 🐍 Pip
```bash
pip3 install cloudburst
```

### 🗃 Source
```bash
git clone https://github.com/concurrent-studio/cloudburst.git
cd cloudburst
pip3 install -e .
```

## Documentation 
A brief description of modules and submodules exists below.  
For ruther information, see the [usage guide](https://concurrent-studio.github.io/cloudburst/).

### 📦 Modules + Submodules
#### 🛠 Core Functions
##### Usage
```python
import cloudburst as cb
```

##### Components
- Core
    - `concurrent`
        - Execute a function concurrently over a list
    - `mkdir`
        - Make a new directory if one doesn't exist
    - `query`
        - Query a folder by filename extension
    - `write_list_to_file`
        - Write a given list to a file
    - `get_list_from_file`
        - Read a file line by line into a list
    - `write_dict_to_file`
        - Write a dictionary to a .json file
    - `line_coeff_from_segment`
        - Get slope and y intersect given two points on a line
    - `tri_centroid`
        - Calculate the centroid of a triangle given its vertices
    - `quad_centroid`
        - Calculate the centroid of a quadrilateral given its vertices
    - `point_in_rect`
        - Check whether a point is in a rectangle given the rectangle's vertices

#### 📱 Social
##### Usage
```python
from cloudburst import social as cbs
```

##### Components
- `Instagram`
    - Class for scraping the data of an Instagram user
    - `__init__`
        - Constructor method
    - `download_profile_picture`
        - Download an Instagram user's profile picure in its highest quality
    - `get_previews`
        - Get low-res Instagram previews for media
    - `download_stories`
        - Download all stories
    - `download_highlights`
        - Download all highlights
    - `download_thumbnails`
        - Download all thumbnails
    - `download_posts`
        - Download all posts from an Instagram user
    - `get_post_by_number`
        - Find the shortcode of a post based on its number (-1 = first post, list notation)
    - `search_captions_by_keyword`
        - Search all captions for a specific keyword
    - `get_tagged_users` 
        - Get a ranked list of all tagged users
    - `get_tagged_users_in_captions` 
        - Get a ranked list of all tagged users in captions
    - `get_hashtags`
        - Get all hashtags posted by a user
    - `get_posts_by_like_count`
        - Ranked posts by descending like count
    - `get_lifetime_like_count`
        - Get total number of likes a user has received over their lifetime
    
- `download_instagram_by_shortcode`
    - Download media and data from a posed given its shortcode 

- `VSCO`
    - Class for scraping the data of a VSCO user
    - `download_images`
        - Download the user's images
    - `download_journal`
        - Download the user's journal posts
    - `download_all`
        - `download_images` and `download_journal` encapsulated in a single call

#### 📹 Vision
##### Usage
```python
from cloudburst import vision as cbv
```

##### Components
- Color
    - `color_delta`
        - Compute the percent difference between two given colors
    - `get_colors`
        - Get a color palette from a given image
-  Face
    - `get_faces`
        - Get all faces
    - `get_eyes`
        - Get all eyes
    - `face_match`
        - Compare a list of unknown faces against a known one
    - `get_landmarks`
        - Get 68 (or 5) facial landmarks from an image
    - `average_faces`
        - Compute the average of all faces in a directory
-  Face3D
    - `face_to_3d`
        - Transform a 2D image of a face into a 3D model
- I/O
    - `download`
        - Download an image or video from a url
    - `write_points_to_disk`
        - Write a list of points to disk
    - `get_points_from_disk`
        - Get points saved through above function
    - `load_png`
        - Load a png file, transforming the alpha channel into a given color
- Transform
    - `draw_points_on_image`
        - Draw a set of points on top of an image
    - `draw_rect_on_image`
        - Draw a rectangle on top of an image
    - `create_collage`
        - Create a collage from a list of images