from pprint import pprint

# Third-party libraries
from aiogram.types import CallbackQuery, Message
import aiohttp

# Libraries of this project
# -- base
from fh_collab_bot.logger import logger
# -- database
from fh_collab_bot.database import get_projects_of_manager_with_votes
from fh_collab_bot.database import get_project_data_with_votes
from fh_collab_bot.database import are_projects_in_table
from fh_collab_bot.database import update_project_manager_telegram_id
from fh_collab_bot.database import update_project_tss
from fh_collab_bot.database import change_vote, delete_vote
from fh_collab_bot.database import insert_project
from fh_collab_bot.aiots_plus_database import insert_project_with_its_tss_getting
# -- other
from fh_collab_bot.utils import to_twitter_handles
from fh_collab_bot.view import full_project_data_representation
from fh_collab_bot.aiots import get_tss
# -- aiogram
from fh_collab_bot.loader import dp, bot
from fh_collab_bot.keyboards.inline.project_management_buttons import create_project_management_inline_keyboard
from fh_collab_bot.keyboards.inline.project_management_buttons import new_project_keyboard
from keyboards.inline.callback_data import hide_keyboard_cb
from keyboards.inline.callback_data import lead_project_cb
from keyboards.inline.callback_data import vote_cb, delete_vote_cb
from keyboards.inline.callback_data import request_tss_cb


@dp.message_handler(commands=['my', 'me'])
async def cmd_projects_of_manager_message(message: Message):
    logger.debug(f'Менеджер {message.from_user.id} запросил список своих проектов')
    projects_data = await get_projects_of_manager_with_votes(message.from_user.id)

    for project_data in projects_data.values():
        logger.debug(project_data)
        project_info_message = full_project_data_representation(project_data)
        project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id,
                                                                                      project_data)
        await message.answer(project_info_message, disable_web_page_preview=True,
                             reply_markup=project_management_keyboard)


@dp.callback_query_handler(hide_keyboard_cb.filter())
async def cancel_cb_handler(query: CallbackQuery):
    await query.message.edit_reply_markup(reply_markup=None)


async def update_project_management_keyboard(query: CallbackQuery, project_twitter_handle: str):
    project_data = await get_project_data_with_votes(project_twitter_handle)
    project_data = project_data[project_twitter_handle]
    full_project_info_message = full_project_data_representation(project_data)
    project_management_keyboard = await create_project_management_inline_keyboard(query.from_user.id, project_data)
    await query.message.edit_text(
        full_project_info_message,
        disable_web_page_preview=True,
        reply_markup=project_management_keyboard,
    )


@dp.callback_query_handler(vote_cb.filter())
async def vote_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    vote_type = int(callback_data['vote_type'])
    await change_vote(query.from_user.id, project_twitter_handle, vote_type)
    await update_project_management_keyboard(query, project_twitter_handle)


@dp.callback_query_handler(delete_vote_cb.filter())
async def delete_vote_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    await delete_vote(query.from_user.id, project_twitter_handle)
    await update_project_management_keyboard(query, project_twitter_handle)


@dp.callback_query_handler(lead_project_cb.filter())
async def lead_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    want_to_lead = int(callback_data['want_to_lead'])
    if want_to_lead == 1:
        await update_project_manager_telegram_id(project_twitter_handle, query.from_user.id)
    elif want_to_lead == 0:
        await update_project_manager_telegram_id(project_twitter_handle, None)
    await update_project_management_keyboard(query, project_twitter_handle)


@dp.callback_query_handler(request_tss_cb.filter())
async def request_tss_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=30)
    project_twitter_handle = callback_data['project_twitter_handle']
    project_data = await get_project_data_with_votes(project_twitter_handle)
    project_data = project_data[project_twitter_handle]
    tss_before = project_data['tss']
    async with aiohttp.ClientSession() as session:
        new_tss = await get_tss(session, project_twitter_handle)
    if tss_before != new_tss:
        await update_project_tss(project_twitter_handle, new_tss)
        await update_project_management_keyboard(query, project_twitter_handle)


@dp.message_handler(content_types='text')
async def cmd_check_twitter(message: Message):
    twitter_handles = to_twitter_handles(message.text.split('\n'))
    twitter_handles_with_statuses = await are_projects_in_table(twitter_handles)
    async with aiohttp.ClientSession() as session:
        for handle, is_in_table in twitter_handles_with_statuses.items():
            if not is_in_table:
                await insert_project_with_its_tss_getting(session, handle)
            project_data = await get_project_data_with_votes(handle)
            project_data = project_data[handle]
            project_info_message = full_project_data_representation(project_data)
            logger.debug(project_data)
            project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id,
                                                                                          project_data)
            await message.answer(project_info_message, disable_web_page_preview=True,
                                 reply_markup=project_management_keyboard)
