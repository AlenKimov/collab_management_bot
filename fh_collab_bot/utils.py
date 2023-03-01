import re


TWITTER_HANDLE_PATTERN = re.compile(r'^(?:.*?\btwitter\.com\/)?@?(\w{1,15})(?:[?\/,].*)?$')


def to_twitter_handle(twitter: str) -> str or None:
    """
    Далее: Twitter handle == никнейм

    Длина никнейма не может быть более 15 символов

    На вход могут поступить строки следующего вида:
    - https://twitter.com/elonmusk
    - https://twitter.com/@elonmusk
    - https://twitter.com/elonmusk?lang=en
    - https://twitter.com/@elonmusk?lang=en
    - @elonmusk
    - elonmusk

    :param twitter: Предполагаемый Twitter аккаунт
    :return: Twitter handle без @
    """
    if not twitter: return None
    twitter = twitter.strip()
    match = TWITTER_HANDLE_PATTERN.search(twitter)
    if match: return match.group(1)
    else: return None


def to_twitter_handles(twitters: list[str]) -> set:
    """
    Далее: Twitter handle == никнейм

    Дополнительно убирает на дубликаты

    :param twitters: Список предполагаемых Twitter аккаунтов
    :return: список никнеймов без @
    """
    twitter_handles = set()
    for twitter in twitters:
        handle = to_twitter_handle(twitter)
        if handle is not None: twitter_handles.add(handle)
    return twitter_handles
