from datetime import datetime
from typing import Optional, List
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.database import Base


class VoteType(enum.Enum):
    """Vote type enumeration"""
    UPVOTE = 1
    DOWNVOTE = -1


class NotificationType(enum.Enum):
    """Notification type enumeration"""
    NEW_REPLY = "new_reply"
    NEW_POST = "new_post"
    THREAD_SUBSCRIPTION = "thread_subscription"
    MENTION = "mention"
    VOTE = "vote"
    SYSTEM = "system"


class User(Base):
    """User model for authentication and user data"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    threads = relationship("Thread", back_populates="author", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Category(Base):
    """Forum category model"""
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    threads = relationship("Thread", back_populates="category", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Thread(Base):
    """Thread model representing discussion topics"""
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="threads")
    author = relationship("User", back_populates="threads")
    posts = relationship("Post", back_populates="thread", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Thread(id={self.id}, title='{self.title}')>"


class Post(Base):
    """Post model for thread replies and comments"""
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    thread_id = Column(Integer, ForeignKey("threads.id", ondelete="CASCADE"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    thread = relationship("Thread", back_populates="posts")
    author = relationship("User", back_populates="posts")
    parent = relationship("Post", remote_side=[id], back_populates="replies")
    replies = relationship("Post", back_populates="parent", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="post", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Post(id={self.id}, thread_id={self.thread_id})>"


class Vote(Base):
    """Vote model for post upvotes/downvotes"""
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    value = Column(Enum(VoteType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    post = relationship("Post", back_populates="votes")
    user = relationship("User", back_populates="votes")

    # Unique constraint to prevent duplicate votes
    __table_args__ = (('unique_post_user', 'post_id', 'user_id'),)

    def __repr__(self):
        return f"<Vote(id={self.id}, post_id={self.post_id}, value={self.value})>"


class Notification(Base):
    """Notification model for user notifications"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    data = Column(JSON, nullable=True)  # Additional data like thread_id, post_id, etc.
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type}')>"