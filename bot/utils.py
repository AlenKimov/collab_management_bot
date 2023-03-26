import re


TWITTER_HANDLE_PATTERN = re.compile(r'^(?:.*?\btwitter\.com\/)?@?([a-zA-Z0-9_]{1,15})(?:[?\/,].*)?$')


def to_twitter_handle(twitter: str) -> str or None:
    """
    Длина Twitter handle не может превышать 15 символов

    На вход могут поступить строки следующего вида:
    - https://twitter.com/elonmusk
    - https://twitter.com/@elonmusk
    - https://twitter.com/elonmusk?lang=en
    - https://twitter.com/@elonmusk?lang=en
    - @elonmusk
    - elonmusk

    :param twitter: Ссылка на Twitter аккаунт или Twitter handle
    :return: Twitter handle без @
    """
    if not twitter: return None
    twitter = twitter.strip().lower()
    match = TWITTER_HANDLE_PATTERN.search(twitter)
    if match: return match.group(1)
    else: return None


def to_twitter_handles(twitters: list[str]) -> set:
    """
    Дополнительно убирает на дубликаты

    :param twitters: Список ссылок на Twitter аккауны или список Twitter handle-ов
    :return: Список Twitter handle-ов без @
    """
    twitter_handles = set()
    for twitter in twitters:
        handle = to_twitter_handle(twitter)
        if handle is not None: twitter_handles.add(handle)
    return twitter_handles
