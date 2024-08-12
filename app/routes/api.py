import os
from typing import Annotated, Dict

from fastapi import APIRouter, Depends, UploadFile
from fastapi.security import APIKeyHeader
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from ..application import DIRECTORY_MEDIA, SQL_MANAGER
from ..application.custom_exp import CustomException
from ..application.models import schemas
from ..application.models.models import (
    Attachments,
    Follower,
    Followers,
    Likes,
    Tweets,
    Users,
)

api_routes = APIRouter()
header_scheme = APIKeyHeader(name="api-key")


async def get_user(api_key: Annotated[str, Depends(header_scheme)]):
    """Функция возвращает пользователя по api-key
    Если пользователя нет, возвращается ошибка 404

    Args:
        api_key (Annotated[str, Depends): уникальный ключ пользователя

    Raises:
        CustomException: Ошибка 404

    Returns:
        _type_: объект модели баз данных Users
    """
    stmt = (
        select(Users)
        .where(Users.api_key == api_key)
        .options(selectinload(Users.tweets))
        .options(selectinload(Users.user_followers))
        .options(selectinload(Users.following))
    )
    user = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if user is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found user by api-key",
        )
    return user


GetUserDep = Annotated[Users, Depends(get_user)]


@api_routes.post("/api/tweets", response_model=schemas.TweetCreateOUT)
async def add_tweet(user: GetUserDep, tweet_in: schemas.TweetCreateIN) -> Dict:
    """Добавляет новый твит в базу данных
    Получает объект Users и схему данных schemas.TweetCreateIN

    Args:
        user (GetUserDep): объект Users
        tweet_in (schemas.TweetCreateIN): Схема данных schemas.TweetCreateIN

    Returns:
        Dict: Возвращает ID нового твита и результат
    """
    new_tweet = Tweets()
    new_tweet.user_id = user.id
    new_tweet.content = tweet_in.tweet_data
    await SQL_MANAGER.add(new_tweet)
    await SQL_MANAGER.attachments_update_tweet_id(
        tweet_in.tweet_media_ids, new_tweet.id
    )
    return {"id": new_tweet.id, "result": True}


@api_routes.post("/api/medias", response_model=schemas.AttachmentLoadOUT)
async def load_media(user: GetUserDep, file: UploadFile) -> Dict:
    """Загружает изображение и создаёт новое вложение Attachments

    Args:
        user (GetUserDep): объект Users
        file (UploadFile): загружаемый файл картинки

    Returns:
        Dict: возвращает id нового вложения и результат
    """
    new_attach = Attachments()
    await SQL_MANAGER.add_attachment(new_attach, file_name=file.filename)
    file_path = "{path}/{id}_{filename}".format(
        path="{}/images".format(DIRECTORY_MEDIA),
        id=new_attach.id,
        filename=file.filename,
    )
    with open(file=file_path, mode="wb") as image:
        image.write(file.file.read())
    return {"result": True, "media_id": new_attach.id}


@api_routes.delete("/api/tweets/{id}", response_model=schemas.Answer)
async def delete_tweet(user: GetUserDep, id: int):
    """Удаляет из базы данных твит по id
    Проверяет принадлежит ли тви пользователю

    Args:
        user (GetUserDep): объект Users
        id (int): id объекта Tweets

    Raises:
        CustomException: Ошибка 404 если твит не найден
        CustomException: Ошибка 400 если твит не принадлежит пользователю

    Returns:
        _type_: возвращает результат
    """
    stmt = (
        select(Tweets).where(Tweets.id == id).options(selectinload(Tweets.attachments))
    )
    get_tweet: Tweets | None = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_tweet is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found tweet by id",
        )
    if get_tweet.user_id != user.id:
        raise CustomException(
            status_code=400,
            error_type="Bad Request",
            error_message="Tweet author is not user",
        )
    tweet_attachments = get_tweet.attachments
    for attach in tweet_attachments:
        os.remove(
            "{path}/images/{filename}".format(
                path=DIRECTORY_MEDIA, filename=attach.file_name
            )
        )
    await SQL_MANAGER.delete(get_tweet)
    return {"result": True}


@api_routes.post("/api/tweets/{id}/likes", response_model=schemas.Answer)
async def add_like(user: GetUserDep, id: int) -> Dict:
    """Добавляет лайк к твиту. Принимает id твита
    Создаёт новый объект Likes в базе данных.

    Args:
        user (GetUserDep): объект Users
        id (int): id твита

    Raises:
        CustomException: Ошибка 404 если твит не найден

    Returns:
        Dict: возвращает результат
    """
    stmt = select(Tweets).where(Tweets.id == id)
    get_tweet = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_tweet is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found tweet by id",
        )
    new_like = Likes()
    new_like.user_id = user.id
    new_like.name = user.name
    new_like.tweet_id = get_tweet.id
    await SQL_MANAGER.add(new_like)
    return {"result": True}


@api_routes.delete("/api/tweets/{id}/likes", response_model=schemas.Answer)
async def delete_like(user: GetUserDep, id: int) -> Dict:
    """Удаляет лайк к твиту. Принимает id твита
    Удаляет объект Likes в базе данных.

    Args:
        user (GetUserDep): объект Users
        id (int): id твита

    Raises:
        CustomException: Ошибка 404 если твит не найден

    Returns:
        Dict: возвращает результат
    """
    stmt = select(Tweets).where(Tweets.id == id)
    get_tweet = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_tweet is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found tweet by id",
        )
    stmt = (
        select(Likes)
        .where(Likes.user_id == user.id)
        .where(Likes.tweet_id == get_tweet.id)
    )
    get_like = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_like is not None:
        await SQL_MANAGER.delete(get_like)
    return {"result": True}


@api_routes.post("/api/users/{id}/follow", response_model=schemas.Answer)
async def add_follow(user: GetUserDep, id: int) -> Dict:
    """Добавляет подписчика. Принимает id пользователя на которого подписываются
    Добавляет объект Followers в базе данных.

    Args:
        user (GetUserDep): объект Users
        id (int):id пользователя на которого подписываются

    Raises:
        CustomException: 404 если пользователь не найден
        CustomException: 400 если подписка уже есть

    Returns:
        Dict: результат
    """
    stmt = select(Users).where(Users.id == id)
    get_follow_user = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_follow_user is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found user by id",
        )
    stmt = select(Follower).where(Follower.user_id == user.id)
    follower: Follower | None = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if follower is None:
        follower = Follower()
        follower.user_id = user.id
        follower.name = user.name
        await SQL_MANAGER.add(follower)
    stmt = (
        select(Followers)
        .where(Followers.user_id == get_follow_user.id)
        .where(Followers.follower_id == follower.user_id)
    )
    followers = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if followers is not None:
        raise CustomException(
            status_code=400,
            error_type="Bad Request",
            error_message="The user has already followed",
        )
    new_followers = Followers()
    new_followers.user_id = get_follow_user.id
    new_followers.follower_id = follower.user_id
    await SQL_MANAGER.add(new_followers)
    return {"result": True}


@api_routes.delete("/api/users/{id}/follow", response_model=schemas.Answer)
async def delete_follow(user: GetUserDep, id: int) -> Dict:
    """Удаляет подписчика. Принимает id пользователя на которого подписываются
    Удаляет объект Followers в базе данных.

    Args:
        user (GetUserDep): объект Users
        id (int):id пользователя на которого подписываются

    Raises:
        CustomException: 404 если пользователь не найден
        CustomException: 400 если подписки уже нет

    Returns:
        Dict: результат
    """
    stmt = select(Users).where(Users.id == id)
    get_follow_user = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if get_follow_user is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found user by id",
        )
    stmt = (
        select(Followers)
        .where(Followers.user_id == get_follow_user.id)
        .where(Followers.follower_id == user.id)
    )
    get_followers = await SQL_MANAGER.select_scalars_one_or_none(stmt)
    if get_followers is None:
        raise CustomException(
            status_code=400,
            error_type="Bad Request",
            error_message="The user is no following",
        )
    await SQL_MANAGER.delete(get_followers)
    return {"result": True}


@api_routes.get("/api/tweets", response_model=schemas.GetTweets)
async def get_tweets(user: GetUserDep) -> Dict:
    """Возвращает все твиты из базы данных

    Args:
        user (GetUserDep): объект Users

    Returns:
        Dict: Результат и список твитов в виде словаря
    """
    stmt = (
        select(Tweets)
        .options(selectinload(Tweets.author))
        .options(selectinload(Tweets.likes))
        .options(selectinload(Tweets.attachments))
    )
    get_tweets: list[Tweets] = await SQL_MANAGER.select_scalars_all(stmt=stmt)
    tweets = [
        schemas.TweetsOut(
            id=tweet.id,
            content=tweet.content,
            author=schemas.UserTweetsOut(id=tweet.author.id, name=tweet.author.name),
            attachments=[att.link for att in tweet.attachments],
            likes=[
                schemas.LikesTweetsOut(user_id=like.user_id, name=like.name)
                for like in tweet.likes
            ],
        )
        for tweet in get_tweets
    ]
    return {"result": True, "tweets": tweets}


@api_routes.get("/api/users/me")
async def get_me(user: GetUserDep) -> Dict:
    """Возвращает информацию о пользователе

    Args:
        user (GetUserDep): объект Users

    Returns:
        Dict: возвращает словарь с результатом и информацией о пользователе
    """
    answer = {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [],
            "following": [],
        },
    }
    # Get Followers
    follower_ids = [f.follower_id for f in user.user_followers]
    stmt = select(Users).filter(Users.id.in_(follower_ids))
    followers_users: list[Users] = await SQL_MANAGER.select_scalars_all(stmt=stmt)
    answer["user"]["followers"] = [
        {"id": user.id, "name": user.name} for user in followers_users
    ]
    # GET Following
    if user.following is not None:
        stmt = (
            select(Follower)
            .where(Follower.user_id == user.following.user_id)
            .options(selectinload(Follower.followers))
        )
        following: Follower = await SQL_MANAGER.select_scalars_one_or_none(stmt)
        stmt = select(Users).filter(
            Users.id.in_([f.user_id for f in following.followers])
        )
        following_users: list[Users] = await SQL_MANAGER.select_scalars_all(stmt=stmt)
        answer["user"]["following"] = [
            {"id": user.id, "name": user.name} for user in following_users
        ]
    return answer


@api_routes.get("/api/users/{id}")
async def get_user(id: int) -> Dict:
    """Возвращает информацию о пользователе по id

    Args:
        id (int): id пользователя

    Raises:
        CustomException: возвращает 404 если пользователь не найден

    Returns:
        Dict: _description_
    """
    stmt = (
        select(Users)
        .where(Users.id == id)
        .options(selectinload(Users.user_followers))
        .options(selectinload(Users.following))
    )
    user: Users | None = await SQL_MANAGER.select_scalars_one_or_none(stmt=stmt)
    if user is None:
        raise CustomException(
            status_code=404,
            error_type="Not Found",
            error_message="Not found user by id",
        )
    answer = {
        "result": True,
        "user": {
            "id": user.id,
            "name": user.name,
            "followers": [],
            "following": [],
        },
    }
    # Get Followers
    follower_ids = [f.follower_id for f in user.user_followers]
    stmt = select(Users).filter(Users.id.in_(follower_ids))
    followers_users: list[Users] = await SQL_MANAGER.select_scalars_all(stmt=stmt)
    answer["user"]["followers"] = [
        {"id": user.id, "name": user.name} for user in followers_users
    ]
    # GET Following
    if user.following is not None:
        stmt = (
            select(Follower)
            .where(Follower.user_id == user.following.user_id)
            .options(selectinload(Follower.followers))
        )
        following: Follower = await SQL_MANAGER.select_scalars_one_or_none(stmt)
        stmt = select(Users).filter(
            Users.id.in_([f.user_id for f in following.followers])
        )
        following_users: list[Users] = await SQL_MANAGER.select_scalars_all(stmt=stmt)
        answer["user"]["following"] = [
            {"id": user.id, "name": user.name} for user in following_users
        ]
    return answer
