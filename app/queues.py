import asyncio


def _insert_to_args(t, obj, n):
    t = list(t)
    t.insert(n, obj)
    return tuple(t)


class RedisQueue:
    """
    Asyncio compatible Redis Queue.
    """
    _put_cmd = ''
    _get_cmd = ''
    _allownull = False

    def __init__(self, redis, key):
        self._redis = redis
        self.key = key

    async def _call_redis(self, cmd, *args, **kwargs):
        func = getattr(self._redis, cmd)
        return await func(self.key, *args, **kwargs)

    async def put(self, member, *args, **kwargs):
        return await self._call_redis(self._put_cmd, member, *args, **kwargs)

    async def put_bulk(self, members, *args, **kwargs):
        return await self._call_redis(self._put_cmd, *members, *args, **kwargs)

    async def get(self, *args, **kwargs):
        if self._allownull:
            i = await self._call_redis(self._get_cmd, *args, **kwargs)
            return i

        if not self._allownull:
            while True:
                await asyncio.sleep(0.05)
                i = await self._call_redis(self._get_cmd, *args, **kwargs)
                if i:
                    return i


class RedisSetQueue(RedisQueue):

    _put_cmd = 'sadd'
    _get_cmd = 'spop'


class RedisListQueue(RedisQueue):

    _put_cmd = 'lpush'
    _get_cmd = 'lrange'

    async def get(self, *args, **kwargs):
        """
        We want first element if no args are provided.
        """
        args = args or (0, 0)
        return await super(RedisListQueue, self).get(*args, **kwargs)

