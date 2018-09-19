
botname = 'poeparser'
poeapi_url = 'http://api.pathofexile.com/public-stash-tabs/?id={}'
poeninja_url = 'https://poe.ninja/api/Data/GetStats'
next_id = 'next_change_id'
regx = r'(?<=\"next_change_id\":)\"(.*?)\"'


redis_kwargs = {
    'address': 'redis://redis',
    'db': 2,
    'encoding': 'utf-8',
}

headers = {
    'Accept-Encoding': 'gzip',
    'User-Agent': ''
}

wait_time = 25  # time to wait if too many requests

