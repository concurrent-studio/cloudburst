# cloudburst ⛈
[![CircleCI](https://circleci.com/gh/concurrent-studio/cloudburst.svg?style=shield)](https://circleci.com/gh/concurrent-studio/cloudburst)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/4bb39fbbdf594ef5915003e824c323ef)](https://www.codacy.com/gh/concurrent-studio/cloudburst?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=concurrent-studio/cloudburst&amp;utm_campaign=Badge_Grade)
[![Documentation](https://img.shields.io/badge/docs-reference-brightgreen.svg)](https://concurrent-studio.github.io/cloudburst/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

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

## ⚠️  IMPLEMENT THESE FEATURES
- NLP, text cleaning and scraping [tds](https://towardsdatascience.com/nlp-for-beginners-cleaning-preprocessing-text-data-ae8e306bef0f)
- Lyric scraping [genius](https://towardsdatascience.com/nlp-for-beginners-cleaning-preprocessing-text-data-ae8e306bef0f) 

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
- `query`
    - Query a folder by filename extension
- `sort_tuples`
    - Sort a list of tuples by their second element

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
    - `download_posts`
        - Download all posts from an Instagram user
- `download_instagram_by_shortcode`
    - Download media and data from a posed given its shortcode 

#### 📹 Vision
##### Usage
```python
from cloudburst import vision as cbv
```

##### Components
- `download_image`
    - Download an image from a url
- `create_collage`
    - Create a collage from a list of images
- `crop_faces`
    - Crop and save all faces in a list of images
- `crop_eyes`
    - Crop and save all eyes in a list of images
- `face_match`
    - Compare a list of unknown faces against a known one
