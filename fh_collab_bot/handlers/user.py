from aiogram import Router, html
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fh_collab_bot.models import Manager

router = Router()


@router.message(Command('help', 'start'))
async def start_message(message: Message, session: AsyncSession):
    admins_telegram_handles = await session.scalars(select(Manager.telegram_handle).filter_by(is_admin=True))
    if admins_telegram_handles:
        with_at = [f'@{handle}' for handle in admins_telegram_handles]
        await message.answer(f'Твой Telegram ID: {html.code(str(message.from_user.id))}\n'
                             f'Если ты считаешь, что достоин мной пользоваться, напиши одному из администраторов:\n'
                             f'{", ".join(with_at)}')
    else:
        await message.answer(f'Твой Telegram ID: {message.from_user.id}')


@router.message(Command('my', 'best', 'new'))
async def unavailable_commands(message: Message):
    await message.reply('Эта команда доступна только менеджерам!\n'
                        'Как стать менеджером: /help')
