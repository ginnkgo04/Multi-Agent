from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime


# 基础模式
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# 用户相关模式
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseSchema):
    display_name: Optional[str] = Field(None, max_length=100)
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserPublic(UserInDB):
    pass


# 认证相关模式
class Token(BaseSchema):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class TokenData(BaseSchema):
    username: Optional[str] = None


class LoginRequest(BaseSchema):
    username: str
    password: str


# 分类相关模式
class CategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field("#3b82f6", regex="^#[0-9a-fA-F]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = 0

    @validator('slug', pre=True, always=True)
    def generate_slug(cls, v, values):
        if 'name' in values:
            return values['name'].lower().replace(' ', '-')
        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    color: Optional[str] = Field(None, regex="^#[0-9a-fA-F]{6}$")
    icon: Optional[str] = Field(None, max_length=50)
    order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryInDB(CategoryBase):
    id: int
    slug: str
    is_active: bool
    created_at: datetime
    thread_count: Optional[int] = 0

    class Config:
        from_attributes = True


# 主题相关模式
class ThreadBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    category_id: int


class ThreadCreate(ThreadBase):
    pass


class ThreadUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_pinned: Optional[bool] = None
    is_locked: Optional[bool] = None


class ThreadInDB(ThreadBase):
    id: int
    slug: str
    is_pinned: bool
    is_locked: bool
    view_count: int
    reply_count: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    last_post_at: Optional[datetime]

    class Config:
        from_attributes = True


class ThreadWithAuthor(ThreadInDB):
    author: UserPublic
    category: CategoryInDB


# 帖子相关模式
class PostBase(BaseSchema):
    content: str = Field(..., min_length=1)
    thread_id: int
    parent_id: Optional[int] = None


class PostCreate(PostBase):
    pass


class PostUpdate(BaseSchema):
    content: Optional[str] = Field(None, min_length=1)
    edit_reason: Optional[str] = Field(None, max_length=200)


class PostInDB(PostBase):
    id: int
    author_id: int
    is_edited: bool
    edit_reason: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PostWithAuthor(PostInDB):
    author: UserPublic
    replies: List["PostWithAuthor"] = []


# 投票相关模式
class VoteBase(BaseSchema):
    vote_type: int = Field(..., ge=-1, le=1, description="1 for upvote, -1 for downvote")


class VoteCreate(VoteBase):
    thread_id: Optional[int] = None
    post_id: Optional[int] = None

    @validator('thread_id', 'post_id')
    def validate_target(cls, v, values, **kwargs):
        if 'thread_id' in values and 'post_id' in values:
            if values.get('thread_id') and values.get('post_id'):
                raise ValueError("Cannot vote on both thread and post simultaneously")
        return v


class VoteInDB(VoteBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# 分页相关模式
class PaginationParams(BaseSchema):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseSchema):
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


# 更新PostWithAuthor的递归引用
PostWithAuthor.update_forward_refs()