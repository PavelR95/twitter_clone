import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.application.models.core import SQLManager
from app.application.models.models import (
    Attachments,
    Follower,
    Followers,
    Likes,
    Tweets,
    Users,
)

from .factories import FactoryTweets, FactoryUser


@pytest.mark.asyncio
async def test_user(sql_manager: SQLManager):
    """Проверяет добавление пользователя в базу данных

    Args:
        sql_manager (SQLManager): менеджер SQL запросов
    """
    user_factory = FactoryUser()
    user = Users(**user_factory.get_dict())
    await sql_manager.add(user)
    assert user.id is not None
    assert user.name == user_factory.name
    assert user.api_key == user_factory.api_key


@pytest.mark.asyncio
async def test_tweet(sql_manager: SQLManager):
    """Проверяет добавление твита в базу данных

    Args:
        sql_manager (SQLManager): менеджер SQL запросов
    """
    user_factory = FactoryUser()
    user = Users(**user_factory.get_dict())
    tweets_factory = FactoryTweets()
    tweet = Tweets(**tweets_factory.get_dict())
    tweet.author = user
    await sql_manager.add(user)
    await sql_manager.add(tweet)
    assert tweet.id is not None
    assert tweet.content == tweets_factory.content
    assert tweet.user_id == user.id


@pytest.mark.asyncio
async def test_likes(sql_manager: SQLManager):
    """Проверяет добавление лайка в базу данных

    Args:
        sql_manager (SQLManager): менеджер SQL запросов
    """
    # Add users and tweet in database
    user_1 = Users(**FactoryUser().get_dict())
    user_2 = Users(**FactoryUser().get_dict())
    await sql_manager.add(user_1, user_2)
    tweet = Tweets(**FactoryTweets().get_dict())
    tweet.author = user_1
    await sql_manager.add(tweet)
    # Add likes
    like_1 = Likes(user_id=user_1.id, tweet_id=tweet.id, name=user_1.name)
    like_2 = Likes(user_id=user_2.id, tweet_id=tweet.id, name=user_2.name)
    await sql_manager.add(like_1, like_2)
    assert like_1.user_id == user_1.id and like_1.tweet_id == tweet.id
    assert like_1.name == user_1.name
    assert like_2.user_id == user_2.id and like_2.tweet_id == tweet.id
    assert like_2.name == user_2.name
    # Check likes tweet
    stmt = (
        select(Tweets).where(Tweets.id == tweet.id).options(
            selectinload(Tweets.likes))
    )
    res_tweet: Tweets = await sql_manager.select_scalars_one_or_none(stmt)
    assert len(res_tweet.likes) == 2
    tweet_like_1 = res_tweet.likes[0]
    tweet_like_2 = res_tweet.likes[1]
    assert tweet_like_1.user_id == user_1.id
    assert tweet_like_2.user_id == user_2.id


@pytest.mark.asyncio
async def test_followers(sql_manager: SQLManager):
    """Проверяет добавление подписки в базу данных

    Args:
        sql_manager (SQLManager): менеджер SQL запросов
    """
    user_1 = Users(**FactoryUser().get_dict())
    user_2 = Users(**FactoryUser().get_dict())
    user_3 = Users(**FactoryUser().get_dict())
    # Add users list in database
    await sql_manager.add(user_1, user_2, user_3)
    # Add and check follower list in database
    follower_1 = Follower(user_id=user_1.id, name=user_1.name)
    follower_2 = Follower(user_id=user_2.id, name=user_2.name)
    follower_3 = Follower(user_id=user_3.id, name=user_3.name)
    await sql_manager.add(follower_1, follower_2, follower_3)
    assert follower_1.user_id == user_1.id
    assert follower_2.user_id == user_2.id
    assert follower_3.user_id == user_3.id
    # Add followers list in database
    followers_1 = Followers(user_id=user_1.id, follower_id=follower_2.user_id)
    followers_2 = Followers(user_id=user_1.id, follower_id=follower_3.user_id)
    await sql_manager.add(followers_1, followers_2)
    assert followers_1.user_id == user_1.id and followers_2.user_id == user_1.id
    assert (
        followers_1.follower_id == follower_2.user_id
        and followers_2.follower_id == follower_3.user_id
    )
    # Load and check followers user_1
    stmt = (
        select(Users)
        .where(Users.id == user_1.id)
        .options(selectinload(Users.user_followers))
    )
    user: Users = await sql_manager.select_scalars_one_or_none(stmt)
    assert len(user.user_followers) == 2
    user_followers_1 = user.user_followers[0]
    user_followers_2 = user.user_followers[1]
    assert (
        user_followers_1.follower_id == user_2.id
        and user_followers_2.follower_id == user_3.id
    )
    # Check follow user_2
    stmt = (
        select(Follower)
        .where(Follower.user_id == user_2.id)
        .options(selectinload(Follower.followers))
    )
    follower: Follower = await sql_manager.select_scalars_one_or_none(stmt)
    assert len(follower.followers) == 1
    followers = follower.followers[0]
    assert followers.follower_id == follower.user_id
    assert followers.user_id == user_1.id
    # Check follow user_3
    stmt = (
        select(Follower)
        .where(Follower.user_id == user_3.id)
        .options(selectinload(Follower.followers))
    )
    follower: Follower = await sql_manager.select_scalars_one_or_none(stmt)
    assert len(follower.followers) == 1
    followers = follower.followers[0]
    assert followers.follower_id == follower.user_id
    assert followers.user_id == user_1.id


@pytest.mark.asyncio
async def test_attach(sql_manager: SQLManager):
    """Проверяет добавление вложения в базу данных

    Args:
        sql_manager (SQLManager): менеджер SQL запросов
    """
    user_1 = Users(**FactoryUser().get_dict())
    await sql_manager.add(user_1)
    tweet_1 = Tweets(**FactoryTweets().get_dict())
    tweet_1.author = user_1
    await sql_manager.add(tweet_1)
    attach_1 = Attachments()
    attach_1.tweet_id = tweet_1.id
    await sql_manager.add(attach_1)
    assert attach_1.id != None
