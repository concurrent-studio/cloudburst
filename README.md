# cloudburst ⛈
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![PyPI](https://img.shields.io/pypi/v/cloudburst)

A cloudburst of data, gathered through scraping 


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
For further information, see the [usage guide](https://concurrent-studio.github.io/cloudburst/).

## To Do
https://github.com/google/portrait-shadow-manipulation.git
https://github.com/sylnsfar/qrcode

### 📦 Modules + Submodules
#### 🛠 Core Functions
##### Usage
```python
import cloudburst as cb
```

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

       - Create a collage from a list of images

