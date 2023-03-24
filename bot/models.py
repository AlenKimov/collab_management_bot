from datetime import datetime

from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, WriteOnlyMapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.schema import PrimaryKeyConstraint, CheckConstraint
from sqlalchemy import DDL, event


class Base(DeclarativeBase):
    pass


class Manager(Base):
    __tablename__ = 'manager'

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    telegram_handle: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(default=func.DATETIME('now'))
    is_admin: Mapped[bool] = mapped_column(default=False)

    projects: WriteOnlyMapped[list['Project']] = relationship(back_populates='manager', order_by='Project.tss')

    votes: WriteOnlyMapped[list['Vote']] = relationship(back_populates='manager', cascade='all, delete')

    def __repr__(self):
        return f'<Manager(telegram_id={self.telegram_id}, is_admin={self.is_admin})>'

    def get_short_info(self):
        if self.telegram_handle is not None:
            return f'@{self.telegram_handle}'
        else:
            return str(self.telegram_id)

    def get_full_info(self):
        parts = []
        if self.is_admin:
            role = 'Admin'
        else:
            role = 'Manager'
        parts.append(f'[{role}]')
        parts.append(str(self.telegram_id))
        if self.telegram_handle is not None:
            parts.append(f'(@{self.telegram_handle})')
        return ' '.join(parts)


class Project(Base):
    __tablename__ = 'project'

    twitter_handle: Mapped[str] = mapped_column(String(15, collation='NOCASE'), primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.DATETIME('now'), index=True)
    tss: Mapped[int | None]
    likes: Mapped[int] = mapped_column(default=0)
    dislikes: Mapped[int] = mapped_column(default=0)

    manager_telegram_id = mapped_column(ForeignKey('manager.telegram_id'))
    manager: Mapped['Manager'] = relationship(back_populates='projects')

    votes: WriteOnlyMapped[list['Vote']] = relationship(back_populates='project', cascade='all, delete')

    def __repr__(self):
        return f'<Project(twitter_handle="{self.twitter_handle}", manager_telegram_id={self.manager_telegram_id})>'

    def get_short_info(self):
        parts = []

        delta = datetime.utcnow() - self.created_at
        if self.manager_telegram_id is None and self.likes == 0 and self.dislikes == 0 and delta.seconds < 300:
            parts.append('[NEW!]')
        else:
            parts.append(f'[+{self.likes}/-{self.dislikes}]')

        if self.tss is not None:
            parts.append(f'({self.tss:04d})')

        parts.append(f'<a href="https://twitter.com/{self.twitter_handle}">{self.twitter_handle}</a>')

        if self.manager_telegram_id is not None:
            parts.append(f'⇨ {self.manager.get_short_info()}')

        return ' '.join(parts)

    def get_full_info(self):
        return self.get_short_info()


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
    event.listen(Base.metadata, 'after_create', trigger)
