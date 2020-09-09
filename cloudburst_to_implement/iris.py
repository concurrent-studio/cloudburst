import os
import cloudburst as cb
from cloudburst import social as cbs
from cloudburst import vision as cbv
from glob import glob

# pseudo code
# get all links to post
# get a link
    # get all faces
    # rotate and save
# resize all faces and combine into average

class IRIS:
    def __init__(self, username):
        self.username = username
        self.shortcodes = []

    # Download and analyze each post
    def get_faces_in_post(self, shortcode):
        for s, i in cbs.download_instagram_by_shortcode(shortcode):
            try:
                filename = "{}_{}.jpg".format(s, i)
                if self.cropfaces:
                    cbv.crop_faces(filename)
                os.remove(filename)
            except:
                print("error at {} {}".format(i, shortcode))

    def execute(self, cropfaces=True):
        self.cropfaces = cropfaces

        # Get all post shortcodes
        shortcode_filename = "{}_shortcode_list.txt".format(self.username)
        if glob("{}_shortcode_list.txt".format(self.username)) != []:
            self.shortcodes = [line.rstrip('\n') for line in open(shortcode_filename)]
        else:
            print("Fetching posts from instagram")
            self.shortcodes = cbs.Instagram(self.username).get_post_shortcodes()
            cb.write_list_to_file(shortcode_filename, self.shortcodes)
        
        cb.concurrent(self.get_faces_in_post, self.shortcodes, executor="threadpool", progress_bar=True)
        cb.write_list_to_file("{}.txt".format(self.username), self.color_list)

IRIS("charlotteslawrence").execute()

