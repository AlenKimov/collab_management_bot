from aiogram import Router, html
from aiogram.types import Message
from aiogram.filters import Command
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.models import Manager

router = Router()


@router.message(Command('help', 'start'))
async def start_message(message: Message, session: AsyncSession):
    stmt = select(Manager.telegram_handle).filter_by(is_admin=True).filter(Manager.telegram_handle != None)
    admins_telegram_handles = (await session.scalars(stmt)).fetchall()
    if admins_telegram_handles:
        with_at = [f'@{handle}' for handle in admins_telegram_handles]
        await message.answer(f'Твой Telegram ID: {html.code(str(message.from_user.id))}\n'
                             f'Чтобы стать менеджером, нужно, '
                             f'чтобы твой Telegram ID внес в базу один из администраторов:\n'
                             f'{", ".join(with_at)}')
    else:
        await message.answer(f'Твой Telegram ID: {html.code(str(message.from_user.id))}\n'
                             f'Чтобы стать менеджером, нужно, '
                             f'чтобы твой Telegram ID внес в базу один из администраторов.')


@router.message(Command('my', 'best', 'new'))
async def unavailable_commands(message: Message):
    await message.reply('Эта команда доступна только менеджерам!\n'
                        'Как стать менеджером: /help')
