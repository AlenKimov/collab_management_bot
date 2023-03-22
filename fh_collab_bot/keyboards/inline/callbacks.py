from aiogram.filters.callback_data import CallbackData


class HideKeyboardCallback(CallbackData, prefix='hide-keyboard'):
    pass


# class ProjectInteractionCallback(CallbackData, prefix='project'):
#     project_twitter_handle: str


class LeadCallback(CallbackData, prefix='lead'):
    project_twitter_handle: str
    want_to_lead: bool


class VoteCallback(CallbackData, prefix='vote'):
    project_twitter_handle: str
    vote_type: int


class DeleteVoteCallback(CallbackData, prefix='delete-vote'):
    project_twitter_handle: str


class RequestTSSCallback(CallbackData, prefix='request-tss'):
    project_twitter_handle: str
