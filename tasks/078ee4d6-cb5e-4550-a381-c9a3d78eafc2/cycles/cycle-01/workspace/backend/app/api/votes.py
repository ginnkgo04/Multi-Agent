from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database import get_db
from app.models import Vote, Thread, Post, User
from app.schemas import VoteCreate, VoteInDB
from app.auth import get_current_user

router = APIRouter()


@router.post("/", response_model=VoteInDB)
def create_vote(
    vote_data: VoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建投票
    """
    # 验证投票目标
    if not vote_data.thread_id and not vote_data.post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Must specify either thread_id or post_id"
        )
    
    if vote_data.thread_id and vote_data.post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot vote on both thread and post simultaneously"
        )
    
    # 检查投票目标是否存在
    if vote_data.thread_id:
        thread = db.query(Thread).filter(Thread.id == vote_data.thread_id).first()
        if not thread:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Thread not found"
            )
        
        # 检查是否已投票
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.user_id == current_user.id,
                Vote.thread_id == vote_data.thread_id
            )
        ).first()
        
        target_id = vote_data.thread_id
        target_type = "thread"
        
    else:  # vote_data.post_id
        post = db.query(Post).filter(Post.id == vote_data.post_id).first()
        if not post:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found"
            )
        
        # 检查是否已投票
        existing_vote = db.query(Vote).filter(
            and_(
                Vote.user_id == current_user.id,
                Vote.post_id == vote_data.post_id
            )
        ).first()
        
        target_id = vote_data.post_id
        target_type = "post"
    
    # 如果已投票，更新投票类型
    if existing_vote:
        if existing_vote.vote_type == vote_data.vote_type:
            # 如果投票类型相同，取消投票（删除）
            db.delete(existing_vote)
            db.commit()
            return {"message": f"Vote removed from {target_type}"}
        else:
            # 如果投票类型不同，更新投票
            existing_vote.vote_type = vote_data.vote_type
            db.commit()
            db.refresh(existing_vote)
            return existing_vote
    
    # 创建新投票
    db_vote = Vote(
        vote_type=vote_data.vote_type,
        user_id=current_user.id,
        thread_id=vote_data.thread_id,
        post_id=vote_data.post_id
    )
    
    db.add(db_vote)
    db.commit()
    db.refresh(db_vote)
    
    return db_vote


@router.get("/thread/{thread_id}/user/{user_id}")
def get_thread_vote_by_user(
    thread_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户对主题的投票
    """
    vote = db.query(Vote).filter(
        and_(
            Vote.user_id == user_id,
            Vote.thread_id == thread_id
        )
    ).first()
    
    if not vote:
        return {"vote_type": 0}  # 0表示没有投票
    
    return {"vote_type": vote.vote_type}


@router.get("/post/{post_id}/user/{user_id}")
def get_post_vote_by_user(
    post_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户对帖子的投票
    """
    vote = db.query(Vote).filter(
        and_(
            Vote.user_id == user_id,
            Vote.post_id == post_id
        )
    ).first()
    
    if not vote:
        return {"vote_type": 0}  # 0表示没有投票
    
    return {"vote_type": vote.vote_type}


@router.get("/thread/{thread_id}/stats")
def get_thread_vote_stats(
    thread_id: int,
    db: Session = Depends(get_db)
):
    """
    获取主题的投票统计
    """
    # 检查主题是否存在
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # 计算赞成票和反对票
    upvotes = db.query(Vote).filter(
        and_(
            Vote.thread_id == thread_id,
            Vote.vote_type == 1
        )
    ).count()
    
    downvotes = db.query(Vote).filter(
        and_(
            Vote.thread_id == thread_id,
            Vote.vote_type == -1
        )
    ).count()
    
    total_score = upvotes - downvotes
    
    return {
        "thread_id": thread_id,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "total_score": total_score,
        "total_votes": upvotes + downvotes
    }


@router.get("/post/{post_id}/stats")
def get_post_vote_stats(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    获取帖子的投票统计
    """
    # 检查帖子是否存在
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # 计算赞成票和反对票
    upvotes = db.query(Vote).filter(
        and_(
            Vote.post_id == post_id,
            Vote.vote_type == 1
        )
    ).count()
    
    downvotes = db.query(Vote).filter(
        and_(
            Vote.post_id == post_id,
            Vote.vote_type == -1
        )
    ).count()
    
    total_score = upvotes - downvotes
    
    return {
        "post_id": post_id,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "total_score": total_score,
        "total_votes": upvotes + downvotes
    }


@router.delete("/thread/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread_vote(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户对主题的投票
    """
    vote = db.query(Vote).filter(
        and_(
            Vote.user_id == current_user.id,
            Vote.thread_id == thread_id
        )
    ).first()
    
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )
    
    db.delete(vote)
    db.commit()


@router.delete("/post/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post_vote(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除用户对帖子的投票
    """
    vote = db.query(Vote).filter(
        and_(
            Vote.user_id == current_user.id,
            Vote.post_id == post_id
        )
    ).first()
    
    if not vote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vote not found"
        )
    
    db.delete(vote)
    db.commit()