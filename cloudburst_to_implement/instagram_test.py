import cloudburst as cb
from cloudburst import social as cbs

bella = cbs.Instagram("bellahadid") # instantiate new Instagram object
shortcodes = bella.download_profile_picture() # download HD profile image
shortcodes = bella.download_posts() # download all posts
