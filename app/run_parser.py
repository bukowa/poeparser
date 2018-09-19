import asyncio
import logging

import aiohttp
import aioredis

import bot
import constants
import queues

logging.basicConfig(level=logging.INFO)


async def run_bot(name, nworkers, wait_for=0.5):

    # HTTP
    session = aiohttp.ClientSession(
        conn_timeout=15,
        read_timeout=15,
        loop=asyncio.get_event_loop(),
        headers=constants.headers
    )

    # REDIS & QUEUES
    redis = await aioredis.create_redis(**constants.redis_kwargs)
    id_queue = queues.RedisSetQueue(redis=redis, key=name + '_id_queue')
    item_queue = queues.RedisListQueue(redis=redis, key=name + '_item_queue')

    # PARSER
    parser = bot.Parser(
        session=session,
        id_queue=id_queue,
        item_queue=item_queue,
    )

    # FETCH FIRST ID
    first_id = await parser.get_id_from_poeninja()
    await id_queue.put(first_id)

    # RUN WORKERS
    for _ in range(nworkers):
        asyncio.ensure_future(parser.parse_api_loop(wait_for=wait_for))


async def main():
    await asyncio.sleep(1)
    await run_bot(name=constants.botname, nworkers=2, wait_for=0.5)

loop = asyncio.get_event_loop()
asyncio.ensure_future(main())
loop.run_forever()
