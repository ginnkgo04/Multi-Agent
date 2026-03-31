from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Post, Thread, User
from app.schemas import PostCreate, PostInDB, PostUpdate, PostWithAuthor, PaginationParams, PaginatedResponse
from app.auth import get_current_user, get_current_admin_user, get_category_moderator

router = APIRouter()


@router.post("/", response_model=PostWithAuthor, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新帖子
    """
    # 检查主题是否存在且未锁定
    thread = db.query(Thread).filter(Thread.id == post_data.thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    if thread.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread is locked"
        )
    
    # 如果指定了父帖子，检查是否存在
    if post_data.parent_id:
        parent_post = db.query(Post).filter(Post.id == post_data.parent_id).first()
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found"
            )
        
        # 确保父帖子属于同一个主题
        if parent_post.thread_id != post_data.thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post does not belong to the same thread"
            )
    
    # 创建帖子
    db_post = Post(
        content=post_data.content,
        author_id=current_user.id,
        thread_id=post_data.thread_id,
        parent_id=post_data.parent_id
    )
    
    db.add(db_post)
    
    # 更新主题的回复计数和最后回复时间
    thread.reply_count += 1
    thread.last_post_at = db_post.created_at
    
    db.commit()
    db.refresh(db_post)
    
    # 获取完整的帖子信息
    post = db.query(Post).filter(Post.id == db_post.id).first()
    return post


@router.get("/thread/{thread_id}", response_model=List[PostWithAuthor])
def read_thread_posts(
    thread_id: int,
    parent_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    获取主题下的帖子列表
    """
    # 检查主题是否存在
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    query = db.query(Post).filter(Post.thread_id == thread_id)
    
    # 如果指定了父帖子ID，只获取该父帖子的回复
    if parent_id is not None:
        query = query.filter(Post.parent_id == parent_id)
    else:
        # 否则只获取顶级帖子（没有父帖子）
        query = query.filter(Post.parent_id == None)
    
    # 按创建时间排序
    posts = query.order_by(Post.created_at).all()
    
    return posts


@router.get("/{post_id}", response_model=PostWithAuthor)
def read_post(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定帖子信息
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.put("/{post_id}", response_model=PostWithAuthor)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新帖子信息
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 检查主题是否锁定
    thread = db.query(Thread).filter(Thread.id == post.thread_id).first()
    if thread and thread.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread is locked"
        )
    
    # 检查权限：作者、版主或管理员可以编辑
    is_author = post.author_id == current_user.id
    is_moderator = any(category.id == thread.category_id for category in current_user.moderated_categories)
    
    if not (is_author or current_user.is_admin or is_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    update_data = post_data.dict(exclude_unset=True)
    
    # 标记为已编辑
    update_data["is_edited"] = True
    
    for field, value in update_data.items():
        setattr(post, field, value)
    
    db.commit()
    db.refresh(post)
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除帖子
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 检查主题是否锁定
    thread = db.query(Thread).filter(Thread.id == post.thread_id).first()
    if thread and thread.is_locked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Thread is locked"
        )
    
    # 检查权限：作者、版主或管理员可以删除
    is_author = post.author_id == current_user.id
    is_moderator = any(category.id == thread.category_id for category in current_user.moderated_categories)
    
    if not (is_author or current_user.is_admin or is_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # 如果有回复，需要处理
    if post.replies:
        # 如果是版主或管理员删除，可以删除整个回复链
        if current_user.is_admin or is_moderator:
            # 递归删除所有回复
            def delete_replies(post_id):
                replies = db.query(Post).filter(Post.parent_id == post_id).all()
                for reply in replies:
                    delete_replies(reply.id)
                    db.delete(reply)
            
            delete_replies(post_id)
        else:
            # 普通用户只能删除没有回复的帖子
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete post with replies"
            )
    
    # 更新主题的回复计数
    if thread:
        thread.reply_count -= 1
    
    db.delete(post)
    db.commit()


@router.get("/user/{user_id}", response_model=PaginatedResponse)
def read_user_posts(
    user_id: int,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    获取用户的帖子列表
    """
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    query = db.query(Post).filter(Post.author_id == user_id)
    total = query.count()
    
    posts = query.order_by(desc(Post.created_at))\
                 .offset((pagination.page - 1) * pagination.page_size)\
                 .limit(pagination.page_size)\
                 .all()
    
    return {
        "items": posts,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size
    }