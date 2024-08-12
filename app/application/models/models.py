from typing import List

from sqlalchemy import ARRAY, ForeignKey, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Users(Base):

    __tablename__: str = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    api_key: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)

    tweets: Mapped[List["Tweets"]] = relationship(
        back_populates="author", cascade="all, delete"
    )
    user_likes: Mapped[List["Likes"]] = relationship(
        back_populates="users", cascade="all, delete"
    )
    following: Mapped["Follower"] = relationship(
        back_populates="user", cascade="all, delete"
    )
    user_followers: Mapped[List["Followers"]] = relationship(
        back_populates="user_follower", cascade="all, delete"
    )


class Tweets(Base):

    __tablename__: str = "tweets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey(column="users.id"))

    author: Mapped["Users"] = relationship(back_populates="tweets")
    likes: Mapped[List["Likes"]] = relationship(
        back_populates="tweet", cascade="all, delete"
    )
    attachments: Mapped[List["Attachments"]] = relationship(
        back_populates="tweet_media", cascade="all, delete"
    )


class Attachments(Base):

    __tablename__: str = "attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tweet_id: Mapped[int] = mapped_column(ForeignKey("tweets.id"), nullable=True)
    file_name: Mapped[str] = mapped_column(String(100), nullable=True)
    link: Mapped[str] = mapped_column(String(200), nullable=True)

    tweet_media: Mapped["Tweets"] = relationship(back_populates="attachments")


class Likes(Base):

    __tablename__: str = "likes"

    tweet_id: Mapped[int] = mapped_column(
        ForeignKey(column="tweets.id"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id"), primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100))

    tweet: Mapped["Tweets"] = relationship(back_populates="likes")
    users: Mapped["Users"] = relationship(back_populates="user_likes")


class Follower(Base):

    __tablename__: str = "follower"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    user: Mapped["Users"] = relationship(back_populates="following")
    followers: Mapped[List["Followers"]] = relationship(back_populates="user_followers")


class Followers(Base):

    __tablename__: str = "followers"

    user_id: Mapped[int] = mapped_column(
        ForeignKey(column="users.id"), primary_key=True
    )
    follower_id: Mapped[int] = mapped_column(
        ForeignKey(column="follower.user_id"), primary_key=True
    )

    user_follower: Mapped["Users"] = relationship(back_populates="user_followers")
    user_followers: Mapped["Follower"] = relationship(back_populates="followers")
