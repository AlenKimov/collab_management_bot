from datetime import datetime, timedelta

from aiogram import Router
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, exists

# Libraries of this project
from bot.logger import logger
from bot.utils import to_twitter_handles
# -- database
from bot.models import Project, Manager, Vote
# -- aiogram
from bot.filters import ManagerFilter
from bot.keyboards.inline.project_management import create_project_management_inline_keyboard
from bot.keyboards.inline.callbacks import HideKeyboardCallback
from bot.keyboards.inline.callbacks import LeadCallback
from bot.keyboards.inline.callbacks import VoteCallback, DeleteVoteCallback
from bot.keyboards.inline.callbacks import RequestTSSCallback


router = Router()
router.message.filter(ManagerFilter())


MANAGER_COMMANDS_HELP_MESSAGE = """
/my — выводит список всех взятых менеджером проектов, 
отсортированных по дате взятия.
/best — выводит список из 5-ти никем не взятых проектов 
в порядке убывания лайков и в порядке убывания TSS. 
Не выводит проекты, добавленные менее 5 минут назад.
/new — выводит список из 5-ти никем не взятых проектов 
без оценок, отсортированных по новизне и в порядке убывания TSS. 
Не выводит проекты, добавленные менее 5 минут назад.
/set_username — заносит Telegram Handle менеджера в базу. 
Теперь вместо Telegram ID на месте, где указывается менеджер, 
будет указан его Telegram Handle. Если менеджер изменил свой Telegram Handle, 
ему нужно снова ввести эту команду.
"""


@router.message(Command('help'))
async def start_message(message: Message):
    await message.answer(f'<b>Список доступных команд:</b>\n'
                         f'{MANAGER_COMMANDS_HELP_MESSAGE}')


@router.message(Command('start'))
async def start_message(message: Message):
    await message.answer('Привет! Можешь начинать пользоваться ботом, ты уже в базе.\n'
                         'Список доступных команд: /help')


@router.message(Command('me', 'my'))
async def cmd_my_projects(message: Message, session: AsyncSession):
    """Выводит список всех взятыых менеджером проектов,
    отсортированных по дате взятия"""
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{manager.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    async for project in await session.stream_scalars(manager.projects.select()):
        project_management_keyboard = await create_project_management_inline_keyboard(
            session, message.from_user.id, project)
        await message.answer(project.get_full_info(), disable_web_page_preview=True,
                             reply_markup=project_management_keyboard)


@router.message(Command('best'))
async def cmd_best_projects(message: Message, session: AsyncSession):
    """Выводит список из 10-ти никем не взятых проектов
    в порядке убывания лайков и в порядке убывания TSS

    Не выводит проекты, добавленные менее 5 минут назад.
    """
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{manager.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    now = datetime.utcnow()
    five_minutes_ago = now - timedelta(minutes=5)

    best_projects_query = (
        select(Project)
        .filter_by(manager_telegram_id=None)
        .filter_by(dislikes=0)
        .filter(Project.created_at < five_minutes_ago)
        .order_by(Project.likes.desc())
        .order_by(Project.tss.desc())
        .limit(5)
    )
    async for project in await session.stream_scalars(best_projects_query):
        project_management_keyboard = await create_project_management_inline_keyboard(
            session, message.from_user.id, project)
        await message.answer(project.get_full_info(), disable_web_page_preview=True,
                             reply_markup=project_management_keyboard)


@router.message(Command('new'))
async def cmd_best_projects(message: Message, session: AsyncSession):
    """Выводит список из 10-ти никем не взятых проектов без оценок,
    отсортированных по новизне и в порядке убывания TSS

    Не выводит проекты, добавленные менее 5 минут назад.
    """
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{manager.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    now = datetime.utcnow()
    five_minutes_ago = now - timedelta(minutes=5)

    best_projects_query = (
        select(Project)
        .filter_by(manager_telegram_id=None)
        .filter_by(likes=0, dislikes=0)
        .filter(Project.created_at < five_minutes_ago)
        .order_by(Project.created_at.desc())
        .order_by(Project.tss.desc())
        .limit(5)
    )
    async for project in await session.stream_scalars(best_projects_query):
        project_management_keyboard = await create_project_management_inline_keyboard(
            session, message.from_user.id, project)
        await message.answer(project.get_full_info(), disable_web_page_preview=True,
                             reply_markup=project_management_keyboard)


@router.message(Command('set_username'))
async def cmd_set_handle(message: Message, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{manager.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    manager.telegram_handle = message.from_user.username
    await session.commit()
    await message.answer('Имя пользователя успешно установлено!')


@router.callback_query(HideKeyboardCallback.filter())
async def hide_keyboard_cb_handler(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer(text='Клавиатура спрятана')


async def update_project_management_keyboard(session: AsyncSession, callback: CallbackQuery, project: Project):
    project_management_keyboard = await create_project_management_inline_keyboard(
        session, callback.from_user.id, project)
    await callback.message.edit_text(project.get_full_info(), disable_web_page_preview=True,
                                     reply_markup=project_management_keyboard)


@router.callback_query(VoteCallback.filter())
async def vote_cb_handler(callback: CallbackQuery, callback_data: VoteCallback, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=callback.from_user.id))

    info_message = f'{manager.get_full_info()} поставил оценку следующему проекту: {callback_data.project_twitter_handle}'
    logger.info(info_message)

    await session.merge(Vote(manager_telegram_id=callback.from_user.id,
                             project_twitter_handle=callback_data.project_twitter_handle,
                             vote_type=callback_data.vote_type))
    await session.commit()
    project_query = select(Project).filter_by(twitter_handle=callback_data.project_twitter_handle)
    project = await session.scalar(project_query)
    await update_project_management_keyboard(session, callback, project)
    await callback.answer(cache_time=2)


@router.callback_query(DeleteVoteCallback.filter())
async def delete_vote_cb_handler(callback: CallbackQuery, callback_data: DeleteVoteCallback, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=callback.from_user.id))

    info_message = f'{manager.get_full_info()} снял оценку следующего проекта: {callback_data.project_twitter_handle}'
    logger.info(info_message)

    vote_query = select(Vote).filter_by(manager_telegram_id=callback.from_user.id,
                                        project_twitter_handle=callback_data.project_twitter_handle)
    vote: Vote = await session.scalar(vote_query)
    if vote is not None:
        await session.delete(vote)
        await session.commit()
        project_query = select(Project).filter_by(twitter_handle=callback_data.project_twitter_handle)
        project: Project = await session.scalar(project_query)
        await update_project_management_keyboard(session, callback, project)
    await callback.answer(cache_time=1)


@router.callback_query(LeadCallback.filter())
async def lead_cb_handler(callback: CallbackQuery, callback_data: LeadCallback, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=callback.from_user.id))

    project_query = select(Project).filter_by(twitter_handle=callback_data.project_twitter_handle)
    project = await session.scalar(project_query)
    if callback_data.want_to_lead:
        project.manager_telegram_id = callback.from_user.id
        info_message = f'{manager.get_full_info()} теперь ведет следующий проекта: {callback_data.project_twitter_handle}'
    else:
        project.manager_telegram_id = None
        info_message = f'{manager.get_full_info()} больше не ведет следующий проекта: {callback_data.project_twitter_handle}'
    logger.info(info_message)
    await update_project_management_keyboard(session, callback, project)
    await session.commit()
    await callback.answer(cache_time=1)


@router.callback_query(RequestTSSCallback.filter())
async def request_tss_cb_handler(callback: CallbackQuery, callback_data: RequestTSSCallback, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=callback.from_user.id))

    info_message = f'{manager.get_full_info()} запросил TSS следующего проекта: {callback_data.project_twitter_handle}'
    logger.info(info_message)

    project_query = select(Project).filter_by(twitter_handle=callback_data.project_twitter_handle)
    project: Project = await session.scalar(project_query)

    old_tss = project.tss
    await project.refresh_tss()

    if old_tss != project.tss:
        await update_project_management_keyboard(session, callback, project)

    await callback.answer(cache_time=3)
    await session.commit()


@router.message(F.text)
async def cmd_check_twitter(message: Message, session: AsyncSession):
    manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))
    twitter_handles = to_twitter_handles(message.text.split('\n'))

    info_message = f'{manager.get_full_info()} запросил следующие проекты: {", ".join(twitter_handles)}'
    logger.info(info_message)

    for twitter_handle in twitter_handles:
        project_query = select(Project).filter_by(twitter_handle=twitter_handle)
        project_exists_query = exists(project_query).select()
        is_in_table = await session.scalar(project_exists_query)
        if not is_in_table:
            project = Project(twitter_handle=twitter_handle)
            await project.refresh_tss()
            session.add(project)
            logger.info(f'Новый проект: {twitter_handle}. Его TSS: {project.tss}')
        else:
            project: Project = await session.scalar(project_query)
        project_management_keyboard = await create_project_management_inline_keyboard(
            session, message.from_user.id, project)
        await message.answer(project.get_full_info(), disable_web_page_preview=True,
                             reply_markup=project_management_keyboard)
    await session.commit()
