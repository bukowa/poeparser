import asyncio
import itertools
import logging
import re

import aiohttp

import constants
import queues


class PoeApiRateLimitExceeded(Exception):
    """
    {"error":{"code":3,"message":"Rate limit exceeded;
    You are requesting stashes frequently. Please try again later."}}
    """


class PoeBotError(Exception):
    pass


class Parser:
    """
    Base worker that handles all parsing logic.
    """
    __newid = itertools.count()  # counter for unique names

    def __init__(self, session, id_queue, item_queue, proxy_queue=None):

        self.session: aiohttp.ClientSession = session
        self.id_queue: queues.RedisSetQueue = id_queue
        self.item_queue: queues.RedisListQueue = item_queue
        self.proxy_queue = proxy_queue

        self.use_proxy = True if self.proxy_queue else False

        # logging
        self.name = str(__class__.__newid.__next__()) + f' {self.__class__.__name__}'
        self._logger = logging.getLogger(self.name)

    @staticmethod
    def get_api_url(id_):
        return constants.poeapi_url.format(id_)

    async def get_id_from_poeninja(self):
        data = await self.fetch_json(constants.poeninja_url)
        return data[constants.next_id]

    async def fetch_json(self, *args, **kwargs) -> dict:
        if self.use_proxy:
            kwargs['proxy'] = await self.proxy_queue.get()
        async with self.session.get(*args, **kwargs) as resp:
            return await resp.json()

    async def get_connection_kwargs(self, next_change_id, **kwargs):
        """"""
        kwargs['url'] = self.get_api_url(next_change_id)
        if self.use_proxy:
            self._logger.debug(f'Awaiting proxy from {self.proxy_queue}')
            kwargs['proxy'] = await self.proxy_queue.get()
            self._logger.debug(f'Received {kwargs.get("proxy")}')

        return kwargs

    async def fetch_chunks(self):
        """
        Main logic.
        """
        self._logger.debug(f'Awaiting next_change_id from {self.id_queue}')
        current_change_id = await self.id_queue.get()
        self._logger.debug(f'Received {current_change_id}')

        conn_kwargs = await self.get_connection_kwargs(current_change_id)
        self._logger.info(f'Fetching for {conn_kwargs}')

        try:
            chunks = []
            is_first_chunk = True

            async with self.session.get(**conn_kwargs) as resp:
                async for chunk in resp.content.iter_any():

                    self._logger.debug('Received chunk.')
                    chunks.append(chunk)

                    if is_first_chunk:
                        is_first_chunk = False

                        self._logger.debug(f'This is first chunk. Parsing next_change_id.')
                        next_change_id = await self.handle_first_chunk(chunk)

                        self._logger.info(f'{next_change_id} from first chunk, inserting into queue')
                        await self.id_queue.put(next_change_id)

        except Exception as e:
            await self.handle_errors(e, current_change_id)

        else:
            self._logger.info(f'Handling all chunks... {len(chunks)}')
            await self.handle_all_chunks(chunks)

    async def handle_errors(self, exc, current_change_id):
        self._logger.info(f'Received error, inserting {current_change_id} into queue.')
        await self.id_queue.put(current_change_id)

        if isinstance(exc, PoeApiRateLimitExceeded):
            self._logger.error(exc)
            if not self.use_proxy:
                await asyncio.sleep(constants.wait_time)
        else:
            self._logger.exception(exc)

    async def handle_first_chunk(self, chunk):

        chunk = chunk.decode('utf-8')
        ids = re.findall(constants.regx, chunk)

        if len(ids) == 0:
            if 'Rate limit exceeded; You are requesting stashes frequently. Please try again later' in chunk:
                raise PoeApiRateLimitExceeded(chunk)
            else:
                raise PoeBotError

        next_change_id = ids[0]
        return next_change_id

    async def handle_all_chunks(self, chunks):
        chunks = [c.decode('utf-8') for c in chunks]
        await self.item_queue.put(''.join(chunks))

    async def parse_api_loop(self, wait_for=0.3):
        while True:
            try:
                self._logger.debug(f'Waiting for {wait_for} before starting...')
                await asyncio.sleep(wait_for)
                self._logger.debug(f'Starting...')
                await self.fetch_chunks()
                self._logger.debug(f'Done...')
            except PoeBotError as e:
                self._logger.exception(e)
                continue

