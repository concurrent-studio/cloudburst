# cloudburst ⛈
a python package for computational design by [CONCURRENT STUDIO™](https://www.concurrent.studio)

[![License: CC BY-NC-SA 4.0](https://licensebuttons.net/l/by-nc-sa/4.0/80x15.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

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

## 📦 Modules + Submodules
### 🛠 Core Functions
#### Usage
```python
import cloudburst as cb
```

#### Components
- `query`
    - Query a folder by filename extension
- `sort_tuples`
    - Sort a list of tuples by their second element

### 📱 Social
#### Usage
```python
from cloudburst import social as cbs
```

#### Components
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

### 📹 Vision
#### Usage
```python
from cloudburst import vision as cbv
```

#### Components
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