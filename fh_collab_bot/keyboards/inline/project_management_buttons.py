from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Libraries of this project
from fh_collab_bot.database import get_vote


new_project_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='SKIP', callback_data='skip'),
            InlineKeyboardButton(text='ADD',  callback_data='add'),
            InlineKeyboardButton(text='LEAD', callback_data='add-and-lead'),
        ]
    ],
    one_time_keyboard=True,
)


async def create_project_management_inline_keyboard(
        manager_telegram_id: int, project_data: dict
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    vote_data = await get_vote(project_data['twitter_handle'], manager_telegram_id)

    project_twitter_handle = project_data['twitter_handle']

    # Далее: "этот менеджер" — менеджер, который запросил информацию об этом проекте и вызвал эту клавиатуру
    # Здесь проверяется, есть ли у проекта ведущий.
    #   Если нет — то сформировать кнопку для возможности начать вести проект
    #   Если есть и это этот менеджер, то сформировать кнопку для прекращения ведения проекта
    #   Если есть и это другой менеджер, то кнопки быть не должно
    if project_data['manager_telegram_id'] is None:
        lead_button = InlineKeyboardButton(text='LEAD', callback_data=f'lead:{project_twitter_handle}')
        keyboard.insert(lead_button)
    elif project_data['manager_telegram_id'] == manager_telegram_id:
        stop_leading_button = InlineKeyboardButton(text='STOP LEADING',
                                                   callback_data=f'stop-leading:{project_twitter_handle}')
        keyboard.insert(stop_leading_button)
    else:
        pass

    # Здесь проверяется, поставил ли этот менеджер лайк или дизлайк
    #   Если нет, то сформировать обе кнопки: LIKE и DISLIKE
    #   Если поставил что-то из двух, то не формировать вторую кнопку, а рядом с первой поставить галочку
    if vote_data is None:
        like_button = InlineKeyboardButton(text='LIKE', callback_data=f'vote:1:{project_twitter_handle}')
        dislike_button = InlineKeyboardButton(text='DISLIKE', callback_data=f'vote:0:{project_twitter_handle}')
        keyboard.insert(like_button)
        keyboard.insert(dislike_button)
    elif vote_data['vote_type'] == 0:
        delete_vote_button = InlineKeyboardButton(text='✓ DISLIKE', callback_data=f'delete-vote:{project_twitter_handle}')
        keyboard.insert(delete_vote_button)
    elif vote_data['vote_type'] == 1:
        delete_vote_button = InlineKeyboardButton(text='✓ LIKE', callback_data=f'delete-vote:{project_twitter_handle}')
        keyboard.insert(delete_vote_button)

    cancel_button = InlineKeyboardButton(text='Погодите-ка..', callback_data='cancel')
    keyboard.insert(cancel_button)

    return keyboard
