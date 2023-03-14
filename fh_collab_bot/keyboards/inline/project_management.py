from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Libraries of this project
# -- database
from fh_collab_bot.models import Project, Manager, Vote
from fh_collab_bot.database import DatabaseSession

# TODO Не используется: удалить
# new_project_keyboard = InlineKeyboardMarkup(
#     inline_keyboard=[
#         [
#             InlineKeyboardButton(text='SKIP', callback_data='skip'),
#             InlineKeyboardButton(text='ADD',  callback_data='add'),
#             InlineKeyboardButton(text='LEAD', callback_data='add-and-lead'),
#         ]
#     ],
#     one_time_keyboard=True,
# )


async def create_project_management_inline_keyboard(
        manager_telegram_id: int, project: Project
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    session = DatabaseSession()
    vote: Vote = session.query(Vote)\
        .filter_by(manager_telegram_id=manager_telegram_id, project_twitter_handle=project.twitter_handle)\
        .scalar()

    # Далее: "этот менеджер" — менеджер, который запросил информацию об этом проекте и вызвал эту клавиатуру
    # Здесь проверяется, есть ли у проекта ведущий.
    #   Если нет — то сформировать кнопку для возможности начать вести проект
    #   Если есть и это этот менеджер, то сформировать кнопку для прекращения ведения проекта
    #   Если есть и это другой менеджер, то кнопки быть не должно
    if project.manager_telegram_id is None:
        lead_button = InlineKeyboardButton(text='LEAD', callback_data=f'lead:1:{project.twitter_handle}')
        keyboard.insert(lead_button)
    elif project.manager_telegram_id == manager_telegram_id:
        lead_button = InlineKeyboardButton(text='STOP LEADING', callback_data=f'lead:0:{project.twitter_handle}')
        keyboard.insert(lead_button)
    else:
        pass

    # Здесь проверяется, поставил ли этот менеджер лайк или дизлайк
    #   Если нет, то сформировать обе кнопки: LIKE и DISLIKE
    #   Если поставил что-то из двух, то не формировать вторую кнопку, а рядом с первой поставить галочку
    if vote is None:
        like_button = InlineKeyboardButton(text='LIKE', callback_data=f'vote:1:{project.twitter_handle}')
        dislike_button = InlineKeyboardButton(text='DISLIKE', callback_data=f'vote:0:{project.twitter_handle}')
        keyboard.insert(like_button)
        keyboard.insert(dislike_button)
    elif vote.vote_type == 0:
        delete_vote_button = InlineKeyboardButton(text='✓ DISLIKE', callback_data=f'delete-vote:{project.twitter_handle}')
        keyboard.insert(delete_vote_button)
    elif vote.vote_type == 1:
        delete_vote_button = InlineKeyboardButton(text='✓ LIKE', callback_data=f'delete-vote:{project.twitter_handle}')
        keyboard.insert(delete_vote_button)

    request_tss_button = InlineKeyboardButton(text='TSS', callback_data=f'request-tss:{project.twitter_handle}')
    keyboard.insert(request_tss_button)

    cancel_button = InlineKeyboardButton(text='Скрыть клавиатуру', callback_data='hide-keyboard')
    keyboard.insert(cancel_button)

    return keyboard
