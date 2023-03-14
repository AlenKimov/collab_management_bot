from aiogram.types import CallbackQuery, Message
import aiohttp

# Libraries of this project
from fh_collab_bot.logger import logger
from fh_collab_bot.utils import to_twitter_handles
from fh_collab_bot.aiots import get_tss
# -- database
from fh_collab_bot.models import Project, Manager, Vote
from fh_collab_bot.database import DatabaseSession
# -- aiogram
from fh_collab_bot.loader import dp, bot
from fh_collab_bot.keyboards.inline.project_management import create_project_management_inline_keyboard
from keyboards.inline.callback_data import hide_keyboard_cb
from keyboards.inline.callback_data import lead_project_cb
from keyboards.inline.callback_data import vote_cb, delete_vote_cb
from keyboards.inline.callback_data import request_tss_cb


@dp.message_handler(commands=['my', 'me'])
async def cmd_my_projects(message: Message):
    """Выводит список всех взятыых менеджером проектов, отсортированных по дате взятия"""
    with DatabaseSession() as db_session:
        manager: Manager = db_session.query(Manager).filter_by(telegram_id=message.from_user.id).scalar()
        projects: list[Project] = manager.projects
        for project in projects:
            logger.debug(f'Командой {message.text}'
                         f' менеджер {message.from_user.id} (@{message.from_user.username})'
                         f' запросил {project}')
            project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id, project)
            await message.answer(project.get_full_info(), disable_web_page_preview=True,
                                 reply_markup=project_management_keyboard)


@dp.message_handler(commands=['best'])
async def cmd_best_projects(message: Message):
    """Выводит список из 10-ти никем не взятых проектов в порядке убывания лайков и в порядке убывания TSS"""
    with DatabaseSession() as db_session:
        projects: list[Project] = (
            db_session.query(Project)
            .filter_by(manager_telegram_id=None)
            .order_by(Project.likes.desc())
            .order_by(Project.tss.desc())
            .limit(10)
            .all()
        )
        for project in projects:
            logger.debug(f'Командой {message.text}'
                         f' менеджер {message.from_user.id} (@{message.from_user.username})'
                         f' запросил {project}')
            project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id, project)
            await message.answer(project.get_full_info(), disable_web_page_preview=True,
                                 reply_markup=project_management_keyboard)


@dp.message_handler(commands=['new'])
async def cmd_best_projects(message: Message):
    """Выводит список из 10-ти никем не взятых проектов без оценок,
    отсортированных по новизне и в порядке убывания TSS"""
    with DatabaseSession() as db_session:
        projects: list[Project] = (
            db_session.query(Project)
            .filter_by(manager_telegram_id=None)
            .filter_by(likes=0, dislikes=0)
            .order_by(Project.created_at.desc())
            .order_by(Project.tss.desc())
            .limit(10)
            .all()
        )
        for project in projects:
            logger.debug(f'Командой {message.text}'
                         f' менеджер {message.from_user.id} (@{message.from_user.username})'
                         f' запросил {project}')
            project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id, project)
            await message.answer(project.get_full_info(), disable_web_page_preview=True,
                                 reply_markup=project_management_keyboard)


@dp.callback_query_handler(hide_keyboard_cb.filter())
async def cancel_cb_handler(query: CallbackQuery):
    await query.message.edit_reply_markup(reply_markup=None)


async def update_project_management_keyboard(query: CallbackQuery, project: Project):
    project_management_keyboard = await create_project_management_inline_keyboard(query.from_user.id, project)
    await query.message.edit_text(project.get_full_info(), disable_web_page_preview=True,
                                  reply_markup=project_management_keyboard)


@dp.callback_query_handler(vote_cb.filter())
async def vote_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    vote_type = int(callback_data['vote_type'])
    with DatabaseSession() as db_session:
        db_session.merge(Vote(manager_telegram_id=query.from_user.id, project_twitter_handle=project_twitter_handle,
                              vote_type=vote_type))
        db_session.commit()
        project: Project = db_session.query(Project).filter_by(twitter_handle=project_twitter_handle).scalar()
        await update_project_management_keyboard(query, project)


@dp.callback_query_handler(delete_vote_cb.filter())
async def delete_vote_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    with DatabaseSession() as db_session:
        vote: Vote = db_session.query(Vote).filter_by(manager_telegram_id=query.from_user.id,
                                                      project_twitter_handle=project_twitter_handle).scalar()
        db_session.delete(vote)
        db_session.commit()
        project: Project = db_session.query(Project).filter_by(twitter_handle=project_twitter_handle).scalar()
        await update_project_management_keyboard(query, project)


@dp.callback_query_handler(lead_project_cb.filter())
async def lead_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=1)
    project_twitter_handle = callback_data['project_twitter_handle']
    want_to_lead = int(callback_data['want_to_lead'])
    with DatabaseSession() as db_session:
        project: Project = db_session.query(Project).filter_by(twitter_handle=project_twitter_handle).scalar()
        if want_to_lead == 1:
            project.manager_telegram_id = query.from_user.id
            db_session.commit()
        elif want_to_lead == 0:
            project.manager_telegram_id = None
            db_session.commit()
        await update_project_management_keyboard(query, project)


@dp.callback_query_handler(request_tss_cb.filter())
async def request_tss_cb_handler(query: CallbackQuery, callback_data: dict):
    await query.answer(cache_time=60)
    project_twitter_handle = callback_data['project_twitter_handle']
    with DatabaseSession() as db_session:
        project: Project = db_session.query(Project).filter_by(twitter_handle=project_twitter_handle).scalar()
        async with aiohttp.ClientSession() as session:
            new_tss = await get_tss(session, project_twitter_handle)
        if project.tss != new_tss:
            project.tss = new_tss
            db_session.commit()
            await update_project_management_keyboard(query, project)


@dp.message_handler(content_types='text')
async def cmd_check_twitter(message: Message):
    twitter_handles = to_twitter_handles(message.text.split('\n'))
    logger.debug(f'Менеджер {message.from_user.id} (@{message.from_user.username})'
                 f' внес следующие проекты: {twitter_handles}')
    with DatabaseSession() as db_session:
        async with aiohttp.ClientSession() as session:
            for twitter_handle in twitter_handles:
                is_in_table = db_session.query(
                    db_session.query(Project).filter_by(twitter_handle=twitter_handle).exists()
                ).scalar()
                if not is_in_table:
                    tss = await get_tss(session, twitter_handle)
                    project = Project(twitter_handle=twitter_handle, tss=tss)
                    db_session.add(project)
                    db_session.commit()
                else:
                    project: Project = db_session.query(Project).filter_by(twitter_handle=twitter_handle).scalar()
                project_management_keyboard = await create_project_management_inline_keyboard(message.from_user.id, project)
                await message.answer(project.get_full_info(), disable_web_page_preview=True,
                                     reply_markup=project_management_keyboard)
