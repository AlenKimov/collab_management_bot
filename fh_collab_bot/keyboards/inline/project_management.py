from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Libraries of this project
# -- database
from fh_collab_bot.models import Project, Vote
# -- aiogram
from fh_collab_bot.keyboards.inline.callbacks import HideKeyboardCallback
from fh_collab_bot.keyboards.inline.callbacks import LeadCallback
from fh_collab_bot.keyboards.inline.callbacks import VoteCallback, DeleteVoteCallback
from fh_collab_bot.keyboards.inline.callbacks import RequestTSSCallback


async def create_project_management_inline_keyboard(
        session: AsyncSession,
        manager_telegram_id: int, project: Project
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    query = select(Vote).filter_by(manager_telegram_id=manager_telegram_id, project_twitter_handle=project.twitter_handle)
    vote = await session.scalar(query)

    if project.manager_telegram_id is None:
        builder.button(text='LEAD',
                       callback_data=LeadCallback(project_twitter_handle=project.twitter_handle,
                                                  want_to_lead=True))
    elif project.manager_telegram_id == manager_telegram_id:
        builder.button(text='STOP LEADING',
                       callback_data=LeadCallback(project_twitter_handle=project.twitter_handle,
                                                  want_to_lead=False))

    if vote is None:
        builder.button(text='LIKE', callback_data=VoteCallback(project_twitter_handle=project.twitter_handle,
                                                               vote_type=1))
        builder.button(text='DISLIKE', callback_data=VoteCallback(project_twitter_handle=project.twitter_handle,
                                                                  vote_type=0))
    elif vote.vote_type == 0:
        builder.button(text='✓ DISLIKE', callback_data=DeleteVoteCallback(project_twitter_handle=project.twitter_handle))
    elif vote.vote_type == 1:
        builder.button(text='✓ LIKE', callback_data=DeleteVoteCallback(project_twitter_handle=project.twitter_handle))

    builder.button(text='TSS', callback_data=RequestTSSCallback(project_twitter_handle=project.twitter_handle))
    builder.button(text='Скрыть', callback_data=HideKeyboardCallback())

    return builder.as_markup()
