from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Libraries of this project
from fh_collab_bot.logger import logger
from fh_collab_bot.utils import to_twitter_handles
# -- database
from fh_collab_bot.models import Project, Manager
# -- aiogram
from fh_collab_bot.filters import AdminFilter, load_manager_ids
from fh_collab_bot.handlers.manager import MANAGER_COMMANDS_HELP_MESSAGE


router = Router()
router.message.filter(AdminFilter())


ADMIN_COMMANDS_HELP_MESSAGE = """
/managers — выводит список всех менеджеров и администраторов.
/add_manager [telegram_id] — добавляет менеджера с указанным Telegram ID.
/delete_managers [telegram_id] — удаляет менеджеров с указанными Telegram ID.
/delete_projects [twitter_handle] — удаляет проекты с указанными Twitter handle.
"""


@router.message(Command('help'))
async def start_message(message: Message):
    await message.answer(f'<b>Список доступных команд:</b>\n'
                         f'{MANAGER_COMMANDS_HELP_MESSAGE}'
                         f'{ADMIN_COMMANDS_HELP_MESSAGE}')


@router.message(Command('start'))
async def start_message(message: Message):
    await message.answer('Здравствуй, повелитель!\n'
                         'Список доступных команд: /help')


@router.message(Command('managers'))
async def cmd_managers(message: Message, session: AsyncSession):
    admin: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{admin.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    result = await session.execute(select(Manager))
    managers = result.scalars()
    for manager in managers:
        await message.answer(manager.get_full_info())


@router.message(Command('delete_projects', 'delete_project'))
async def cmd_delete_project(message: Message, session: AsyncSession, command: CommandObject):
    admin: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{admin.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    if command.args:
        twitter_handles = to_twitter_handles(command.args.split())
        for twitter_handle in twitter_handles:
            project: Project = await session.scalar(select(Project).filter_by(twitter_handle=twitter_handle))
            if project:
                await session.delete(project)
                await session.commit()
                await message.answer(f"<b>{twitter_handle}</b>: проект успешно удален из базы данных!")
            else:
                await message.answer(f"<b>{twitter_handle}</b>: проект не найден")
    else:
        await message.answer("Перечислите Twitter Handles проектов для удаления!")


@router.message(Command('delete_managers', 'delete_manager'))
async def cmd_delete_manager(message: Message, session: AsyncSession, command: CommandObject):
    admin: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{admin.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    if command.args:
        telegram_ids = command.args.split()
        for telegram_id in telegram_ids:
            manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=telegram_id))
            if manager:
                await session.delete(manager)
                await session.commit()
                await message.answer(f"<b>{manager.get_short_info()}</b>: менеджер успешно удален из базы!")
                await load_manager_ids()  # TODO Да это же какой-то костыль!
            else:
                manager = Manager(telegram_id=telegram_id)
                await message.answer(f"<b>{manager.get_short_info()}</b>: менеджер не найден")
    else:
        await message.answer("Предоставьте Telegram ID менеджера для удаления!")


@router.message(Command('add_manager'))
async def cmd_add_manager(message: Message, session: AsyncSession, command: CommandObject):
    admin: Manager = await session.scalar(select(Manager).filter_by(telegram_id=message.from_user.id))

    info_message = f'{admin.get_full_info()} использовал команду {message.text}'
    logger.info(info_message)

    if command.args:
        telegram_id = command.args.split()[0]
        manager: Manager = await session.scalar(select(Manager).filter_by(telegram_id=telegram_id))
        if not manager:
            manager = Manager(telegram_id=telegram_id)
            session.add(manager)
            await message.answer(f"<b>{manager.get_short_info()}</b>: менеджер успешно внесен в базу!")
            await session.commit()
            await load_manager_ids()  # TODO Да это же какой-то костыль!
        else:
            await message.answer(f"<b>{manager.get_short_info()}</b>: менеджер уже в базе!")
    else:
        await message.answer("Предоставьте Telegram ID менеджера для добавления!")
