# cloudburst ⛈
[![CircleCI](https://circleci.com/gh/concurrent-studio/cloudburst.svg?style=shield)](https://circleci.com/gh/concurrent-studio/cloudburst) [![Documentation](https://img.shields.io/badge/docs-reference-brightgreen.svg)](https://concurrent-studio.github.io/cloudburst/) [![License: MIT](https://img.shields.io/badge/packager-pypak-dbd3cd.svg)](https://github.com/concurrent-studio/pypak) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 


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
    - `sort_tuples`
        - Sort a list of tuples by their second element
- Math
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
    - `get_post_shortcodes`
        - Retrieve all shortcodes associated with a user, saving them in a text file
    - `download_posts`
        - Download all posts from an Instagram user
    - `download_faces`
        - Download all cropped faces present in a given user's posts
    - `download_faces_and_colors`
        - Same as `download_faces`, but with the addition of retrieving color palettes from the posts
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
- Image
    - `download`
        - Download an image or video from a url
    - `draw_points_on_image`
        - Draw a set of points on top of an image
    - `write_points_to_disk`
        - Write a list of points to disk
    - `get_points_from_disk`
        - Get points saved through above function
    - `create_collage`
        - Create a collage from a list of images
-  Face
    - `crop_faces`
        - Crop and save all faces in a list of images
    - `crop_eyes`
        - Crop and save all eyes in a list of images
    - `face_match`
        - Compare a list of unknown faces against a known one
    - `get_landmarks`
        - Get 68 facial landmarks from an image
    - `get_5_landmarks`
        - Get 5 facial landmarks from an image
    - `write_landmarks_database`
        - Save a list of 68 facial landmarks as a text file
    - `write_5_landmarks_database`
        - Save a list of 5 facial landmarks as a text file
    - `average_faces`
        - Compute the average of all faces in a directory
