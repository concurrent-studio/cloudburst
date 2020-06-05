# -*- coding: utf-8 -*-
""" Scrape Twitter """

import os
import requests
from pathlib import Path
from time import time
from cloudburst.core import concurrent, mkdir, write_dict_to_file
from cloudburst import vision as cbv

"""
get_tweets(query: str [, pages: int]) -> dictionary
for tweet in get_tweets('twitter', pages=1):
...     print(tweet['text'])
Key	Type	Description
tweetId	string	Tweet's identifier, visit twitter.com/USERNAME/ID to view tweet.
username	string	Tweet's username
tweetUrl	string	Tweet's URL
isRetweet	boolean	True if it is a retweet, False othercase
time	datetime	Published date of tweet
text	string	Content of tweet
replies	integer	Replies count of tweet
retweets	integer	Retweet count of tweet
likes	integer	Like count of tweet
entries	dictionary	Has hashtags, videos, photos, urls keys. Each one's value is 

from twitter_scraper import get_trends
>>> get_trends()
['#WHUTOT', '#ARSSOU', 'West Ham', '#AtalantaJuve', '#バビロニア', '#おっさんずラブinthasky', 'Southampton', 'Valverde', '#MMKGabAndMax', '#23NParoNacional']

>>> from twitter_scraper import Profile
>>> profile = Profile('bugraisguzar')
>>> profile.location
'Istanbul'
>>> profile.name
'Buğra İşgüzar'
>>> profile.username
'bugraisguzar'
"""

__all__ = ["Twitter"]

class Twitter:
    """Scrape the data of a VSCO user

    Attributes
    ----------
    username : str
        User's username

    Examples
    --------
    Download all data of @joe

    .. code-block:: python

       from cloudburst import social as cbs

       joe = cbs.VSCO("joe") # instantiate new VSCO object
       joe.cbv.download_all() # download all images and journal images
    """

    def __init__(self, username):
        """Constructor method

        Parameters
        ----------
        username : str
            any Instagram user's username
        """

        self.username = username
        self.session = requests.Session() 
        self.session.get("http://vsco.co/content/Static/userinfo?callback=jsonp_{}_0".format(round(time()*1000)), headers=session_header)
        self.uid = self.session.cookies.get_dict()['vs']
        self.userpath = mkdir(self.username)
        os.chdir(self.userpath)
        self.siteid = self.session.get("http://vsco.co/ajxp/{}/2.0/sites?subdomain={}".format(self.uid,self.username)).json()["sites"][0]["id"]
        self.journal_url = "http://vsco.co/ajxp/{}/2.0/articles?site_id={}".format(self.uid, self.siteid)
        self.media_url = "http://vsco.co/ajxp/{}/2.0/medias?site_id={}".format(self.uid,self.siteid)
    
    @staticmethod
    def _cbv.download_vsco_media(data):
        """Download a vsco post given its type, id, and a link to its static content"""
        media_id = data[1]
        media_link = "https://{}".format(data[2])
        if data[0] == "image":
            cbv.download(media_link, "{}.jpg".format(media_id))
        elif data[0] == "video":
            cbv.download(media_link, "{}.mp4".format(media_id))

    def cbv.download_images(self):
        """Download all images for a given user"""
        # Make directory for journal and cd into it
        image_path = mkdir("images")
        os.chdir(image_path)

        # Keep track of media type, id, and link
        data = []
        # Get JSON data for journal and write to file
        image_data = self.session.get(self.media_url, params={"size":10000, "page":1}, headers=media_header).json()
        write_dict_to_file("{}_images.json".format(self.username), image_data)

        # Iterate through data, appending each journal post to data (or uncbv.downloadable if necessary)
        for i in image_data["media"]:
            if i["is_video"] == True:
                post_type = "video"
            else:
                post_type = "image"
            try:
                data.append((post_type, i["_id"], i["responsive_url"]))
            except:
                print(j)
        # Concurrently cbv.download all media
        concurrent(self._cbv.download_vsco_media, data, progress_bar=True, desc="Downloading {}'s images".format(self.username))
        # Change directory back into master path
        os.chdir(self.userpath)

    def cbv.download_journal(self):
        """Download all journal images for a given user"""
        # Make directory for journal and cd into it
        journal_path = mkdir("journal")
        os.chdir(journal_path)

        # Keep track of media type, id, and link
        data = []
        # Keep track of uncbv.downloadable links (download of these links to be implemented)
        uncbv.downloadable_links = {"undownloadable": []}
        # Get JSON data for journal and write to file
        journal_data = self.session.get(self.journal_url, params={"size":10000, "page":1}, headers=media_header).json()
        write_dict_to_file("{}_journal.json".format(self.username), journal_data)

        # Iterate through data, appending each journal post to data (or uncbv.downloadable if necessary)
        for j in journal_data["articles"]:
            for b in j["body"]:
                if b["type"] in ("image", "video"):
                    try:
                        c = b["content"][0]
                        data.append((b["type"], c["id"], c["responsive_url"]))
                    except:
                        uncbv.downloadable_links["undownloadable"].append(b)
        write_dict_to_file("{}_journal_uncbv.downloadable.json".format(self.username), undownloadable_links)

        # Concurrently cbv.download all media
        concurrent(self._cbv.download_vsco_media, data, progress_bar=True, desc="Downloading {}'s journal images".format(self.username))
        # Change directory back into master path
        os.chdir(self.userpath)

    def cbv.download_all(self):
        """Download all available data for a user"""
        # Get images
        self.cbv.download_images()
        # Get journal
        self.cbv.download_journal()
