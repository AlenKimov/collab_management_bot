from aiogram.utils.callback_data import CallbackData

hide_keyboard_cb = CallbackData('hide-keyboard')
lead_project_cb = CallbackData('lead', 'want_to_lead', 'project_twitter_handle')
vote_cb = CallbackData('vote', 'vote_type', 'project_twitter_handle')
delete_vote_cb = CallbackData('delete-vote', 'project_twitter_handle')
request_tss_cb = CallbackData('request-tss', 'project_twitter_handle')
