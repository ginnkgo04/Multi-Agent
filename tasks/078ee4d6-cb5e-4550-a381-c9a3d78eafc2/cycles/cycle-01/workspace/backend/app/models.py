from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# 用户-分类关联表（用于版主管理）
category_moderators = Table(
    'category_moderators',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100))
    bio = Column(Text)
    avatar_url = Column(String(255))
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    threads = relationship("Thread", back_populates="author", cascade="all, delete-orphan")
    posts = relationship("Post", back_populates="author", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="user", cascade="all, delete-orphan")
    moderated_categories = relationship("Category", secondary=category_moderators, back_populates="moderators")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    color = Column(String(7), default="#3b82f6")  # 十六进制颜色代码
    icon = Column(String(50))
    is_active = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    threads = relationship("Thread", back_populates="category", cascade="all, delete-orphan")
    moderators = relationship("User", secondary=category_moderators, back_populates="moderated_categories")


class Thread(Base):
    __tablename__ = "threads"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(200), index=True)
    content = Column(Text, nullable=False)
    is_pinned = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    view_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    last_post_at = Column(DateTime(timezone=True))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    author = relationship("User", back_populates="threads")
    category = relationship("Category", back_populates="threads")
    posts = relationship("Post", back_populates="thread", cascade="all, delete-orphan")
    votes = relationship("Vote", back_populates="thread", cascade="all, delete-orphan")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    is_edited = Column(Boolean, default=False)
    edit_reason = Column(String(200))
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("posts.id"), nullable=True)  # 用于嵌套回复
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    author = relationship("User", back_populates="posts")
    thread = relationship("Thread", back_populates="posts")
    parent = relationship("Post", remote_side=[id], backref="replies")
    votes = relationship("Vote", back_populates="post", cascade="all, delete-orphan")


class Vote(Base):
    __tablename__ = "votes"

    id = Column(Integer, primary_key=True, index=True)
    vote_type = Column(Integer, nullable=False)  # 1: 赞, -1: 踩
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    thread_id = Column(Integer, ForeignKey("threads.id"), nullable=True)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 约束：确保每个投票要么针对主题，要么针对帖子
    __table_args__ = (
        # 确保vote_type只能是1或-1
        # 确保thread_id和post_id至少有一个不为空
    )

    # 关系
    user = relationship("User", back_populates="votes")
    thread = relationship("Thread", back_populates="votes")
    post = relationship("Post", back_populates="votes")