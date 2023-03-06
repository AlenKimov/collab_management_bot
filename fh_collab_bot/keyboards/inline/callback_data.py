from aiogram.utils.callback_data import CallbackData

add_and_lead_project_cb = CallbackData('add-and-lead', 'project_twitter_handle')
lead_project_cb = CallbackData('lead', 'want_to_lead', 'project_twitter_handle')
delete_vote_cb = CallbackData('delete-vote', 'project_twitter_handle')
vote_cb = CallbackData('vote', 'vote_type', 'project_twitter_handle')
