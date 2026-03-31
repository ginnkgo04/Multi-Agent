from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import List, Optional

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Thread, Post, Category, Vote
from app.schemas import (
    ThreadCreate,
    ThreadResponse,
    ThreadListResponse,
    ThreadDetailResponse,
    PostCreate,
    PostResponse,
    PaginationParams
)
from app.websocket.manager import manager as ws_manager

router = APIRouter(prefix="/api/threads", tags=["threads"])


@router.post("/", response_model=ThreadResponse, status_code=status.HTTP_201_CREATED)
def create_thread(
    thread_data: ThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new thread in a category.
    """
    # Check if category exists
    category = db.query(Category).filter(Category.id == thread_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Create thread
    thread = Thread(
        title=thread_data.title,
        content=thread_data.content,
        category_id=thread_data.category_id,
        author_id=current_user.id
    )
    
    db.add(thread)
    db.commit()
    db.refresh(thread)
    
    # Create initial post from thread content
    post = Post(
        content=thread_data.content,
        thread_id=thread.id,
        author_id=current_user.id
    )
    
    db.add(post)
    db.commit()
    
    # Load thread with author and category
    thread = db.query(Thread).options(
        joinedload(Thread.author),
        joinedload(Thread.category)
    ).filter(Thread.id == thread.id).first()
    
    return thread


@router.get("/{thread_id}", response_model=ThreadDetailResponse)
def get_thread(
    thread_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get thread details with paginated posts.
    """
    # Get thread with author and category
    thread = db.query(Thread).options(
        joinedload(Thread.author),
        joinedload(Thread.category)
    ).filter(Thread.id == thread_id).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Calculate offset for pagination
    offset = (page - 1) * limit
    
    # Get posts for this thread with authors and vote counts
    posts_query = db.query(Post).options(
        joinedload(Post.author)
    ).filter(
        Post.thread_id == thread_id,
        Post.parent_id == None  # Only top-level posts
    ).order_by(Post.created_at.asc())
    
    total_posts = posts_query.count()
    posts = posts_query.offset(offset).limit(limit).all()
    
    # Get vote information for each post if user is authenticated
    post_ids = [post.id for post in posts]
    user_votes = {}
    vote_counts = {}
    
    if current_user:
        # Get user's votes on these posts
        votes = db.query(Vote).filter(
            Vote.post_id.in_(post_ids),
            Vote.user_id == current_user.id
        ).all()
        user_votes = {vote.post_id: vote.value for vote in votes}
    
    # Get vote counts for each post
    vote_counts_query = db.query(
        Vote.post_id,
        func.sum(Vote.value).label("total_votes")
    ).filter(
        Vote.post_id.in_(post_ids)
    ).group_by(Vote.post_id).all()
    
    vote_counts = {row.post_id: row.total_votes or 0 for row in vote_counts_query}
    
    # Format posts with vote information
    formatted_posts = []
    for post in posts:
        post_dict = PostResponse.from_orm(post).dict()
        post_dict["vote_count"] = vote_counts.get(post.id, 0)
        post_dict["user_vote"] = user_votes.get(post.id, 0)
        
        # Get replies for this post
        replies = db.query(Post).options(
            joinedload(Post.author)
        ).filter(
            Post.parent_id == post.id
        ).order_by(Post.created_at.asc()).all()
        
        # Format replies
        formatted_replies = []
        for reply in replies:
            reply_dict = PostResponse.from_orm(reply).dict()
            
            # Get vote information for reply
            reply_vote_count = db.query(func.sum(Vote.value)).filter(
                Vote.post_id == reply.id
            ).scalar() or 0
            
            reply_user_vote = 0
            if current_user:
                user_reply_vote = db.query(Vote).filter(
                    Vote.post_id == reply.id,
                    Vote.user_id == current_user.id
                ).first()
                if user_reply_vote:
                    reply_user_vote = user_reply_vote.value
            
            reply_dict["vote_count"] = reply_vote_count
            reply_dict["user_vote"] = reply_user_vote
            formatted_replies.append(reply_dict)
        
        post_dict["replies"] = formatted_replies
        formatted_posts.append(post_dict)
    
    # Increment thread view count (optional - could be implemented as a separate model)
    # For now, we'll just return the thread data
    
    return {
        "thread": ThreadResponse.from_orm(thread),
        "posts": formatted_posts,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total_posts,
            "pages": (total_posts + limit - 1) // limit
        }
    }


@router.get("/", response_model=List[ThreadListResponse])
def list_threads(
    category_id: Optional[int] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|title)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List threads with filtering, searching, and sorting options.
    """
    # Build query
    query = db.query(Thread).options(
        joinedload(Thread.author),
        joinedload(Thread.category)
    )
    
    # Apply filters
    if category_id:
        query = query.filter(Thread.category_id == category_id)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Thread.title.ilike(search_term)) |
            (Thread.content.ilike(search_term))
        )
    
    # Apply sorting
    sort_column = getattr(Thread, sort_by)
    if sort_order == "desc":
        query = query.order_by(desc(sort_column))
    else:
        query = query.order_by(sort_column)
    
    # Apply pagination
    offset = (page - 1) * limit
    threads = query.offset(offset).limit(limit).all()
    
    # Get post counts for each thread
    thread_ids = [thread.id for thread in threads]
    
    if thread_ids:
        post_counts_query = db.query(
            Post.thread_id,
            func.count(Post.id).label("post_count")
        ).filter(
            Post.thread_id.in_(thread_ids)
        ).group_by(Post.thread_id).all()
        
        post_counts = {row.thread_id: row.post_count for row in post_counts_query}
    else:
        post_counts = {}
    
    # Format response
    response = []
    for thread in threads:
        thread_dict = ThreadListResponse.from_orm(thread).dict()
        thread_dict["post_count"] = post_counts.get(thread.id, 0)
        
        # Get last post info
        last_post = db.query(Post).filter(
            Post.thread_id == thread.id
        ).order_by(desc(Post.created_at)).first()
        
        if last_post:
            thread_dict["last_post_at"] = last_post.created_at
            thread_dict["last_post_author"] = last_post.author.username if last_post.author else None
        else:
            thread_dict["last_post_at"] = thread.created_at
            thread_dict["last_post_author"] = thread.author.username
        
        response.append(thread_dict)
    
    return response


@router.put("/{thread_id}", response_model=ThreadResponse)
def update_thread(
    thread_id: int,
    thread_data: ThreadCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update a thread (only by author or admin).
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # Check permissions
    if thread.author_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this thread"
        )
    
    # Check if category exists
    category = db.query(Category).filter(Category.id == thread_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Update thread
    thread.title = thread_data.title
    thread.content = thread_data