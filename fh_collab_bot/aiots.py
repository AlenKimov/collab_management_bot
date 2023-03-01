from typing import Iterable
import aiohttp
import asyncio


async def _get_tweetscout_data(session: aiohttp.ClientSession, twitter_handle: str):
    url = 'https://tweetscout.io/api/v1/accounts/search'
    querystring = {'q': twitter_handle}
    async with session.get(url, params=querystring) as response:
        return await response.json()


async def get_tss(session: aiohttp.ClientSession, twitter_handle: str) -> int:
    data = await _get_tweetscout_data(session, twitter_handle)
    tss = data['score']['value']
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
