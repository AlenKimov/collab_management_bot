-- Таблица менеджеров
CREATE TABLE manager(
    telegram_id BIGINT   NOT NULL PRIMARY KEY,
    created_at  DATETIME NOT NULL DEFAULT (DATETIME('now', '+3 hour')),
    is_admin    INTEGER  NOT NULL CHECK(vote_type BETWEEN 0 AND 1)
);

-- Таблица проектов
CREATE TABLE project(
    twitter_handle         TEXT     NOT NULL PRIMARY KEY,
    created_at             DATETIME NOT NULL DEFAULT (DATETIME('now', '+3 hour')),
    discord_url            TEXT,
    discord_admin_nickname TEXT,
    tss                    INTEGER,
    note                   TEXT,
    manager_telegram_id    REFERENCES manager(telegram_id)
);

-- Таблица лайков и дизлайков
CREATE TABLE IF NOT EXISTS vote(
    manager_telegram_id    REFERENCES manager(telegram_id),
    project_twitter_handle REFERENCES project(twitter_handle),
    vote_type INTEGER CHECK(vote_type BETWEEN 0 AND 1),
    UNIQUE (manager_telegram_id, project_twitter_handle)
);

-- Индексация проектов для более быстрого поиска
CREATE UNIQUE INDEX IF NOT EXISTS project_twitter_handle_unique_index
ON project (twitter_handle);