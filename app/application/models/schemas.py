from pydantic import BaseModel, model_serializer


class UserTweetsOut(BaseModel):
    id: int
    name: str


class LikesTweetsOut(BaseModel):
    user_id: int
    name: str


class AttachmentTweetsOut(BaseModel):
    link: str


class TweetsOut(BaseModel):
    id: int
    content: str
    attachments: list[str]
    author: UserTweetsOut
    likes: list[LikesTweetsOut]


class TweetCreateIN(BaseModel):
    tweet_data: str
    tweet_media_ids: list[int]


class Answer(BaseModel):
    result: bool


class TweetCreateOUT(Answer):
    id: int


class AttachmentLoadOUT(Answer):
    media_id: int


class GetTweets(Answer):
    tweets: list[TweetsOut]
