from typing import Iterable

import aiosqlite

from definitions import DATABASES_DIR


DATABASE_FILENAME = 'db.sqlite3'
DATABASE_FILEPATH = DATABASES_DIR / DATABASE_FILENAME


async def insert_project(twitter_handle: str):
    """Добавляет проект в таблицу проектов"""
    query = f"""
    INSERT INTO project (twitter_handle)
    VALUES (?)
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (twitter_handle,))
            await db.commit()


async def insert_manager(manager_telegram_id: str):
    """Добавляет менеджера в таблицу менеджеров"""
    query = f"""
    INSERT INTO manager (manager_telegram_id)
    VALUES (?)
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (manager_telegram_id,))
            await db.commit()


async def insert_vote(manager_telegram_id: int, twitter_handle: str, vote_type: int):
    """Добавляет менеджера в таблицу менеджеров"""
    query = f"""
    INSERT INTO vote (manager_telegram_id, twitter_handle, vote_type)
    VALUES (?, ?, ?)
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (manager_telegram_id, twitter_handle, vote_type))
            await db.commit()


async def _update_table(table_name: str, field_name: str, primary_key_name: str, field_value, primary_key_value):
    query = f"""
        UPDATE {table_name}
        SET {field_name} = ?
        WHERE {primary_key_name} = ?
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (field_value, primary_key_value))
            await db.commit()


async def update_project_table(field_name: str, field_value, primary_key_value: str):
    await _update_table('project', field_name, 'twitter_handle', field_value, primary_key_value)


async def update_project_discord_url(twitter_handle: str, discord_url: str | None):
    await update_project_table('discord_url', discord_url, twitter_handle)


async def update_project_discord_admin_nickname(twitter_handle: str, discord_admin_nickname: str | None):
    await update_project_table('discord_admin_nickname', discord_admin_nickname, twitter_handle)


async def update_project_tss(twitter_handle: str, tss: int | None):
    await update_project_table('tss', tss, twitter_handle)


async def update_project_note(twitter_handle: str, note: str | None):
    await update_project_table('note', note, twitter_handle)


async def update_project_manager_telegram_id(twitter_handle: str, manager_telegram_id: int | None):
    await update_project_table('manager_telegram_id', manager_telegram_id, twitter_handle)


async def update_manager_table(field_name: str, field_value, primary_key_value: int):
    await _update_table(
        'manager', field_name, 'telegram_id',
        field_value, primary_key_value,
    )


async def change_vote(manager_telegram_id: int, twitter_handle: str, vote_type: int):
    query = f"""
        INSERT INTO vote (manager_telegram_id, project_twitter_handle, vote_type) 
        VALUES (?, ?, ?) 
        ON CONFLICT DO UPDATE
        SET vote_type = excluded.vote_type;
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (manager_telegram_id, twitter_handle, vote_type))
        await db.commit()


async def delete_project(twitter_handle: str):
    """Удаляет голос из таблицы голосов"""
    query = f"""
        DELETE FROM project
        WHERE twitter_handle = ?
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (twitter_handle, ))
            await db.commit()


async def delete_manager(manager_telegram_id: int):
    """Удаляет менеджера из таблицы менеджеров"""
    query = f"""
        DELETE FROM manager
        WHERE manager_telegram_id = ?
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (manager_telegram_id, ))
            await db.commit()


async def delete_vote(manager_telegram_id: int, twitter_handle: str):
    """Удаляет голос из таблицы голосов"""
    query = f"""
        DELETE FROM vote
        WHERE manager_telegram_id = ? AND project_twitter_handle = ?
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            await cursor.execute(query, (manager_telegram_id, twitter_handle))
        await db.commit()


async def get_project_data(twitter_handle: str) -> dict[str: dict]:
    """Возвращает данные об определенном проекте"""
    projects_data = {}
    query = f"""
    SELECT *
    FROM project
    WHERE twitter_handle = ?
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (twitter_handle, ))
            fieldnames = [f[0] for f in result.description]
            values = await result.fetchone()
            if values is not None:
                values = list(values)
                data = {}
                for i in range(len(fieldnames)):
                    data[fieldnames[i]] = values[i]
                projects_data.update({data['twitter_handle']: data})
    return projects_data


async def get_project_data_with_votes(twitter_handle: str) -> dict[str: dict]:
    """Возвращает данные об определенном проекте"""
    projects_data = {}
    query = f"""
    SELECT *, 
    (SELECT COUNT(*)
     FROM vote
     WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 1) AS likes,
    (SELECT COUNT(*)
     FROM vote
     WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 0) AS dislikes
    FROM project
    WHERE twitter_handle = ?
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (twitter_handle, ))
            fieldnames = [f[0] for f in result.description]
            values = await result.fetchone()
            if values is not None:
                values = list(values)
                data = {}
                for i in range(len(fieldnames)):
                    data[fieldnames[i]] = values[i]
                projects_data.update({data['twitter_handle']: data})
    return projects_data


async def get_projects_of_manager(manager_telegram_id: int) -> dict[str: dict]:
    projects_data = {}
    query = f"""
        SELECT *
        FROM project
        WHERE manager_telegram_id = ?
        """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (manager_telegram_id, ))
            fieldnames = [f[0] for f in result.description]
            values_list = await result.fetchall()
            for values in values_list:
                if values is not None:
                    values = list(values)
                    data = {}
                    for i in range(len(fieldnames)):
                        data[fieldnames[i]] = values[i]
                    projects_data.update({data['twitter_handle']: data})
    return projects_data


async def get_projects_of_manager_with_votes(manager_telegram_id: int) -> dict[str: dict]:
    projects_data = {}
    query = f"""
    SELECT *, 
    (SELECT COUNT(*)
     FROM vote
     WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 1) AS likes,
    (SELECT COUNT(*)
     FROM vote
     WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 0) AS dislikes
    FROM project
    WHERE manager_telegram_id = ?
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (manager_telegram_id, ))
            fieldnames = [f[0] for f in result.description]
            values_list = await result.fetchall()
            for values in values_list:
                if values is not None:
                    values = list(values)
                    data = {}
                    for i in range(len(fieldnames)):
                        data[fieldnames[i]] = values[i]
                    projects_data.update({data['twitter_handle']: data})
    return projects_data


async def get_vote(project_twitter_handle: str, manager_telegram_id: int) -> dict | None:
    vote_data = None
    query = """
    SELECT *
    FROM vote
    WHERE manager_telegram_id = ? 
        AND project_twitter_handle = ?
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (manager_telegram_id, project_twitter_handle))
            fieldnames = [f[0] for f in result.description]
            values = await result.fetchone()
            if values is not None:
                values = list(values)
                data = {}
                for i in range(len(fieldnames)):
                    data[fieldnames[i]] = values[i]
                vote_data = data
    return vote_data


async def get_interesting_projects(n: int = 10) -> dict[str: dict]:
    """**Сначала интересные**

    Возвращает {n} проектов без ведущих, без дизлайков, в порядке убывания лайков и в порядке убывания TSS.
    """
    projects_data = {}
    query = f"""
        SELECT *, 
        (SELECT COUNT(*)
         FROM vote
         WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 1) AS likes,
        (SELECT COUNT(*)
         FROM vote
         WHERE vote.project_twitter_handle = project.twitter_handle AND vote.vote_type = 0) AS dislikes
        FROM project
        WHERE project.manager_telegram_id IS NULL
              AND dislikes=0
        ORDER BY likes DESC, project.tss DESC
        LIMIT ?
    """
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            result = await cursor.execute(query, (n, ))
            fieldnames = [f[0] for f in result.description]
            values_list = await result.fetchall()
            for values in values_list:
                if values is not None:
                    values = list(values)
                    data = {}
                    for i in range(len(fieldnames)):
                        data[fieldnames[i]] = values[i]
                    projects_data.update({data['twitter_handle']: data})
    return projects_data


async def are_projects_in_table(twitter_handles: Iterable[str]) -> dict[str: bool]:
    query = """SELECT EXISTS(SELECT twitter_handle FROM project WHERE twitter_handle = ?)"""
    answers = {}
    async with aiosqlite.connect(DATABASE_FILEPATH) as db:
        async with db.cursor() as cursor:
            for handle in twitter_handles:
                cursor = await cursor.execute(query, (handle, ))
                answer = await cursor.fetchone()
                answer = bool(answer[0])
                answers.update({handle: answer})
    return answers
