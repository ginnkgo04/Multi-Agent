from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Post, Thread, Notification
from app.schemas import PostCreate, PostResponse, PostUpdate
from app.websocket.manager import manager

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.post("/", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new post in a thread.
    """
    # Check if thread exists
    thread = db.query(Thread).filter(Thread.id == post_data.thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # If parent_id is provided, check if parent post exists and belongs to same thread
    if post_data.parent_id:
        parent_post = db.query(Post).filter(Post.id == post_data.parent_id).first()
        if not parent_post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent post not found"
            )
        if parent_post.thread_id != post_data.thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent post does not belong to the same thread"
            )
    
    # Create post
    post = Post(
        content=post_data.content,
        thread_id=post_data.thread_id,
        author_id=current_user.id,
        parent_id=post_data.parent_id
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    # Update thread's updated_at timestamp
    thread.updated_at = post.created_at
    db.commit()
    
    # Create notification for thread author if post author is not thread author
    if thread.author_id != current_user.id:
        notification = Notification(
            user_id=thread.author_id,
            type="new_reply",
            title="New Reply",
            message=f"{current_user.username} replied to your thread: {thread.title}",
            data={"thread_id": thread.id, "post_id": post.id}
        )
        db.add(notification)
        db.commit()
        
        # Send real-time notification via WebSocket
        manager.send_notification(thread.author_id, {
            "type": "new_reply",
            "title": "New Reply",
            "message": f"{current_user.username} replied to your thread: {thread.title}",
            "data": {"thread_id": thread.id, "post_id": post.id}
        })
    
    # If this is a reply to another post, notify the parent post author
    if post_data.parent_id and parent_post.author_id != current_user.id:
        notification = Notification(
            user_id=parent_post.author_id,
            type="new_reply",
            title="New Reply",
            message=f"{current_user.username} replied to your post",
            data={"thread_id": thread.id, "post_id": post.id, "parent_post_id": parent_post.id}
        )
        db.add(notification)
        db.commit()
        
        # Send real-time notification via WebSocket
        manager.send_notification(parent_post.author_id, {
            "type": "new_reply",
            "title": "New Reply",
            "message": f"{current_user.username} replied to your post",
            "data": {"thread_id": thread.id, "post_id": post.id, "parent_post_id": parent_post.id}
        })
    
    return post


@router.get("/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific post by ID.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return post


@router.put("/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a post (only by author or admin).
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check authorization
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post"
        )
    
    # Update post content
    post.content = post_data.content
    db.commit()
    db.refresh(post)
    
    # Update thread's updated_at timestamp
    thread = db.query(Thread).filter(Thread.id == post.thread_id).first()
    if thread:
        from datetime import datetime
        thread.updated_at = datetime.utcnow()
        db.commit()
    
    return post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a post (only by author or admin).
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check authorization
    if post.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post"
        )
    
    # Store thread_id for updating timestamp
    thread_id = post.thread_id
    
    # Delete the post
    db.delete(post)
    db.commit()
    
    # Update thread's updated_at timestamp
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if thread:
        from datetime import datetime
        thread.updated_at = datetime.utcnow()
        db.commit()


@router.get("/thread/{thread_id}", response_model=List[PostResponse])
def get_thread_posts(
    thread_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all posts in a thread, optionally filtered by parent_id for nested replies.
    """
    # Check if thread exists
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Get all posts in thread
    posts = db.query(Post).filter(Post.thread_id == thread_id).order_by(Post.created_at).all()
    
    return posts


@router.get("/{post_id}/replies", response_model=List[PostResponse])
def get_post_replies(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all replies to a specific post.
    """
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Get all replies to this post
    replies = db.query(Post).filter(Post.parent_id == post_id).order_by(Post.created_at).all()
    
    return replies