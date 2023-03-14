from datetime import datetime

from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint, CheckConstraint
from sqlalchemy import DDL, event


class Base(DeclarativeBase):
    pass


class Manager(Base):
    __tablename__ = 'manager'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(default=func.DATETIME('now'))
    is_admin: Mapped[bool] = mapped_column(default=False)

    projects: Mapped[list['Project']] = relationship(back_populates='manager')

    votes: Mapped[list['Vote']] = relationship(back_populates='manager', cascade='all, delete')

    # __table_args__ = (
    #     CheckConstraint("is_admin IN (0, 1)"),
    # )

    def __repr__(self):
        return f'<Manager(telegram_id={self.telegram_id}, is_admin={self.is_admin})>'


class Project(Base):
    __tablename__ = 'project'

    # twitter_handle: Mapped[str] = mapped_column(String(15), primary_key=True, index=True, collation='NOCASE')
    twitter_handle: Mapped[str] = mapped_column(String(15), primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.DATETIME('now'), index=True)
    discord_url: Mapped[str | None]
    discord_admin_nickname: Mapped[str | None]
    tss: Mapped[int | None]
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)

    manager_telegram_id = mapped_column(ForeignKey('manager.telegram_id'))
    manager: Mapped['Manager'] = relationship(back_populates='projects')

    votes: Mapped[list['Vote']] = relationship(back_populates='project', cascade='all, delete')

    def __repr__(self):
        return f'<Project(twitter_handle="{self.twitter_handle}", manager_telegram_id={self.manager_telegram_id})>'

    def get_short_info(self):
        project_info_message_parts = [f'[+{self.likes}/-{self.dislikes}]']
        if self.tss is not None:
            project_info_message_parts.append(f'({self.tss:04d})')
        project_info_message_parts.append(
            f'<a href="https://twitter.com/{self.twitter_handle}">{self.twitter_handle}</a>')
        if self.manager_telegram_id is not None:
            project_info_message_parts.append(f'⇨ {self.manager_telegram_id}')
        project_info_message = ' '.join(project_info_message_parts)
        return project_info_message

    def get_full_info(self):
        project_info_message_parts = [self.get_short_info()]
        if self.discord_url is not None or self.discord_admin_nickname is not None:
            if self.discord_url is not None:
                project_info_message_parts.append(f'Discord: {self.discord_url}')
            if self.discord_admin_nickname is not None:
                project_info_message_parts.append(f' | {self.discord_admin_nickname}')
        project_info_message = '\n'.join(project_info_message_parts)
        return project_info_message


class Vote(Base):
    __tablename__ = 'vote'
    __table_args__ = (
        PrimaryKeyConstraint('manager_telegram_id', 'project_twitter_handle'),
        CheckConstraint('vote_type IN (0, 1)'),
    )

    manager_telegram_id = mapped_column(ForeignKey('manager.telegram_id'))
    manager: Mapped['Manager'] = relationship(back_populates='votes')

    project_twitter_handle = mapped_column(ForeignKey('project.twitter_handle'))
    project: Mapped['Project'] = relationship(back_populates='votes')

    vote_type: Mapped[int]

    def __repr__(self):
        return f'<Vote(project_twitter_handle="{self.project_twitter_handle}", manager_telegram_id={self.manager_telegram_id}), vote_type={self.vote_type}>'


triggers = [
    DDL("""
        CREATE TRIGGER increment_project_likes_after_like_insert
        AFTER INSERT ON vote
        WHEN NEW.vote_type = 1
        BEGIN
            UPDATE project
            SET likes = likes + 1
            WHERE twitter_handle = NEW.project_twitter_handle;
        END;
        """),
    DDL("""
        CREATE TRIGGER increment_project_dislikes_after_dislike_insert
        AFTER INSERT ON vote
        WHEN NEW.vote_type = 0
        BEGIN
            UPDATE project
            SET dislikes = dislikes + 1
            WHERE twitter_handle = NEW.project_twitter_handle;
        END;
        """),
    DDL("""
        CREATE TRIGGER decrement_project_likes_after_like_delete
        AFTER DELETE ON vote
        WHEN OLD.vote_type = 1
        BEGIN
            UPDATE project
            SET likes = likes - 1
            WHERE twitter_handle = OLD.project_twitter_handle;
        END;
        """),
    DDL("""
        CREATE TRIGGER decrement_project_dislikes_after_dislike_delete
        AFTER DELETE ON vote
        WHEN OLD.vote_type = 0
        BEGIN
            UPDATE project
            SET dislikes = dislikes - 1
            WHERE twitter_handle = OLD.project_twitter_handle;
        END;
        """),
]

for trigger in triggers:
    event.listen(Base.metadata, "after_create", trigger)
