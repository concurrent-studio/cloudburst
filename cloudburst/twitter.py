# -*- coding: utf-8 -*-
import json
import re
import urllib.parse

import requests

class TwitterSession:
	def __init__(self):
		"""Create a new TwitterSession object"""
		self.session = requests.Session()
		self._set_headers()

	def _add_cookies(self):
		"""Add necessary cookies to the session"""
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
		"""Set the headers for the session, allowing for twitter API calls"""
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

	def _parse_tweet_response(self, tweet_response, fetch_replies=False):
		typename = tweet_response.get("__typename")
		# Handle tombstones and tweets with visibility results (a.k.a. tweets from affiliated accounts like Russian state media)
		tweet_result = tweet_response
		if typename == "TweetTombstone":
			return {"tomstone": tweet_response["tombstone"]["text"]["text"]}
		elif typename == "TweetWithVisibilityResults":
			tweet_result = tweet_result["tweet"]
		# Get username from tweet author
		try:
			username = tweet_result["core"]["user_results"]["result"]["legacy"]["screen_name"]
		except Exception as e:
			print(json.dumps(tweet_result, indent=2))
			print(e)
			exit()
		# Parse tweet
		tweet = {
			"id": tweet_result["rest_id"],
			"text": tweet_result["legacy"]["full_text"],
			"created_at": tweet_result["legacy"]["created_at"],
			"mentions": [
				{"name": u["name"], "username": u["screen_name"]}
				for u in tweet_result["legacy"]["entities"]["user_mentions"]
				],
			"urls": [u["expanded_url"] for u in tweet_result["legacy"]["entities"]["urls"]],
			"hashtags": [h["text"] for h in tweet_result["legacy"]["entities"]["hashtags"]],
			"stock_symbols": [s["text"] for s in tweet_result["legacy"]["entities"]["symbols"]],
			"likes_count": tweet_result["legacy"]["favorite_count"],
			"quote_count": tweet_result["legacy"]["quote_count"],
			"reply_count": tweet_result["legacy"]["reply_count"],
			"retweet_count": tweet_result["legacy"]["retweet_count"],
			"retweeted": tweet_result["legacy"]["retweeted"],
			"tweet_url": f"https://twitter.com/{username}/status/{tweet_result['rest_id']}"
		}
		match = re.search(r"(?<=\>).+(?=\<)", tweet_result["legacy"]["source"])
		if match:
			tweet["source"] = match.group()
		# Handle replied tweets
		replied_to_username = tweet_result["legacy"].get("in_reply_to_username")
		replied_to_id = tweet_result["legacy"].get("in_reply_to_status_id_str")
		if replied_to_username and replied_to_id:
			if fetch_replies:
				tweet["in_reply_to"] = self.get_tweet(replied_to_id)
			else:
				tweet["in_reply_to_url"] = f"https://twitter.com/{replied_to_username}/status/{replied_to_id}"
		# Handle quoted tweets
		if "quoted_status_result" in tweet_result:
			tweet["quoted_tweet"] = self._parse_tweet_response(tweet_result["quoted_status_result"]["result"])
		# Handle tweets with visibility results (a.k.a. tweets from affiliated accounts like russian state media)
		if tweet_response["__typename"] == "TweetWithVisibilityResults":
			if tweet_response.get("tweetVisibilityNudge"):
				tweet["visiblity_heading"] = tweet_response["tweetVisibilityNudge"]["tweet_visibility_nudge_actions"][0]["tweet_visibility_nudge_action_payload"]["heading"]
			else:
				tweet["visiblity_heading"]  = tweet_result["core"]["user_results"]["result"]["affiliates_highlighted_label"]["label"]["description"]
		return tweet

	def get_username(self, userId):
		"""Get a username from a person's userId"""
		queryURL = f"https://api.twitter.com/1.1/users/lookup.json?user_id={userId}"
		return requests.get(queryURL, headers=self.headers).json()[0]["screen_name"]

	def user_info(self, username):
		"""Get a user's info"""
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

	def get_tweet(self, status_code, fetch_replies=False):
		"""Get a tweet given its status code"""
		tweet_url = "https://twitter.com/i/api/graphql/-mbYIJl8o1KjY_4prcJ4ZQ/TweetDetail?"
		tweet_variables = {
			'focalTweetId': status_code,
			'with_rux_injections': False,
			'includePromotedContent': True,
			'withCommunity': True,
			'withQuickPromoteEligibilityTweetFields': True,
			'withBirdwatchNotes': True,
			'withSuperFollowsUserFields': True,
			'withDownvotePerspective': False,
			'withReactionsMetadata': False,
			'withReactionsPerspective': False,
			'withSuperFollowsTweetFields': True,
			'withVoice': True,
			'withV2Timeline': True
		}
		tweet_features = {
			'responsive_web_twitter_blue_verified_badge_is_enabled': True,
			'verified_phone_label_enabled': False,
			'responsive_web_graphql_timeline_navigation_enabled': True,
			'unified_cards_ad_metadata_container_dynamic_card_content_query_enabled': True,
			'tweetypie_unmention_optimization_enabled': True,
			'responsive_web_uc_gql_enabled': True,
			'vibe_api_enabled': True,
			'responsive_web_edit_tweet_api_enabled': True,
			'graphql_is_translatable_rweb_tweet_is_translatable_enabled': True,
			'standardized_nudges_misinfo': True,
			'tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled': False,
			'interactive_text_enabled': True,
			'responsive_web_text_conversations_enabled': False,
			'responsive_web_enhance_cards_enabled': True
		}
		tweet_query_selection = {
			'variables': json.dumps(tweet_variables).replace(" ", ""),
			'features': json.dumps(tweet_features).replace(" ", "")
		}
		tweet_query_url = tweet_url + urllib.parse.urlencode(tweet_query_selection)
		resp = self.session.get(tweet_query_url, headers=self.headers).json()
		tweets = []
		for instruction in resp["data"]["threaded_conversation_with_injections_v2"]["instructions"]:
			if instruction["type"] == "TimelineAddEntries":
				if len(instruction["entries"]) <= 2:
					break
				for entry in instruction["entries"]:
					if entry["entryId"].startswith("tweet-"):
						result = entry["content"]["itemContent"]["tweet_results"]["result"]
						tweets.append(self._parse_tweet_response(result, fetch_replies=fetch_replies))
		return tweets

	def search(self, query, fetch_replies=False):
		"""Search for tweets"""
		query = urllib.parse.quote(query)
		search_url = f"https://twitter.com/i/api/2/search/adaptive.json?include_profile_interstitial_type=1&include_blocking=1&include_blocked_by=1&include_followed_by=1&include_want_retweets=1&include_mute_edge=1&include_can_dm=1&include_can_media_tag=1&include_ext_has_nft_avatar=1&include_ext_is_blue_verified=1&skip_status=1&cards_platform=Web-12&include_cards=1&include_ext_alt_text=true&include_ext_limited_action_results=false&include_quote_count=true&include_reply_count=1&tweet_mode=extended&include_ext_collab_control=true&include_entities=true&include_user_entities=true&include_ext_media_color=true&include_ext_media_availability=true&include_ext_sensitive_media_warning=true&include_ext_trusted_friends_metadata=true&send_error_codes=true&simple_quoted_tweet=true&q={query}&count=20&query_source=typed_query&pc=1&spelling_corrections=1&include_ext_edit_control=true&ext=mediaStats%2ChighlightedLabel%2ChasNftAvatar%2CvoiceInfo%2CbirdwatchPivot%2Cenrichments%2CsuperFollowMetadata%2CunmentionInfo%2CeditControl%2Ccollab_control%2Cvibe"
		resp = self.session.get(search_url, headers=self.headers).json()
		tweets = []
		entries = resp["timeline"]["instructions"][0]["addEntries"]["entries"]
		if len(entries) <= 2:
			return []
		for entry in entries:
			if entry["entryId"].startswith("tweet-"):
				statusId = entry["content"]["item"]["content"]["tweet"]["id"]
				tweets.extend(self.get_tweet(statusId, fetch_replies=fetch_replies))
		return tweets

	def get_user_tweets(self, username, fetch_replies=False):
		"""Get tweets and replies from a user"""
		user_info = self.user_info(username)
		variables = {
			"userId": user_info["id"],
			"count": 100,  # Can't do more than 100 at a time
			"includePromotedContent": True,
			"withQuickPromoteEligibilityTweetFields": True,
			"withSuperFollowsUserFields": True,
			"withDownvotePerspective": False,
			"withReactionsMetadata": False,
			"withReactionsPerspective": False,
			"withSuperFollowsTweetFields": True,
			"withVoice": True,
			"withV2Timeline": True
		}
		features = {
			"responsive_web_twitter_blue_verified_badge_is_enabled": True,
			"verified_phone_label_enabled": False,
			"responsive_web_graphql_timeline_navigation_enabled": True,
			"unified_cards_ad_metadata_container_dynamic_card_content_query_enabled": True,
			"tweetypie_unmention_optimization_enabled": True,
			"responsive_web_uc_gql_enabled": True,
			"vibe_api_enabled": True,
			"responsive_web_edit_tweet_api_enabled": True,
			"graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
			"standardized_nudges_misinfo": True,
			"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
			"interactive_text_enabled": True,
			"responsive_web_text_conversations_enabled": False,
			"responsive_web_enhance_cards_enabled": True
		}
		tweets = []
		cursors = set()
		cursor = None
		while True:
			variables = {**variables, "cursor": cursor} if cursor else variables
			query_selection = {
				'variables': json.dumps(variables).replace(" ", ""),
				'features': json.dumps(features).replace(" ", "")
			}
			tweets_replies_base = "https://twitter.com/i/api/graphql/s0hG9oAmWEYVBqOLJP-TBQ/UserTweetsAndReplies?"
			tweets_replies_url = tweets_replies_base + urllib.parse.urlencode(query_selection)
			resp = self.session.get(tweets_replies_url, headers=self.headers).json()
			# Iterate through all tweets in the response
			for instruction in resp["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]:
				if instruction["type"] == "TimelineAddEntries":
					if len(instruction["entries"]) <= 2:
						break
					for entry in instruction["entries"]:
						if entry["entryId"].startswith("cursor-bottom-"):
							cursor = entry["content"]["value"]
						elif entry["entryId"].startswith("tweet-"):
							result = entry["content"]["itemContent"]["tweet_results"]["result"]
							tweets.append(self._parse_tweet_response(result, fetch_replies=fetch_replies))
			if cursor in cursors:
				break
			cursors.add(cursor)
		return tweets
