from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database import get_db
from app.auth import get_current_user
from app.models import User, Post, Vote
from app.schemas import VoteCreate, VoteResponse

router = APIRouter(prefix="/api/votes", tags=["votes"])


@router.post("/posts/{post_id}", response_model=VoteResponse)
async def vote_post(
    post_id: int,
    vote_data: VoteCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> VoteResponse:
    """
    Vote on a post.
    
    Vote value can be:
    - 1: Upvote
    - -1: Downvote
    - 0: Remove vote
    
    Returns the updated vote status for the post.
    """
    # Check if post exists
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Check if user is trying to vote on their own post
    if post.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot vote on your own post"
        )
    
    # Check for existing vote
    existing_vote = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.user_id == current_user.id
    ).first()
    
    # Handle vote value
    if vote_data.value == 0:
        # Remove vote
        if existing_vote:
            db.delete(existing_vote)
            db.commit()
            
            # Update post vote count
            post.vote_count = post.vote_count - existing_vote.value
            db.commit()
            
            return VoteResponse(
                post_id=post_id,
                user_id=current_user.id,
                value=0,
                vote_count=post.vote_count
            )
        else:
            # No vote to remove
            return VoteResponse(
                post_id=post_id,
                user_id=current_user.id,
                value=0,
                vote_count=post.vote_count
            )
    
    # Validate vote value
    if vote_data.value not in [1, -1]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vote value must be 1 (upvote), -1 (downvote), or 0 (remove)"
        )
    
    if existing_vote:
        # Update existing vote
        old_value = existing_vote.value
        existing_vote.value = vote_data.value
        db.commit()
        
        # Update post vote count
        post.vote_count = post.vote_count - old_value + vote_data.value
        db.commit()
        
        return VoteResponse(
            post_id=post_id,
            user_id=current_user.id,
            value=vote_data.value,
            vote_count=post.vote_count
        )
    else:
        # Create new vote
        new_vote = Vote(
            post_id=post_id,
            user_id=current_user.id,
            value=vote_data.value
        )
        db.add(new_vote)
        db.commit()
        db.refresh(new_vote)
        
        # Update post vote count
        post.vote_count = post.vote_count + vote_data.value
        db.commit()
        
        return VoteResponse(
            post_id=post_id,
            user_id=current_user.id,
            value=vote_data.value,
            vote_count=post.vote_count
        )


@router.get("/posts/{post_id}/my-vote", response_model=Dict[str, Any])
async def get_my_vote(
    post_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get the current user's vote on a specific post.
    """
    vote = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.user_id == current_user.id
    ).first()
    
    return {
        "post_id": post_id,
        "value": vote.value if vote else 0
    }


@router.get("/posts/{post_id}/stats", response_model=Dict[str, Any])
async def get_post_vote_stats(
    post_id: int,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get vote statistics for a post.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    # Count upvotes and downvotes
    upvotes = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.value == 1
    ).count()
    
    downvotes = db.query(Vote).filter(
        Vote.post_id == post_id,
        Vote.value == -1
    ).count()
    
    return {
        "post_id": post_id,
        "vote_count": post.vote_count,
        "upvotes": upvotes,
        "downvotes": downvotes,
        "total_votes": upvotes + downvotes
    }


@router.get("/users/{user_id}/votes", response_model=Dict[str, Any])
async def get_user_votes(
    user_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get all votes by a specific user.
    """
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Get votes
    votes = db.query(Vote).filter(
        Vote.user_id == user_id
    ).order_by(Vote.created_at.desc()).offset(skip).limit(limit).all()
    
    # Count total
    total = db.query(Vote).filter(Vote.user_id == user_id).count()
    
    return {
        "user_id": user_id,
        "username": user.username,
        "votes": [
            {
                "id": vote.id,
                "post_id": vote.post_id,
                "value": vote.value,
                "created_at": vote.created_at
            }
            for vote in votes
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }