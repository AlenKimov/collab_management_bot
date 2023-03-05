from aiogram.utils.callback_data import CallbackData

skip_project_cb =         CallbackData('skip')
add_project_cb =          CallbackData('add')
lead_project_cb =         CallbackData('lead', 'project_twitter_handle')
stop_leading_project_cb = CallbackData('stop-leading', 'project_twitter_handle')
add_and_lead_project_cb = CallbackData('add-and-lead', 'project_twitter_handle')
vote_cb =                 CallbackData('vote', 'vote_type', 'project_twitter_handle')
delete_vote_cb =          CallbackData('delete-vote', 'project_twitter_handle')
cancel_cb =               CallbackData('cancel')
