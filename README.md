# cloudburst
a python package for computational design by CONCURRENT STUDIO™

## Installation
For local installation, run `pip3 install -e .`

## Core Functions
Example usage
```python
import cloudburst as cb

# Get all .jpg files in ./images folder
jpgs = cb.query("./images", "jpg")

# Create a list of tuples
tuple_list = [("CONCURRENT", 2), ("STUDIO", 1)]
# Sort list of tuples
sorted_tuple_list = cb.sort_tuples(tuple_list)
```

## Social
Example usage
```python
from cloudburst import social as cbs

# Instantiate Instagram on username "instagram"
ig = cbs.Instagram("instagram")
# Print user's biography
print(ig.biography)
# Download user's profile picture
ig.get_profile_picture()
# Download all of user's posts
ig.get_posts()
```

## Vision
Example usage
```python
from cloudburst import vision as cbv

# Get all .jpg files in ./images folder
jpgs = cb.query("./images", "jpg")

# Crop and save all faces in jpgs
crop_faces(jpgs)
# Crop and save all eyes in jpgs
crop_eyes(jpgs)

# Path to known image
known_image_path = "./known.jpg"
# Return list of True/False values for matches to known photo
matches = face_match(known_image_path, jpgs)
# Print whether or not photo is a path
for idx, match in enumerate(matches):
    print("{} is {}a match".format(jpgs[idx], "not " if match else ""))

# Create and save collage from jpgs
create_collage(1920, 1080, 10, jpgs)
```
