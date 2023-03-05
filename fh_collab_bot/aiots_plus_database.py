import aiohttp

from database import insert_project, update_project_tss
from aiots import get_tss


async def insert_project_with_its_tss_getting(session: aiohttp.ClientSession, twitter_handle: str):
    """Добавляет проект в таблицу проектов. Автоматический запрашивает и апдейтит TSS"""
    tss = await get_tss(session, twitter_handle)
    await insert_project(twitter_handle)
    await update_project_tss(twitter_handle, tss)
