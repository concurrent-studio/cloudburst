import cloudburst as cb
from cloudburst import social as cbs
from urllib.parse import urlparse, parse_qs

url = "https://www.instagram.com/graphql/query/?query_hash=d04b0a864b4b54837c0d870b0e77e076&variables=%7B%22id%22%3A%2216516077%22%2C%22include_reel%22%3Atrue%2C%22fetch_mutual%22%3Afalse%2C%22first%22%3A24%7D"
print(cb.query_decode(url))

bella = cbs.Instagram("bellahadid") # instantiate new Instagram object
bella.download_posts() # download HD profile image
