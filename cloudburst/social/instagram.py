# -*- coding: utf-8 -*-
""" Scrape Instagram through its private API """
import math
import json
import os
import requests
import http.client
from datetime import datetime
from pathlib import Path
from PIL import Image
from tqdm import tqdm
from urllib.parse import urlencode, parse_qs
from cloudburst.core import concurrent, write_list_to_file, get_list_from_file, mkdir
from cloudburst.vision.colors import get_colors
from cloudburst.vision.image import download
from cloudburst.vision.face import crop_faces

__all__ = ["Instagram", "download_instagram_by_shortcode"]


def _download_post(node, only_images=False):
    """Download an instagram post (private method)

    Parameters
    ----------
    node : dictionary
        json data from instagram's public api

    Return
    ------
    saved : list
        list of saved posts in the form (shortcode, id)

    Notes
    -----
    Posts saved in the format [shortcode]_[id].[extension] such that their source can be easily retrieved and sidecar posts don't overwrite themselves
    """
    # Post type
    typename = node["__typename"]
    # Post shortcode
    shortcode = node["shortcode"]
    # Post id
    post_id = node["id"]
    # List of saved posts
    saved = []

    # Handle sidecar (multi-content posts)
    if typename == "GraphSidecar":
        # Download each element in sidecar
        for node_sidecar in node["edge_sidecar_to_children"]["edges"]:
            sidecar = node_sidecar["node"]
            sidecar_typename = sidecar["__typename"]
            sidecar_id = sidecar["id"]
            
            # Append id to list of downloaded ids
            saved.append((shortcode, sidecar_id))

            # Download sidecar image
            if sidecar_typename == "GraphImage":
                download(sidecar["display_resources"][-1]["src"], "{}_{}.jpg".format(shortcode, sidecar_id))
            
            # Download sidecar video
            elif sidecar_typename == "GraphVideo":
                if only_images:
                    download(sidecar["display_url"], "{}_{}.jpg".format(shortcode, sidecar_id))
                else:
                    download(sidecar["video_url"], "{}_{}.mp4".format(shortcode, sidecar_id))

    # Handle image
    elif typename == "GraphImage":
        saved.append((shortcode, post_id))
        download(node["display_resources"][-1]["src"], "{}_{}.jpg".format(shortcode, post_id))

    # Handle video
    elif typename == "GraphVideo":
        saved.append((shortcode, post_id))
        if only_images:
            download(node["display_url"], "{}_{}.jpg".format(shortcode, post_id))
        else:
            download(node["video_url"], "{}_{}.mp4".format(shortcode, post_id))

    # return list of tuples in form (shortcode, id)
    return saved

def download_instagram_by_shortcode(shortcode, only_images=False):
    """Download an instagram post from its shortcode

    Parameters
    ----------
    shortcode : str
        shortcode from an Instagram post; see glossary for definition

    Examples
    --------
    Download the Instagram post "https://www.instagram.com/p/B-X0DDrj30s/"

    .. code-block:: python
       from cloudburst import social as cbs

       cbs.download_instagram_by_shortcode("B-X0DDrj30s")
    """
    # Full url with shortcode
    url = "https://www.instagram.com/p/{}/".format(shortcode)
    try:
        # Get data
        data = json.loads(requests.get("{}?__a=1".format(url)).text)["graphql"]["shortcode_media"]
        return _download_post(data, only_images=only_images)

    except:
        # Print error if one occured along the way
        print("Error: could not download post {}".format(url))
        return None

class Instagram:
    """Scrape the data of an Instagram User

    Attributes
    ----------
    username : str
        User's username
    id : str
        User's unique ID
    full_name : str
        User's full name
    biography : str
        User's biography
    external_url : str
        Linked site under user's biography
    follower_count : int
        Number of accounts following the user
    following_count : int
        Number of accounts user is following
    has_ar_effects : bool
        Does the account have any augmented reality effects
    has_channel : bool
        ?
    has_blocked_viewer : bool
        Has the account blocked any viewers
    highlight_reel_count : int
        Number of highlight reels owned by user
    has_requested_viewer : bool
        ?
    is_business_account : bool
        Is it a business account
    business_category_name : str
        Name of business category
    category_id : str
        ID of business category
    overall_category_name : str
        Name of overall category
    is_joined_recently : bool
        Did the user join recently
    is_private : bool
        Is the account private
    is_verified : bool
        Is the account verified
    profile_pic_url_hd : str
        URL to high defintion profile picture
    connected_fb_page : str
        Connected Facebook page
    media_count : int
        Number of posts by user

    Examples
    --------
    Contruct new object for @pharrell, print bio, download profile image, download all media and data

    .. code-block:: python

       from cloudburst import social as cbs

       pharrell = cbs.Instagram("pharrell") # instantiate new Instagram object
       print(pharrell.bio) # print bio
       pharrell.download_profile_picture() # download HD profile image
       pharrell.download_posts(True) # download all posts and media
    """

    def __init__(self, username):
        """Constructor method

        Parameters
        ----------
        username : str
            any Instagram user's username
        """
        # Retrieve JSON profile for user
        data_url = "https://www.instagram.com/{}/?__a=1".format(username)
        data = json.loads(requests.get(data_url).text)["graphql"]["user"]

        # Profile data gathered upon instantiation
        self.username = username
        self.id = data["id"]
        self.full_name = data["full_name"]
        self.biography = data["biography"]
        self.external_url = data["external_url"]
        self.follower_count = data["edge_followed_by"]["count"]
        self.following_count = data["edge_follow"]["count"]
        self.has_ar_effects = data["has_ar_effects"]
        self.has_channel = data["has_channel"]
        self.has_blocked_viewer = data["has_blocked_viewer"]
        self.highlight_reel_count = data["highlight_reel_count"]
        self.has_requested_viewer = data["has_requested_viewer"]
        self.is_business_account = data["is_business_account"]
        self.business_category_name = data["business_category_name"]
        self.category_id = data["category_id"]
        self.overall_category_name = data["overall_category_name"]
        self.is_joined_recently = data["is_joined_recently"]
        self.is_private = data["is_private"]
        self.is_verified = data["is_verified"]
        self.profile_pic_url_hd = data["profile_pic_url_hd"]
        self.connected_fb_page = data["connected_fb_page"]
        self.media_count = self.__instagram_query("d496eb541e5c789274548bf473cc553e", {"id": self.id, "first": 1,})["data"]["user"]["edge_owner_to_timeline_media"]["count"]

    @staticmethod
    def __instagram_query(hash, variables):
        """Run a graphql instagram through instagram's public graphql access point"""
        query_url = "https://www.instagram.com/graphql/query/?{}".format(
            urlencode(
                {
                    "query_hash": hash,
                    "variables": json.dumps(variables, separators=(",", ":")),
                }
            )
        )
        try:
            # If successful, load data
            data = json.loads(requests.get(query_url).text)
        except:
            # If unsuccessful, return None
            data = None
        return data

    def download_profile_picture(self):
        """Download an Instagram user's profile picure in its highest quality"""
        download(self.profile_pic_url_hd, "{}_{}.jpg".format(self.username, self.id))
            
    def get_post_shortcodes(self, display_progress=True):
        """Download all posts from an Instagram user in their highest quality
        
        Parameters
        ----------
        display_progress : bool
            Display progress of shortcode retrieval
        """
        # List of shortcodes
        shortcode_list = []

        # Make graphql queries until all shortcodes are gathered
        end_cursor = ""
        count = 0
        while count < self.media_count:
            response = self.__instagram_query(
                "d496eb541e5c789274548bf473cc553e",
                {"id": self.id, "first": 50, "after": end_cursor},
            )
            if response:
                end_cursor = response["data"]["user"]["edge_owner_to_timeline_media"][
                    "page_info"
                ]["end_cursor"]
                edges = response["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
                
                for node in edges:
                    shortcode_list.append(node["node"]["shortcode"])
                    if display_progress:
                        print(" Retreived {}% of @{}'s posts".format(round(100*count/self.media_count, 2), self.username), end="\r", flush=True)
                    count += 1

        return shortcode_list

    def download_posts(self, display_progress=True):
        """Download all posts from an Instagram user in their highest quality

        Parameters
        ----------
        display_progress : bool
            Display progress of post download
        """
        # Check whether shortcodes have already been saved
        shortcode_filename = "{}_shortcode_list.txt".format(self.username)
        if Path(shortcode_filename).is_file():
            shortcode_list = get_list_from_file(shortcode_filename)
        else:
            # Retrieve shortcodes
            shortcode_list = self.get_post_shortcodes(display_progress)
            write_list_to_file(shortcode_filename, shortcode_list)
        
        concurrent(download_instagram_by_shortcode, shortcode_list, progress_bar=display_progress)
    
    def download_faces(self, display_progress=True):
        """Download all faces from an Instagram user in their highest quality

        Parameters
        ----------
        display_progress : bool
            Display progress of post download
        """
        # Function to crop and download faces in a post, then delete the original image
        def _get_faces_by_shortcode(shortcode):
            for media_shortcode, media_id in download_instagram_by_shortcode(shortcode, only_images=True):
                try:
                    filename = "{}_{}.jpg".format(media_shortcode, media_id)
                    crop_faces(filename)
                    os.remove(filename)
                except:
                    pass
        
        # Check whether shortcodes have already been saved
        shortcode_filename = "{}_shortcode_list.txt".format(self.username)
        if Path(shortcode_filename).is_file():
            shortcode_list = get_list_from_file(shortcode_filename)
        else:
            # Retrieve shortcodes
            shortcode_list = self.get_post_shortcodes(display_progress)
            write_list_to_file(shortcode_filename, shortcode_list)
        
        concurrent(_get_faces_by_shortcode, shortcode_list, progress_bar=display_progress)

    def download_faces_and_colors(self, color_count=1, display_progress=True):
        """Download all faces and predominant color of each post from an Instagram user in their highest quality

        Parameters
        ----------
        color_count : int
            Number of colors to grab from each image
        display_progress : bool
            Display progress of post download
        """
        # List of predominant colors in posts
        colors = []
    
        # Function to crop and download faces in a post, then delete the original image
        def _get_faces_and_colors_by_shortcode(shortcode):
            for media_shortcode, media_id in download_instagram_by_shortcode(shortcode, only_images=True):
                try:
                    filename = "{}_{}.jpg".format(media_shortcode, media_id)
                    colors.append(get_colors(filename, color_count=color_count))
                    crop_faces(filename)
                    os.remove(filename)
                except:
                    pass
        
        # Check whether shortcodes have already been saved
        shortcode_filename = "{}_shortcode_list.txt".format(self.username)
        if Path(shortcode_filename).is_file():
            shortcode_list = get_list_from_file(shortcode_filename)
        else:
            # Retrieve shortcodes
            shortcode_list = self.get_post_shortcodes(display_progress)
            write_list_to_file(shortcode_filename, shortcode_list)
        
        # Crop Faces
        face_dir = mkdir("faces")
        os.chdir(face_dir)
        concurrent(_get_faces_and_colors_by_shortcode, shortcode_list, progress_bar=display_progress)
        os.chdir(face_dir.parent)
        # Write color list to file
        write_list_to_file("{}_colors.txt".format(self.username), colors)
        # Write color list to image
        s = math.floor(math.sqrt(2*len(colors)))
        if s%2 != 0:
            s = s-1
        pixel_count = int((s**2/2))
        img = Image.new("RGB", (int(s/2), s))
        img.putdata(colors[0:pixel_count-1])
        img.save("{}_colors.jpg".format(self.username))