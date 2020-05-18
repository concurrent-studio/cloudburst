# -*- coding: utf-8 -*-
""" Scrape VSCO """

import os
import requests
from pathlib import Path
from time import time
from cloudburst.core import concurrent, mkdir, write_dict_to_file
from cloudburst.vision import download

__all__ = ["VSCO"]

session_header = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "vsco.co",
    "Referer": "http://vsco.co/vsco/images/1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36",
}

media_header = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "en-US,en;q=0.9",
    "Connection": "keep-alive",
    "Host": "vsco.co",
    "Referer": "http://vsco.co/vsco/images/1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
    "X-Client-Build": "1",
    "X-Client-Platform": "web",
}


class VSCO:
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
        joe.download_all() # download all images and journal images
    """

    def __init__(self, username):
        """Constructor method

        Parameters
        ----------
        username : str
            any VSCO user's username
        """

        self.username = username
        self.session = requests.Session()
        self.session.get(
            "http://vsco.co/content/Static/userinfo?callback=jsonp_{}_0".format(
                round(time() * 1000)
            ),
            headers=session_header,
        )
        self.uid = self.session.cookies.get_dict()["vs"]
        self.userpath = mkdir(self.username)
        os.chdir(self.userpath)
        self.siteid = self.session.get(
            "http://vsco.co/ajxp/{}/2.0/sites?subdomain={}".format(
                self.uid, self.username
            )
        ).json()["sites"][0]["id"]
        self.journal_url = "http://vsco.co/ajxp/{}/2.0/articles?site_id={}".format(
            self.uid, self.siteid
        )
        self.media_url = "http://vsco.co/ajxp/{}/2.0/medias?site_id={}".format(
            self.uid, self.siteid
        )

    @staticmethod
    def _download_vsco_media(data):
        """Download a vsco post given its type, id, and a link to its static content"""
        media_id = data[1]
        media_link = "https://{}".format(data[2])
        if data[0] == "image":
            download(media_link, "{}.jpg".format(media_id))
        elif data[0] == "video":
            download(media_link, "{}.mp4".format(media_id))

    def download_images(self):
        """Download all images for a given user"""
        # Make directory for journal and cd into it
        image_path = mkdir("images")
        os.chdir(image_path)

        # Keep track of media type, id, and link
        data = []
        # Get JSON data for journal and write to file
        image_data = self.session.get(
            self.media_url, params={"size": 10000, "page": 1}, headers=media_header
        ).json()
        write_dict_to_file("{}_images.json".format(self.username), image_data)

        # Iterate through data, appending each journal post to data (or undownloadable if necessary)
        for i in image_data["media"]:
            if i["is_video"] == True:
                post_type = "video"
            else:
                post_type = "image"
            try:
                data.append((post_type, i["_id"], i["responsive_url"]))
            except:
                print(j)
        # Concurrently download all media
        concurrent(
            self._download_vsco_media,
            data,
            executor="threadpool",
            progress_bar=True,
            desc="Downloading {}'s images".format(self.username),
        )
        # Change directory back into master path
        os.chdir(self.userpath)

    def download_journal(self):
        """Download all journal images for a given user"""
        # Make directory for journal and cd into it
        journal_path = mkdir("journal")
        os.chdir(journal_path)

        # Keep track of media type, id, and link
        data = []
        # Keep track of undownloadable links (download of these links to be implemented)
        undownloadable_links = {"undownloadable": []}
        # Get JSON data for journal and write to file
        journal_data = self.session.get(
            self.journal_url, params={"size": 10000, "page": 1}, headers=media_header
        ).json()
        write_dict_to_file("{}_journal.json".format(self.username), journal_data)

        # Iterate through data, appending each journal post to data (or undownloadable if necessary)
        for j in journal_data["articles"]:
            for b in j["body"]:
                if b["type"] in ("image", "video"):
                    try:
                        c = b["content"][0]
                        data.append((b["type"], c["id"], c["responsive_url"]))
                    except:
                        undownloadable_links["undownloadable"].append(b)
        write_dict_to_file(
            "{}_journal_undownloadable.json".format(self.username), undownloadable_links
        )

        # Concurrently download all media
        concurrent(
            self._download_vsco_media,
            data,
            executor="threadpool",
            progress_bar=True,
            desc="Downloading {}'s journal images".format(self.username),
        )
        # Change directory back into master path
        os.chdir(self.userpath)

    def download_all(self):
        """Download all available data for a user"""
        # Get images
        self.download_images()
        # Get journal
        self.download_journal()
