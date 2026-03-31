from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator


# Base schemas
class BaseSchema(BaseModel):
    class Config:
        from_attributes = True


# User schemas
class UserBase(BaseSchema):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseSchema):
    username: str
    password: str


class UserUpdate(BaseSchema):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None


class UserInDB(UserBase):
    id: int
    is_active: bool
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserPublic(UserBase):
    id: int
    created_at: datetime


class Token(BaseSchema):
    access_token: str
    token_type: str
    user: UserPublic


class TokenData(BaseSchema):
    username: Optional[str] = None


# Category schemas
class CategoryBase(BaseSchema):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseSchema):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)


class Category(CategoryBase):
    id: int
    created_at: datetime
    thread_count: Optional[int] = 0


# Thread schemas
class ThreadBase(BaseSchema):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)


class ThreadCreate(ThreadBase):
    category_id: int


class ThreadUpdate(BaseSchema):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)


class Thread(ThreadBase):
    id: int
    category_id: int
    author_id: int
    created_at: datetime
    updated_at: datetime
    post_count: Optional[int] = 0
    last_post_at: Optional[datetime] = None
    
    author: Optional[UserPublic] = None
    category: Optional[Category] = None


class ThreadWithPosts(Thread):
    posts: List['Post'] = []


# Post schemas
class PostBase(BaseSchema):
    content: str = Field(..., min_length=1)


class PostCreate(PostBase):
    thread_id: int
    parent_id: Optional[int] = None


class PostUpdate(BaseSchema):
    content: Optional[str] = Field(None, min_length=1)


class Post(PostBase):
    id: int
    thread_id: int
    author_id: int
    parent_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    vote_score: Optional[int] = 0
    user_vote: Optional[int] = 0
    
    author: Optional[UserPublic] = None
    replies: List['Post'] = []


# Vote schemas
class VoteBase(BaseSchema):
    value: int = Field(..., ge=-1, le=1)


class VoteCreate(VoteBase):
    post_id: int


class Vote(VoteBase):
    id: int
    post_id: int
    user_id: int
    created_at: datetime


# Notification schemas
class NotificationBase(BaseSchema):
    type: str
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None


class NotificationCreate(NotificationBase):
    user_id: int


class Notification(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    created_at: datetime


class NotificationUpdate(BaseSchema):
    is_read: bool


# Pagination schemas
class PaginationParams(BaseSchema):
    page: int = Field(1, ge=1)
    per_page: int = Field(20, ge=1, le=100)


class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    per_page: int
    total_pages: int


# WebSocket schemas
class WebSocketMessage(BaseSchema):
    type: str
    data: Dict[str, Any]


class NotificationMessage(WebSocketMessage):
    type: str = "notification"
    data: Notification


class VoteMessage(WebSocketMessage):
    type: str = "vote_update"
    data: Dict[str, Any]


class PostMessage(WebSocketMessage):
    type: str = "new_post"
    data: Post


# Update forward references
ThreadWithPosts.update_forward_refs()
Post.update_forward_refs()

# Paginated response types
class PaginatedThreads(PaginatedResponse):
    items: List[Thread]


class PaginatedPosts(PaginatedResponse):
    items: List[Post]


class PaginatedNotifications(PaginatedResponse):
    items: List[Notification]


# Search schemas
class SearchParams(BaseSchema):
    query: str
    category_id: Optional[int] = None
    author_id: Optional[int] = None


# Response schemas for API endpoints
class MessageResponse(BaseSchema):
    message: str


class ErrorResponse(BaseSchema):
    detail: str


class ValidationErrorResponse(BaseSchema):
    detail: List[Dict[str, Any]]