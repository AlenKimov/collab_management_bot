from typing import Iterable
import asyncio

import aiohttp
from aiohttp.client_exceptions import ContentTypeError
from asyncio_throttle import Throttler

from logger import logger

throttler = Throttler(rate_limit=1, period=2)


async def _get_tweetscout_data(session: aiohttp.ClientSession, twitter_handle: str) -> dict:
    url = 'https://tweetscout.io/api/v1/accounts/search'
    querystring = {'q': twitter_handle}
    async with throttler:
        async with session.get(url, params=querystring) as response:
            try:
                return await response.json()
            except ContentTypeError as exception:
                logger.exception(exception)
                logger.error(await response.text())
                return {}


async def get_tss(session: aiohttp.ClientSession, twitter_handle: str) -> int | None:
    data = await _get_tweetscout_data(session, twitter_handle)
    if 'score' not in data:
        tss = None
    else:
        tss = int(data['score']['value'])
    return tss


def get_all_data(twitter_handles: Iterable) -> dict:
    async def save_all_information(twitter_handles: Iterable, all_data: dict):
        async with aiohttp.ClientSession() as session:
            for handle in twitter_handles:
                data = await _get_tweetscout_data(session, handle)
                all_data.update({handle: data})

    all_data = {}
    asyncio.run(save_all_information(twitter_handles, all_data))
    return all_data
