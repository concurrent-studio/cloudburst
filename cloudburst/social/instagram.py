#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Scrape Instagram through its private API """

import json
import requests
import http.client
from datetime import datetime
from urllib.parse import urlencode, parse_qs
from cloudburst import vision as cbv

__all__ = ["Instagram", "download_instagram_by_shortcode"]


def download_post(node, download_data=False):
    node_shortcode = node["shortcode"]
    node_typename = node["__typename"]

    # "caption_is_edited": node["caption_is_edited"],
    # "has_ranked_comments": node["has_ranked_comments"],
    # "is_ad": node["is_ad"],
    data_out = {
        "shortcode": node["shortcode"],
        "typename": node_typename,
        "display_url": node["display_url"],
        "id": node["id"],
        "caption": node["edge_media_to_caption"]["edges"],
        "comments_disabled": node["comments_disabled"],
        "likes": node["edge_media_preview_like"]["count"],
        "location": node["location"],
        "timestamp": node["taken_at_timestamp"],
        "time_string": str(datetime.fromtimestamp(node["taken_at_timestamp"])),
        "media": [],
    }

    if node_typename == "GraphSidecar":
        for idx, node_sidecar in enumerate(node["edge_sidecar_to_children"]["edges"]):
            node_sidecar = node_sidecar["node"]
            node_sidecar_typename = node_sidecar["__typename"]

            media_data = {
                "content_url": "",
                "id": node_sidecar["id"],
                "typename": node_sidecar_typename,
                "dimensions": node_sidecar["dimensions"],
                # "accessibility_caption": node_sidecar["accessibility_caption"],
                "tagged_users": node_sidecar["edge_media_to_tagged_user"]["edges"],
            }

            if node_sidecar_typename == "GraphImage":
                node_url = node_sidecar["display_resources"][-1]["src"]
                media_data["content_url"] = node_url
                cbv.download_image(node_url, "{}_{}.jpg".format(node_shortcode, idx))
            elif node_typename == "GraphVideo":
                node_url = node["video_url"]
                media_data["content_url"] = node_url
                cbv.download_image(node_url, "{}_{}.mp4".format(node_shortcode, idx))

            data_out["media"].append(media_data)

    else:
        media_data = {
            "content_url": "",
            "dimensions": node["dimensions"],
            "tagged_users": node["edge_media_to_tagged_user"]["edges"],
        }

        if node_typename == "GraphImage":
            node_url = node["display_resources"][-1]["src"]
            media_data["content_url"] = node_url
            cbv.download_image(node_url, "{}.jpg".format(node_shortcode))
        elif node_typename == "GraphVideo":
            node_url = node["video_url"]
            media_data["content_url"] = node_url
            cbv.download_image(node_url, "{}.mp4".format(node_shortcode))

        data_out["media"].append(media_data)

    if download_data:
        with open("{}.json".format(node_shortcode), "w") as f:
            f.write(json.dumps(data_out, indent=4))


def download_instagram_by_shortcode(shortcode):
    """Download media and data from a posed given its shortcode

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
    # Retrieve JSON data for post
    data_url = "https://www.instagram.com/p/{}/?__a=1".format(shortcode)
    data = json.loads(requests.get(data_url).text)["graphql"]["shortcode_media"]
    download_post(data, True)


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
        page_data = json.loads(requests.get(data_url).text)["graphql"]["user"]

        # Profile data gathered upon instantiation
        self.username = username
        self.id = page_data["id"]
        self.full_name = page_data["full_name"]
        self.biography = page_data["biography"]
        self.external_url = page_data["external_url"]
        self.follower_count = page_data["edge_followed_by"]["count"]
        self.following_count = page_data["edge_follow"]["count"]
        self.has_ar_effects = page_data["has_ar_effects"]
        self.has_channel = page_data["has_channel"]
        self.has_blocked_viewer = page_data["has_blocked_viewer"]
        self.highlight_reel_count = page_data["highlight_reel_count"]
        self.has_requested_viewer = page_data["has_requested_viewer"]
        self.is_business_account = page_data["is_business_account"]
        self.business_category_name = page_data["business_category_name"]
        self.category_id = page_data["category_id"]
        self.overall_category_name = page_data["overall_category_name"]
        self.is_joined_recently = page_data["is_joined_recently"]
        self.is_private = page_data["is_private"]
        self.is_verified = page_data["is_verified"]
        self.profile_pic_url_hd = page_data["profile_pic_url_hd"]
        self.connected_fb_page = page_data["connected_fb_page"]
        self.media_count = self.__instagram_query(
            "d496eb541e5c789274548bf473cc553e", {"id": self.id, "first": 1,}
        )["data"]["user"]["edge_owner_to_timeline_media"]["count"]

    @staticmethod
    def __instagram_query(hash, variables):
        query_url = "https://www.instagram.com/graphql/query/?{}".format(
            urlencode(
                {
                    "query_hash": hash,
                    "variables": json.dumps(variables, separators=(",", ":")),
                }
            )
        )
        page_data = json.loads(requests.get(query_url).text)
        return page_data

    def download_profile_picture(self):
        """Download an Instagram user's profile picure in its highest quality"""
        cbv.download_image(self.profile_pic_url_hd, "{}.jpg".format(self.id))

    def get_following(self):
        """Get all users that someone is followign"""
        following = []
        end_cursor = ""
        count = 0
        while count < self.following_count:
            response = self.__instagram_query(
                "d04b0a864b4b54837c0d870b0e77e076",
                {"id": self.id, "include_reel": True, "fetch_mutual": False, "first": 24, "after": end_cursor},
            )
            print(response)

            # end_cursor = response["data"]["user"]["edge_follow"]["page_info"]["end_cursor"]
            # edges = response["data"]["user"]["edge_follow"]["edges"]
            # for node in edges:
            #     following.append(node["username"])
            #     print(node["username"])
            #     count += 1
            

    def download_posts(self, download_data=False):
        """Download all posts from an Instagram user in their highest quality

        Parameters
        ----------
        download_data : bool
            download post data as well as media
        """
        end_cursor = ""
        count = 0
        while count < self.media_count:
            response = self.__instagram_query(
                "d496eb541e5c789274548bf473cc553e",
                {"id": self.id, "first": 50, "after": end_cursor},
            )

            end_cursor = response["data"]["user"]["edge_owner_to_timeline_media"][
                "page_info"
            ]["end_cursor"]
            edges = response["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
            for node in edges:
                download_post(node["node"], download_data)
                count += 1
            print(count/self.media_count)
