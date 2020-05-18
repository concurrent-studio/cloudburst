# -*- coding: utf-8 -*-
""" Scrape Instagram through its GraphQL API """
import json
import pickle
import requests
from binascii import a2b_base64
from datetime import datetime
from getpass import getpass
from io import BytesIO
from pathlib import Path
from string import ascii_letters, digits, punctuation
from time import time, sleep
from urllib.parse import urlencode
from PIL import Image
from cloudburst.core import (
    concurrent,
    write_dict_to_file,
    get_dict_from_file,
    mkdir,
    query,
)
from cloudburst.vision import download

__all__ = ["Instagram", "download_instagram_by_shortcode"]


def download_instagram_by_shortcode(shortcode):
    """Download a post from its shortcode

    Parameters
    ----------
    shortcode : str
        shortcode from an Instagram post; see glossary for definition

    Examples
    --------
    Download the Instagram post "https://www.instagram.com/p/B-X0DDrj30s/"

    >>> from cloudburst import social as cbs
    >>> cbs.download_instagram_by_shortcode("B-X0DDrj30s")
    """
    def __download_media(shortcode, node):
        """ Download a post's media """
        filename = "{}_{}".format(shortcode, node["id"])
        # Get content based on typename
        if node["__typename"] == "GraphImage":
            content_url = node["display_resources"][-1]["src"]
            # Check to ensure content isn't gone from Facebook's CDN
            if requests.get(content_url).text != "Gone":
                download(content_url, "{}.jpg".format(filename))
        elif node["__typename"] == "GraphVideo":
            content_url = node["video_url"]
            # Check to ensure content isn't gone from Facebook's CDN
            if requests.get(content_url).text != "Gone":
                download(content_url, "{}.jpg".format(filename))
            download(content_url, "{}.mp4".format(filename))
        else:
            pass

    # Full url with shortcode
    url = "https://www.instagram.com/p/{}/".format(shortcode)
    try:
        # Get data
        data = json.loads(requests.get("{}?__a=1".format(url)).text)["graphql"][
            "shortcode_media"
        ]
        if data["__typename"] == "GraphSidecar":
            # Iterate through individual media in sidecar
            for node in data["edge_sidecar_to_children"]["edges"]:
                __download_media(shortcode, node["node"])
        else:
            __download_media(shortcode, data)
    except:
        # Print error if one occured along the way
        print("Error: could not download post {}".format(url))


class Instagram:
    """Scrape the data of an Instagram User

    Attributes
    ----------
    username : str
        User's username
    id : str
        User's unique ID
    name : str
        User's full name
    biography : str
        User's biography
    url : str
        Linked site under user's biography
    followers : int
        Number of accounts following the user
    following : int
        Number of accounts user is following
    business_category_name : str
        Name of business category
    category_id : str
        ID of business category
    overall_category_name : str
        Name of overall category
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
    timestamp : int
        Current UNIX epoch timestamp
    shortcode_list : list
        List of all shortcodes for a user

    Examples
    --------
    Contruct new object for @denimtears, gather media, do some analytics
    
    >>> from cloudburst import social as cbs
    >>> ig = cbs.Instagram("denimtears") # Build pseudo-database for user
    >>> ig.download_profile_picture()
    >>> ig.get_previews()
    >>> ig.download_stories()
    >>> ig.download_highlights()
    >>> ig.download_thumbnails()
    >>> ig.download_posts()
    >>> print(f"First post: https://www.instagram.com/p/{ig.get_post_by_number(-1)}")
    >>> print("Querying for keyword \"acyde\":")
    >>> for shortcode, _ in ig.search_captions_by_keyword("acyde"):
    >>>     print(f"\thttps://www.instagram.com/p/{shortcode}")
    >>> print(f"Top tagged user: {ig.get_tagged_users()[0][0]}")
    >>> print(f"Top tagged users in captions: {ig.get_tagged_users_in_captions()[0][0]}")
    >>> print(f"Top hashtag: {ig.get_hashtags()[0][0]}")
    >>> top_liked_post = ig.get_posts_by_like_count()[0]
    >>> print(f"Most liked post: https://www.instagram.com/p/{top_liked_post[0]} ({top_liked_post[1]} likes)")
    >>> print(f"Total lifetime likes: {ig.get_lifetime_like_count()}")
    """

    def __init__(self, username):
        """Constructor method

        Parameters
        ----------
        username : str
            Any Instagram user's username to query
        """
        # Create ~/.cloudubrst directory if necessary
        # Used to store session
        mkdir(Path.home().joinpath(".cloudburst"))

        # Login user
        self.cache_file = Path.home().joinpath(".cloudburst/instagram_session.dat")
        self.useragent = "Instagram 123.0.0.21.114 (iPhone; CPU iPhone OS 11_4 like Mac OS X; en_US; en-US; scale=2.00; 750x1334) AppleWebKit/605.1.15"
        self.session = requests.Session()
        self.session.headers = {"user-agent": self.useragent}
        self.session.cookies.set("ig_pr", "1")
        self.cookies = None
        self.is_logged_in = False
        self.__login()

        # Try to joad JSON file for user
        self.json = get_dict_from_file("{}.json".format(username))
        # Get current UNIX epoch timestamp for record keeping purposes
        self.timestamp = int(time())
        # If the file can't be found
        if self.json == None:
            # Retrieve JSON profile for user
            data = self.__a_query(username, login_required=True)["graphql"]["user"]

            # Gather profile data
            self.username = username
            self.id = data["id"]
            self.name = data["full_name"]
            self.biography = data["biography"]
            self.url = data["external_url"]
            self.following = data["edge_follow"]["count"]
            self.followers = data["edge_followed_by"]["count"]
            self.media_count = self.__graphql_query(
                "d496eb541e5c789274548bf473cc553e", {"id": self.id, "first": 1,}
            )["data"]["user"]["edge_owner_to_timeline_media"]["count"]
            self.profile_pic = data["profile_pic_url_hd"]
            self.private = data["is_private"]
            self.verified = data["is_verified"]
            self.overall_category_name = data["overall_category_name"]
            self.business_category_name = data["business_category_name"]
            self.category_id = data["category_id"]
            self.connected_facebook = data["connected_fb_page"]

            # Fill JSON file with profile data
            self.json = {
                "profile": {
                    "username": self.username,
                    "id": self.id,
                    "name": self.name,
                    "biography": self.biography,
                    "url": self.url,
                    "following": self.following,
                    "followers": self.followers,
                    "media count": self.media_count,
                    "profile pic": self.profile_pic,
                    "private": self.private,
                    "verified": self.verified,
                    "business": {
                        "overall category": self.overall_category_name,
                        "category name": self.business_category_name,
                        "category id": self.category_id,
                    },
                    "facebook": self.connected_facebook,
                    "changes": {
                        self.timestamp: {
                            "name": self.name,
                            "biography": self.biography,
                            "url": self.url,
                            "following": self.following,
                            "followers": self.followers,
                            "profile pic": self.profile_pic,
                            "private": self.private,
                            "verified": self.verified,
                            "business": {
                                "overall category": self.overall_category_name,
                                "category name": self.business_category_name,
                                "category id": self.category_id,
                            },
                            "facebook": self.connected_facebook,
                        }
                    },
                },
                "posts": [],
                "stories": [],
                "highlights": [],
                "meta": {"created at": self.timestamp},
            }

            # Get post shortcodes and fill posts with scaffold
            self.shortcode_list = self.__get_post_shortcodes()
            # No posts recorded for initial scaffold build
            self.recorded_list = []
            self.__build_post_scaffold()
            self.__populate_post_scaffold()
            self.story_ids = []
            self.highlight_ids = []
            self.__get_stories()
            self.__get_highlights()
            # Write JSON file to disk without spacing/indents
            write_dict_to_file(
                "{}.json".format(self.username), self.json, minimize=True
            )

        # If JSON file exists, read it into class attributes
        else:
            # Profile data gathered upon instantiation
            self.username = self.json["profile"]["username"]
            self.id = self.json["profile"]["id"]
            self.name = self.json["profile"]["name"]
            self.biography = self.json["profile"]["biography"]
            self.url = self.json["profile"]["url"]
            self.following = self.json["profile"]["following"]
            self.followers = self.json["profile"]["followers"]
            self.media_count = self.json["profile"]["media count"]
            self.profile_pic = self.json["profile"]["profile pic"]
            self.private = self.json["profile"]["private"]
            self.verified = self.json["profile"]["verified"]
            self.overall_category_name = self.json["profile"]["business"][
                "overall category"
            ]
            self.business_category_name = self.json["profile"]["business"][
                "category name"
            ]
            self.category_id = self.json["profile"]["business"]["category id"]
            self.connected_facebook = self.json["profile"]["facebook"]

            # Check for changes in profile, ignore unchangeable params
            changes = {}
            write_changes = True
            data = self.__a_query(username, login_required=True)["graphql"]["user"]
            if self.name != data["full_name"]:
                self.json["profile"]["name"] = data["full_name"]
                changes.update({"name": data["full_name"]})
            elif self.biography != data["biography"]:
                self.json["profile"]["biography"] = data["biography"]
                changes.update({"biography": data["biography"]})
            elif self.url != data["external_url"]:
                self.json["profile"]["url"] = data["external_url"]
                changes.update({"url": data["external_url"]})
            elif self.following != data["edge_follow"]["count"]:
                self.json["profile"]["following"] = data["edge_follow"]["count"]
                changes.update({"following": data["edge_follow"]["count"]})
            elif self.followers != data["edge_followed_by"]["count"]:
                self.json["profile"]["followers"] = data["edge_followed_by"]["count"]
                changes.update({"followers": data["edge_followed_by"]["count"]})
            elif self.profile_pic != data["profile_pic_url_hd"]:
                self.json["profile"]["profile_pic"] = data["profile_pic_url_hd"]
                changes.update({"profile pic": data["profile_pic_url_hd"]})
            elif self.private != data["is_private"]:
                self.json["profile"]["private"] = data["is_private"]
                changes.update({"private": data["is_private"]})
            elif self.verified != data["is_verified"]:
                self.json["profile"]["verified"] = data["is_verified"]
                changes.update({"verified": data["is_verified"]})
            elif self.business_category_name != data["business_category_name"]:
                self.json["profile"]["business"]["category name"] = data[
                    "business_category_name"
                ]
                changes.update(
                    {"business category name": data["business_category_name"]}
                )
            elif self.category_id != data["category_id"]:
                self.json["profile"]["business"]["category id"] = data["category_id"]
                changes.update({"business category id": data["category_id"]})
            elif self.overall_category_name != data["overall_category_name"]:
                self.json["profile"]["business"]["overall category"] = data[
                    "overall_category_name"
                ]
                changes.update(
                    {"business overall category": data["overall_category_name"]}
                )
            elif self.connected_facebook != data["connected_fb_page"]:
                self.json["profile"]["facebook"] = data["connected_fb_page"]
                changes.update({"facebook": data["connected_fb_page"]})
            else:
                print("No changes to profile detected")
                write_changes = False

            # If changes are detected, write them to JSON file
            if write_changes:
                self.json["profile"]["changes"].update({self.timestamp: changes})
                write_dict_to_file(
                    "{}.json".format(self.username), self.json, minimize=True
                )

            # Check if number of recorded posts are equivalent to number of posted posts
            if (
                len(self.json["posts"])
                != self.__graphql_query(
                    "d496eb541e5c789274548bf473cc553e", {"id": self.id, "first": 1,}
                )["data"]["user"]["edge_owner_to_timeline_media"]["count"]
            ):
                # Currently recorded posts
                self.recorded_list = [
                    post["shortcode"] for post in self.json["posts"] if post is not None
                ]
                # Udpate shortcode list
                self.shortcode_list = self.__get_post_shortcodes()
                # Add shortcodes to json["posts"] and write to disk
                self.__build_post_scaffold()
            else:
                self.shortcode_list = [post["shortcode"] for post in self.json["posts"]]

            self.__populate_post_scaffold()
            # Get story list
            self.story_ids = [story_id["id"] for story_id in self.json["stories"]]
            self.highlight_ids = [
                highlight_id["id"] for highlight_id in self.json["highlights"]
            ]
            self.__get_stories()
            self.__get_highlights()
            write_dict_to_file(
                "{}.json".format(self.username), self.json, minimize=True
            )
        self.__cache_session()

    ########################
    # LOGIN/LOGOUT METHODS #
    ########################
    def __login(self):
        """ Log into Instagram """
        cached_session_found = False
        if self.cache_file.exists():
            # Only load file if it was modified less than an hour ago
            if (
                datetime.now() - datetime.fromtimestamp(self.cache_file.stat().st_mtime)
            ).seconds < 3600:
                with open(self.cache_file, "rb") as f:
                    # Load session from file
                    self.session = pickle.load(f)
                    cached_session_found = True
                    print("Session loaded from cache\n")

        # If no valid cache found, create new session
        if not cached_session_found:
            # Prompt user for login username and password
            self.login_username = input("Username: ")
            self.login_password = getpass("Password: ")

            # Attempt login
            self.session.headers.update(
                {"Referer": "https://www.instagram.com/", "user-agent": self.useragent}
            )
            self.session.headers.update(
                {
                    "X-CSRFToken": self.session.get(
                        "https://www.instagram.com/"
                    ).cookies["csrftoken"]
                }
            )
            login = self.session.post(
                "https://www.instagram.com/accounts/login/ajax/",
                data={"username": self.login_username, "password": self.login_password},
                allow_redirects=True,
            )
            self.session.headers.update({"X-CSRFToken": login.cookies["csrftoken"]})
            self.cookies = login.cookies
            login_response = json.loads(login.text)

            # Check if login succeeded
            if login_response.get("authenticated") and login.status_code == 200:
                self.is_logged_in = True
                self.session.headers.update({"user-agent": self.useragent})
            # Display errors if necessary
            else:
                if "two_factor_required" in login_response:
                    # This needs to be done
                    print("Error: two-factor authentication not yet implemented.")
                elif "error_type" in login_response:
                    error_type = login_response["error_type"]
                    if error_type == "rate_limit_error":
                        print(
                            f"Error: login failed for user @{self.login_username} because of rate limiting"
                        )
                        print("Sleeping for 2 minutes and retrying")
                        sleep(120)
                        self.__login()
                    else:
                        print(
                            f"Error: login failed for user @{self.login_username} with error {error_type}"
                        )
                else:
                    print(f"Error: login failed for user @{self.login_username}")
                print("Exiting program")
                quit(0)

            # Cache session so unnecessary logins avoided
            self.__cache_session()

    def __logout(self):
        """ Log out of Instagram """
        # Only logout if logged in
        if self.is_logged_in:
            try:
                self.session.post(
                    "https://www.instagram.com/accounts/logout/",
                    data={"csrfmiddlewaretoken": self.cookies["csrftoken"]},
                )
                self.is_logged_in = False
            except requests.exceptions.RequestException:
                print("Error: logout failed")

    def __cache_session(self):
        """ Cache session to prevent unnecessary logins """
        with open(self.cache_file, "wb") as f:
            pickle.dump(self.session, f)
            print("Session cache file updated")

    ##################
    # STATIC METHODS #
    ##################
    @staticmethod
    def __download_tuple(tuple):
        """ Helper method/workaround to allow for concurrent downloading of images 
        
        Parameters
        ----------
        tuple : tuple
            Tuple or url and filename to deconstruct
        """
        # Check to ensure content isn't gone from Facebook's CDN
        if requests.get(tuple[0]).text != "Gone":
            download(tuple[0], tuple[1])

    @staticmethod
    def __media_preview_to_image(media_preview):
        """ Transform a media_preview string into a PIL Image through Instagram's proprietary compression algorithm 
    
        Parameters
        ----------
        media_preview : string
            Instagram media preview string

        Returns
        -------
        image : Image
            Turn media preview string into PIL Image
        """
        # Base64 to bytes
        preview_binary = [i for i in a2b_base64(media_preview)]
        # Common header to bytes
        header = [
            i
            for i in list(
                a2b_base64(
                    "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEABsaGikdKUEmJkFCLy8vQkc/Pj4/R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0cBHSkpNCY0PygoP0c/NT9HR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//AABEIABQAKgMBIgACEQEDEQH/xAGiAAABBQEBAQEBAQAAAAAAAAAAAQIDBAUGBwgJCgsQAAIBAwMCBAMFBQQEAAABfQECAwAEEQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+gEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoLEQACAQIEBAMEBwUEBAABAncAAQIDEQQFITEGEkFRB2FxEyIygQgUQpGhscEJIzNS8BVictEKFiQ04SXxFxgZGiYnKCkqNTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqCg4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1tre4ubrCw8TFxsfIycrS09TV1tfY2dri4+Tl5ufo6ery8/T19vf4+fr/2gAMAwEAAhEDEQA/AA=="
                )
            )
        ]
        header[162], header[160] = preview_binary[1:3]
        # Encode data to bytes from ISO-8859-1 codec
        data = "".join([chr(i) for i in header + preview_binary[3:]]).encode(
            "iso-8859-1"
        )
        # Create PIL Image from data
        image = Image.open(BytesIO(data))

        return image

    @staticmethod
    def __strip_hashtag(hashtag):
        """ Remove extraneous octothorpes and other punctuation from hashtags 
        
        Parameters
        ----------
        hashtag : string
            Hashtag to strip

        Returns
        -------
        hashtag : string
            Properly stripped hashtag
        """
        try:
            while hashtag[1] == "#":
                hashtag = hashtag[1:]
        except:
            pass
        try:
            while hashtag[-1] in list(punctuation):
                hashtag = hashtag[:-1]
        except:
            pass

        return hashtag

    @staticmethod
    def __strip_username(username):
        """ Remove extraneous octothorpes and other punctuation from hashtags 
        
        Parameters
        ----------
        username : string
            Username to strip

        Returns
        -------
        username : string
            Properly stripped username
        """
        try:
            while username[-1] not in list(ascii_letters + digits + "._"):
                username = username[:-1]
            return username
        except:
            return None

    ######################################
    # METHODS FOR BUILDING JSON DATABASE #
    ######################################
    def __a_query(self, query, login_required=True):
        """ Run a query through Instagram's "?__a=1" initial page-loading method 

        Returns
        -------
        data : dict
            JSON data from ?__a=1 query
        """
        query_count = 0
        max_queries_allowed = 2

        def __execute_a_query(query_url):
            try:
                # Load data from query, using either logged in, or publically accessible page
                if login_required:
                    return json.loads(self.session.get(query_url).text)
                else:
                    return json.loads(requests.get(query_url).text)
            except:
                # If unsuccessful, try again, up to max attempt number
                query_count += 1
                if query_count <= max_queries_allowed + 1:
                    print(f"Error: couldn't retrieve data @ {query_url}. Retrying.")
                    __a_query(query_url)
                else:
                    print(f"Error: couldn't retrieve data @ {query_url}. Passing.")
                    return None

        # Form query url and exexcute query
        query_url = "https://www.instagram.com/{}/?__a=1".format(query)
        data = __execute_a_query(query_url)

        return data

    def __graphql_query(self, hash, variables):
        """ Run a query through Instagram's GraphQL infrastructure 

        Parameters
        ----------
        hash : string
            GraphQL hash for query
        variables : dict
            Dictionary of variables to include in query

        Returns
        -------
        data : dict
            JSON data from GraphQL query
        """
        sleep_time = 0
        # Construct GraphQL query url from query has and variables to pass
        query_url = "https://www.instagram.com/graphql/query/?{}".format(
            urlencode(
                {
                    "query_hash": hash,
                    "variables": json.dumps(variables, separators=(",", ":")),
                }
            )
        )

        # Actually execute the query here, retry method
        def _graphql_query(url):
            data = json.loads(self.session.get(query_url).text)
            if data["status"] == "ok":
                return data
            else:
                sleep_time += 60
                print(
                    f"Instagram GraphQL query failed. Sleeping for {sleep_time} seconds before retrying."
                )
                sleep(sleep_time)
                _graphql_query(url)

        try:
            # If successful, load data
            data = _graphql_query(query_url)
        except:
            # If unsuccessful, return None
            print(f"Error with query {query_url}")
            data = None
        return data

    def __get_post_shortcodes(self, old_list=None, progress_bar=True):
        """Get shortcodes for all posts by a user
        
        Parameters
        ----------
        old_list : list
            An old list of shortcodes, so not as to re-run unnecessary tasks
        progress_bar : bool
            Display progress of shortcode retrieval

        Returns
        -------
        shortcode_list : list
            List of all shortcodes for a user
        """
        # Load previous list if applicable, otherwise initialize empty list
        if old_list != None:
            shortcode_list = old_list
        else:
            shortcode_list = []

        # Ensure shortcodes can be downloaded
        if not self.private:
            end_cursor = ""
            # Set current count to length of the shortcode list
            while len(shortcode_list) < self.media_count:
                # Query GraphQL for Instagram shortcodes (max 50 at a time, can't parallelize)
                response = self.__graphql_query(
                    "d496eb541e5c789274548bf473cc553e",
                    {"id": self.id, "first": 50, "after": end_cursor},
                )
                if response:
                    # Record end cursor for next query if necessary
                    end_cursor = response["data"]["user"][
                        "edge_owner_to_timeline_media"
                    ]["page_info"]["end_cursor"]
                    # Iterate through each post in the query
                    for node in response["data"]["user"][
                        "edge_owner_to_timeline_media"
                    ]["edges"]:
                        # Grab shortcode, if not in list, add it to the list and increment count
                        shortcode = node["node"]["shortcode"]
                        if shortcode not in shortcode_list:
                            shortcode_list.append(shortcode)
                            if progress_bar:
                                print(
                                    " Retreived {}% ({}/{}) of @{}'s posts".format(
                                        round(
                                            100
                                            * len(shortcode_list)
                                            / self.media_count,
                                            2,
                                        ),
                                        len(shortcode_list),
                                        self.media_count,
                                        self.username,
                                    ),
                                    end="\r",
                                    flush=True,
                                )
                        # If the shortcode list is up to date, terminate the loop
                        else:
                            break
        # If user is private, print message and return empty list
        else:
            print("Shortcodes could not be accessed. User is private.")

        return shortcode_list

    def __build_post_scaffold(self):
        """ Build a basic post scaffold, adding each shortcode in a dict to json["posts], if not already existing """
        for shortcode in self.shortcode_list:
            # After confirming shortcode hasn't already been recorded, append it to dict
            if shortcode not in self.recorded_list:
                self.json["posts"].append({"shortcode": shortcode})
            else:
                pass

    def __populate_post_scaffold(self, progress_bar=True):
        """Fill JSON with user content"""

        def __get_media(node):
            """ Get various pieces of media-specific from a post """
            # Media dict
            media = {}
            # ID
            media.update({"id": node["id"]})
            # Media type
            media.update({"typename": node["__typename"]})
            # Media thumnail
            media.update({"thumbnail": node["display_resources"][-1]["src"]})
            # Get content based on typename
            if media["typename"] == "GraphImage":
                media.update({"content": media["thumbnail"]})
            elif media["typename"] == "GraphVideo":
                media.update({"content": node["video_url"]})
            else:
                pass
            # Media preview
            if node["media_preview"] is not None:
                media.update({"preview": node["media_preview"]})
            # Tagged users in media media
            try:
                tagged_users = []
                for tagged in node["edge_media_to_tagged_user"]["edges"]:
                    node = tagged["node"]
                    tagged_users.append(
                        {
                            "username": node["user"]["username"],
                            "x": node["x"],
                            "y": node["y"],
                        }
                    )
                if tagged_users != []:
                    media.update({"tagged": tagged_users})
            except Exception as e:
                print(f"Error {e} during __get_media")

            # Return built dict
            return media

        def __build_post_from_scaffold(post, overwrite=False):
            """ Fill in post scaffold with available information """
            shortcode = post["shortcode"]
            # Execute only if post hasn't been recorded or if overwrite is True
            if "typename" not in post or overwrite == True:
                try:
                    # Get JSON data
                    response = self.__a_query(
                        "p/{}".format(shortcode), login_required=False
                    )["graphql"]["shortcode_media"]
                    # Typename
                    try:
                        typename = response["__typename"]
                        post.update({"typename": response["__typename"]})
                    except:
                        pass
                    # Media
                    try:
                        media = []
                        if typename == "GraphSidecar":
                            # Iterate through individual media in sidecar
                            for node in response["edge_sidecar_to_children"]["edges"]:
                                media.append(__get_media(node["node"]))
                        else:
                            media.append(__get_media(response))
                        post.update({"media": media})
                    except:
                        pass
                    # Caption
                    try:
                        post.update(
                            {
                                "caption": response["edge_media_to_caption"]["edges"][
                                    0
                                ]["node"]["text"]
                            }
                        )
                    except:
                        pass
                    # Like count
                    try:
                        post.update(
                            {"likes": response["edge_media_preview_like"]["count"]}
                        )
                    except:
                        pass
                    # Comments count
                    try:
                        post.update(
                            {
                                "comments": response["edge_media_to_parent_comment"][
                                    "count"
                                ]
                            }
                        )
                    except:
                        pass
                    # Dimensions
                    try:
                        post.update(
                            {
                                "dimensions": {
                                    "width": response["dimensions"]["width"],
                                    "height": response["dimensions"]["height"],
                                }
                            }
                        )
                    except:
                        pass
                    # Timestamp
                    try:
                        post.update({"timestamp": response["taken_at_timestamp"]})
                    except:
                        pass
                    # Location
                    try:
                        if response["location"] is not None:
                            post.update({"location": response["location"]})
                    except:
                        pass
                    # Ad
                    try:
                        post.update({"ad": response["is_ad"]})
                    except:
                        pass
                    # Accessibility caption
                    try:
                        if response["accessibility_caption"] is not None:
                            post.update(
                                {
                                    "accessibility caption": response[
                                        "accessibility_caption"
                                    ]
                                }
                            )
                    except:
                        pass
                    # Write changes to JSON file
                    write_dict_to_file(
                        "{}.json".format(self.username), self.json, minimize=True
                    )
                except:
                    print(
                        "Error gathering data for post https://www.instagram.com/p/{}".format(
                            shortcode
                        )
                    )
                    pass
            else:
                pass

        # Concurrently build post json from scaffold
        concurrent(
            __build_post_from_scaffold,
            self.json["posts"],
            progress_bar=progress_bar,
            desc="Building post database",
        )

    def __get_story(self, story_item):
        story = {}
        # Story type
        try:
            story_typename = story_item["__typename"]
            story.update({"typename": story_typename})
        except:
            pass
        # Story ID
        try:
            story.update({"id": story_item["id"]})
        except:
            pass
        # Get content, if not video, default to thumbnail
        try:
            if story_typename == "GraphStoryVideo":
                content = story_item["video_resources"][-1]["src"]
            else:
                content = story_item["display_resources"][-1]["src"]
            story.update({"content": content})
        except:
            pass
        # Media preview
        if "media_preview" in story_item:
            if story_item["media_preview"] != None:
                story.update({"preview": story_item["media_preview"]})
        # Timestamps
        try:
            story.update({"taken at": story_item["taken_at_timestamp"]})
        except:
            pass
        try:
            story.update({"expiring at": story_item["expiring_at_timestamp"]})
        except:
            pass
        # Tappable objects
        try:
            linked = []
            for links in story_item["tappable_objects"]:
                if links["__typename"] == "GraphTappableFeedMedia":
                    story_shortcode = links["media"]["shortcode"]
                    linked.append(f"https://www.instagram.com/p/{story_shortcode}")
                elif links["__typename"] == "GraphTappableMention":
                    story_username = links["username"]
                    linked.append(f"https://www.instagram.com/{story_username}")
            story.update({"linked": linked})
        except:
            pass

        return story

    def __get_stories(self):
        response = self.__graphql_query(
            "f5dc1457da7a4d3f88762dae127e0238",
            {
                "reel_ids": [self.id],
                "precomposed_overlay": False,
                "story_viewer_fetch_count": 50,
            },
        )
        # Try to add stories, pass if none
        try:
            for story_item in response["data"]["reels_media"][0]["items"]:
                story = self.__get_story(story_item)
                if "id" in story:
                    if story["id"] not in self.story_ids:
                        self.json["stories"].append(story)
                        self.story_ids.append(story["id"])
        except:
            pass

    def __get_highlight_reel(self, highlight_reel_id):
        response = self.__graphql_query(
            "f5dc1457da7a4d3f88762dae127e0238",
            {
                "reel_ids": [],
                "tag_names": [],
                "location_ids": [],
                "highlight_reel_ids": [str(highlight_reel_id)],
                "precomposed_overlay": False,
                "show_story_viewer_list": True,
                "story_viewer_fetch_count": 50,
                "story_viewer_cursor": "",
                "stories_video_dash_manifest": False,
            },
        )
        content = []
        for highlight in response["data"]["reels_media"]:
            for item in highlight["items"]:
                content.append(self.__get_story(item))

        return content

    def __get_highlights(self):
        response = self.__graphql_query(
            "ad99dd9d3646cc3c0dda65debcd266a7",
            {
                "user_id": str(self.id),
                "include_reel": True,
                "include_highlight_reels": True,
            },
        )
        for reel in response["data"]["user"]["edge_highlight_reels"]["edges"]:
            hr = reel["node"]
            highlight_reel = {}
            # Reel name
            try:
                highlight_reel.update({"title": hr["title"]})
            except:
                pass
            # Reel ID
            try:
                highlight_reel.update({"id": hr["id"]})
            except:
                pass
            # Reel cover media
            try:
                highlight_reel.update(
                    {"cover": highlight_reel["cover_media"]["thumbnail_src"]}
                )
            except:
                pass
            # Reel content
            try:
                highlight_reel.update({"content": self.__get_highlight_reel(hr["id"])})
            except:
                pass

            if highlight_reel["id"] not in self.highlight_ids:
                self.json["highlights"].append(highlight_reel)
                self.highlight_ids.append(highlight_reel["id"])

    # def get_following(self):
    #     self.__graphql_query("d04b0a864b4b54837c0d870b0e77e076", {"id":str(self.id),"first":50})
    #     self.__graphql_query("d04b0a864b4b54837c0d870b0e77e076", {"id":str(self.id),"first":50,"after":end_cursor})

    # def get_followers(self):
    #     self.__graphql_query("c76146de99bb02f6415203be841dd25a", {"id":str(self.id),"first":50})
    #     self.__graphql_query("c76146de99bb02f6415203be841dd25a", {"id":str(self.id),"first":50,"after":end_cursor})

    # def get_tagged_content(self):
    #     self.__graphql_query("ff260833edf142911047af6024eb634a", {"id":str(self.id),"first":50})
    #     # after

    #################################
    # METHODS FOR DOWNLOADING MEDIA #
    #################################
    def download_profile_picture(self):
        """ Download an Instagram user's profile picure in its highest quality """
        download(self.profile_pic, "{}.jpg".format(self.username))

    def get_previews(self, mode="save", output_dir="previews"):
        """Get all media previews for a user

        Parameters
        ----------
        mode : str
            Determine whether media preview images should be shown or saved

        Returns
        -------
        results : list
            List of all media previews as numpy arrays
        """
        # Make directory is necessary
        mkdir(output_dir)

        # Get media previews
        previews = []
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "media" in post:
                for m in post["media"]:
                    try:
                        # Create filename
                        filename = "{}/{}_{}_preview.jpg".format(
                            output_dir, shortcode, m["id"]
                        )
                        # Append filename and media preview image
                        previews.append(
                            (filename, self.__media_preview_to_image(m["preview"]))
                        )
                    except:
                        pass
            else:
                pass

        # Shor or save image, depending on mode
        results = []
        for filename, image in previews:
            if mode == "save":
                image.save(filename)
            elif mode == "show":
                image.show()
            elif mode == "return":
                results.append(image)
            else:
                print("Error: mode must be either save (default) or show")

        # Return media preview list
        return results

    def download_stories(self, output_dir="", progress_bar=True):
        """ Download all stories from an Instagram user in their highest quality

        Parameters
        ----------
        output_dir : str
            Path to directory where stories should be saved
        progress_bar : bool
            Display progress of post download
        """
        # Create output directory, if necessary
        mkdir(output_dir)
        # Fill stories list with filenames and url's to hd thumbniails
        stories_list = []
        for story in self.json["stories"]:
            if "content" in story:
                ext = "mp4" if story["typename"] == "GraphStoryVideo" else "jpg"
                filename = "{}_story.{}".format(story["id"], ext)
                filename = Path(output_dir).joinpath(filename)
                stories_list.append((story["content"], filename))
            else:
                pass

        # Concurently download images
        concurrent(
            self.__download_tuple,
            stories_list,
            progress_bar=progress_bar,
            desc="Downloading stories",
        )

    def download_highlights(self, output_dir="", progress_bar=True):
        """ Download all highlights from an Instagram user in their highest quality

        Parameters
        ----------
        output_dir : str
            Path to directory where highlights should be saved
        progress_bar : bool
            Display progress of post download
        """
        # Create output directory, if necessary
        mkdir(output_dir)
        # Fill highlights list with filenames and url's to hd thumbniails
        highlights_list = []
        for highlights in self.json["highlights"]:
            if "content" in highlights:
                for story in highlights["content"]:
                    ext = "mp4" if story["typename"] == "GraphStoryVideo" else "jpg"
                    filename = "{}_highlight.{}".format(story["id"], ext)
                    filename = Path(output_dir).joinpath(filename)
                    highlights_list.append((story["content"], filename))
            else:
                pass

        # Concurently download images
        concurrent(
            self.__download_tuple,
            highlights_list,
            progress_bar=progress_bar,
            desc="Downloading highlights",
        )

    def download_thumbnails(self, output_dir="", progress_bar=True):
        """ Download all posts from an Instagram user in their highest quality

        Parameters
        ----------
        output_dir : str
            Path to directory where thumbnails should be saved
        progress_bar : bool
            Display progress of post download
        """
        # Create output directory, if necessary
        mkdir(output_dir)
        # Fill thumbnail list with filenames and url's to hd thumbniails
        thumbnail_list = []
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "media" in post:
                for m in post["media"]:
                    filename = "{}_{}_thumbnail.jpg".format(shortcode, m["id"])
                    filename = Path(output_dir).joinpath(filename)
                    thumbnail_list.append((m["thumbnail"], filename))
            else:
                pass

        # Concurently download images
        concurrent(
            self.__download_tuple,
            thumbnail_list,
            progress_bar=progress_bar,
            desc="Downloading thumbnails",
        )

    def download_posts(self, output_dir="", progress_bar=True):
        """Download all posts from an Instagram user in their highest quality

        Parameters
        ----------
        output_dir : str
            Path to directory where posts should be saved
        progress_bar : bool
            Display progress of post download
        """
        # Create output directory, if necessary
        mkdir(output_dir)
        # Fill content list with filenames and url's to hd content
        content_list = []
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            for m in post["media"]:
                ext = "jpg" if m["typename"] == "GraphImage" else "mp4"
                filename = "{}_{}.{}".format(shortcode, m["id"], ext)
                content_list.append((m["content"], filename))

        # Concurently download images/videos
        concurrent(
            self.__download_tuple,
            content_list,
            progress_bar=progress_bar,
            desc="Downloading posts",
        )

    #####################################
    # METHODS FOR INFORMATION RETRIEVAL #
    #####################################
    def get_post_by_number(self, number):
        """ Get a post shortcode by number

        Parameters
        ----------
        number : str
            Number of post

        Returns
        -------
        shortcode : string
            Shortcode correlating with post
        """
        # Ensure count is <= media count
        if number <= self.json["profile"]["media count"]:
            return self.shortcode_list[number]
        else:
            print(
                "Error: latest post is {}, please enter number either lesser or equal to this post.".format(
                    count
                )
            )
            return None

    def search_captions_by_keyword(self, keyword):
        """ Find all captions containing a queried keyword

        Parameters
        ----------
        keyword : str
            keyword to search captions for

        Returns
        -------
        captions : list
            List of matches of form (shortcode, caption)
        """
        captions = []
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "caption" in post:
                if keyword.lower() in post["caption"].lower():
                    captions.append((shortcode, post["caption"]))
        # Return media preview list
        return captions

    def get_tagged_users(self):
        """ Get list of all users tagged in post

        Returns
        -------
        tagged_users : list
            List of all tagged users
        """
        tagged_users = {}
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "media" in post:
                for m in post["media"]:
                    try:
                        # Get all tagged useres if existing
                        for tu in m["tagged"]:
                            username = tu["username"]
                            if username in tagged_users:
                                tagged_users[username].append(shortcode)
                            else:
                                tagged_users[username] = [shortcode]
                    except:
                        pass
            else:
                pass

        # Return set of tagged users (remove duplicates)
        tagged_users = sorted(
            tagged_users.items(), key=lambda x: len(x[1]), reverse=True
        )
        return tagged_users

    def get_tagged_users_in_captions(self):
        """ Get list of all users tagged in captions

        Returns
        -------
        tagged_users : list
            List of all tagged users in captions
        """
        tagged_users = {}
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "caption" in post:
                for word in post["caption"].split():
                    if word[0] == "@":
                        # Ensure two hashtags not stuck together
                        for word in word.split("@"):
                            word = self.__strip_username(word.lower())
                            if word != "@" and word != None:
                                if word in tagged_users:
                                    tagged_users[word].append(shortcode)
                                else:
                                    tagged_users[word] = [shortcode]
        # Return sorted tagged users in captions
        tagged_users = sorted(
            tagged_users.items(), key=lambda x: len(x[1]), reverse=True
        )
        return tagged_users

    def get_hashtags(self):
        """ Get all hashtags (and the posts that use them) from a user, sorted by frequency 
        
        Returns
        -------
        hashtags : list
            Sorted list of all hashtags by post frequency of form (hashtag, [shortcode(s)])
        """
        hashtags = {}
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "caption" in post:
                for word in post["caption"].split():
                    # Solve the #BEENTRILL# problem
                    if word[0] == "#":
                        # Ensure two hashtags not stuck together
                        for hashtag in word.split("#"):
                            hashtag = self.__strip_hashtag(hashtag)
                            # print(hashtag)
                            if hashtag != "#" and hashtag != None and hashtag != "":
                                if hashtag in hashtags:
                                    hashtags[hashtag].append(shortcode)
                                else:
                                    hashtags.update({hashtag: [shortcode]})

        # Return hashtags list
        hashtags = sorted(hashtags.items(), key=lambda x: len(x[1]), reverse=True)
        return hashtags

    def get_posts_by_like_count(self):
        """ Sort posts by like count
        
        Returns
        -------
        likes : list
            Sorted list of all posts by like count in form (shortcode, like count)
        """
        likes = []
        for post in self.json["posts"]:
            shortcode = post["shortcode"]
            if "likes" in post:
                likes.append((shortcode, post["likes"]))
        # Sort like list and return
        likes = sorted(likes, key=lambda x: x[1], reverse=True)
        return likes

    def get_lifetime_like_count(self):
        """ Total number of likes a user has received
        
        Returns
        -------
        likes : int
            Number of total likes a user has received
        """
        likes = self.get_posts_by_like_count()
        return sum([like_count for (shortcode, like_count) in likes])
