# -*- coding: utf-8 -*-
import json
import urllib.parse

import requests

class TwitterSession:
	def __init__(self):
		self.session = requests.Session()
		self._set_headers()

	def _add_cookies(self):
		self.session.get("https://twitter.com/elonmusk")
		self.session.options('https://api.twitter.com/1.1/guest/activate.json', headers={
			'authority': 'api.twitter.com',
			'accept': '*/*',
			'accept-language': 'en-US,en;q=0.9',
			'access-control-request-headers': 'authorization,x-csrf-token,x-twitter-active-user,x-twitter-client-language',
			'access-control-request-method': 'POST',
			'cache-control': 'no-cache',
			'origin': 'https://twitter.com',
			'pragma': 'no-cache',
			'referer': 'https://twitter.com/',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
		})
		self.session.get("https://twitter.com/sw.js", headers={
			'Accept': '*/*',
			'DNT': '1',
			'Service-Worker': 'script',
		})
		resp= self.session.post('https://api.twitter.com/1.1/guest/activate.json', headers={
			'authority': 'api.twitter.com',
			'accept': '*/*',
			'accept-language': 'en-US,en;q=0.9',
			'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
			'cache-control': 'no-cache',
			'content-type': 'application/x-www-form-urlencoded',
			'dnt': '1',
			'origin': 'https://twitter.com',
			'pragma': 'no-cache',
			'referer': 'https://twitter.com/',
			'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': '"macOS"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
			'x-csrf-token': 'bd3d69b630dea61cf717834b8940a8d2',
			'x-twitter-active-user': 'yes',
			'x-twitter-client-language': 'en',
		})
		if resp.json()["guest_token"]:
			self.session.cookies.set("gt", resp.json()["guest_token"])

	def _set_headers(self):
		self._add_cookies()
		self.headers = {
			"authority": "twitter.com",
			"accept": "*/*",
			"accept-language": "en-US,en;q=0.9",
			"authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
			"content-type": "application/json",
			"cookie": "; ".join(f"{k}={v}" for k, v in self.session.cookies.get_dict().items()),
			"dnt": "1",
			"referer": "https://twitter.com/elonmusk",
			"sec-ch-ua": "\\\"Not?A_Brand\\\";v=\\\"8\\\", \\\"Chromium\\\";v=\\\"108\\\"",
			"sec-ch-ua-mobile": "?0",
			"sec-ch-ua-platform": "\\\"macOS\\\"",
			"sec-fetch-dest": "empty",
			"sec-fetch-mode": "cors",
			"sec-fetch-site": "same-origin",
			"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
			"x-guest-token": self.session.cookies.get_dict()["gt"],
			"x-twitter-active-user": "yes",
			"x-twitter-client-language": "en"
		}

	def user_info(self, username):
		variables = {
			'screen_name': username,
			'withSafetyModeUserFields': True,
			'withSuperFollowsUserFields': True
		}
		features = {
			'responsive_web_twitter_blue_verified_badge_is_enabled': True,
			'verified_phone_label_enabled': False,
			'responsive_web_twitter_blue_new_verification_copy_is_enabled': False,
			'responsive_web_graphql_timeline_navigation_enabled': True
		}
		base_url = "https://twitter.com/i/api/graphql/X7fFRSOaxfcxCk0VGDIKdA/UserByScreenName?"
		query_params = {
			'variables': json.dumps(variables).replace(" ", ""),
			'features': json.dumps(features).replace(" ", ""),
		}
		user_info = self.session.get(base_url + urllib.parse.urlencode(query_params), headers=self.headers).json()
		result = user_info["data"]["user"]["result"]
		description = result["legacy"]["description"]
		for u in result["legacy"]["entities"]["description"]["urls"]:
			description = description.replace(u["url"], u["expanded_url"])
		urls = result["legacy"]["entities"].get("url", {}).get("urls", None)
		return {
				"id": result["rest_id"],
				"name": result["legacy"]["name"],
				"description": description,
				"private": result["legacy"]["protected"],
				"verified": result["legacy"]["verified"],
				"has_nft_avatar": result["has_nft_avatar"],
				"is_blue_verified": result["is_blue_verified"],
				"possibly_sensitive": result["legacy"]["possibly_sensitive"],
				"created_at": result["legacy"]["created_at"],
				"url": urls[0]["expanded_url"] if urls else None,
				"likes_count": result["legacy"]["favourites_count"],
				"followers_count": result["legacy"]["followers_count"],
				"following_count": result["legacy"]["friends_count"],
				"tweet_count": result["legacy"]["listed_count"],
				"media_count": result["legacy"]["media_count"],
				"location": result["legacy"]["location"],
				"pinned_tweets": result["legacy"]["pinned_tweet_ids_str"],
				"profile_image_url": result["legacy"].get("profile_image_url_https", None),
				"profile_banner_url": result["legacy"].get("profile_banner_url", None),
				"affiliates": result["affiliates_highlighted_label"].get("label", {}).get("description", None)
		}
