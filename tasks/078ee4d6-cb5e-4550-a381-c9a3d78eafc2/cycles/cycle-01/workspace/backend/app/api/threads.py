from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.database import get_db
from app.models import Thread, Category, User, Post
from app.schemas import ThreadCreate, ThreadInDB, ThreadUpdate, ThreadWithAuthor, PaginationParams, PaginatedResponse
from app.auth import get_current_user, get_current_admin_user, get_category_moderator

router = APIRouter()


@router.post("/", response_model=ThreadWithAuthor, status_code=status.HTTP_201_CREATED)
def create_thread(
    thread_data: ThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建新主题
    """
    # 检查分类是否存在
    category = db.query(Category).filter(
        Category.id == thread_data.category_id,
        Category.is_active == True
    ).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or inactive"
        )
    
    # 生成slug
    import re
    from datetime import datetime
    
    # 从标题生成基础slug
    base_slug = re.sub(r'[^\w\s-]', '', thread_data.title.lower())
    base_slug = re.sub(r'[-\s]+', '-', base_slug).strip('-')
    
    # 添加时间戳以确保唯一性
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    slug = f"{base_slug}-{timestamp}"
    
    # 创建主题
    db_thread = Thread(
        title=thread_data.title,
        slug=slug,
        content=thread_data.content,
        author_id=current_user.id,
        category_id=thread_data.category_id
    )
    
    db.add(db_thread)
    db.commit()
    db.refresh(db_thread)
    
    # 获取完整的主题信息
    thread = db.query(Thread).filter(Thread.id == db_thread.id).first()
    return thread


@router.get("/", response_model=PaginatedResponse)
def read_threads(
    category_id: Optional[int] = None,
    author_id: Optional[int] = None,
    is_pinned: Optional[bool] = None,
    search: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db)
):
    """
    获取主题列表（支持过滤和搜索）
    """
    query = db.query(Thread)
    
    # 应用过滤器
    if category_id is not None:
        query = query.filter(Thread.category_id == category_id)
    
    if author_id is not None:
        query = query.filter(Thread.author_id == author_id)
    
    if is_pinned is not None:
        query = query.filter(Thread.is_pinned == is_pinned)
    
    if search:
        query = query.filter(
            Thread.title.ilike(f"%{search}%") | 
            Thread.content.ilike(f"%{search}%")
        )
    
    # 排序：置顶主题优先，然后按最后回复时间排序
    query = query.order_by(
        desc(Thread.is_pinned),
        desc(Thread.last_post_at if Thread.last_post_at is not None else Thread.created_at)
    )
    
    total = query.count()
    
    threads = query.offset((pagination.page - 1) * pagination.page_size)\
                   .limit(pagination.page_size)\
                   .all()
    
    return {
        "items": threads,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": (total + pagination.page_size - 1) // pagination.page_size
    }


@router.get("/{thread_id}", response_model=ThreadWithAuthor)
def read_thread(
    thread_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定主题信息
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # 增加查看次数
    thread.view_count += 1
    db.commit()
    db.refresh(thread)
    
    return thread


@router.get("/slug/{slug}", response_model=ThreadWithAuthor)
def read_thread_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    通过slug获取主题信息
    """
    thread = db.query(Thread).filter(Thread.slug == slug).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # 增加查看次数
    thread.view_count += 1
    db.commit()
    db.refresh(thread)
    
    return thread


@router.put("/{thread_id}", response_model=ThreadWithAuthor)
def update_thread(
    thread_id: int,
    thread_data: ThreadUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新主题信息
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # 检查权限：作者、版主或管理员可以编辑
    is_author = thread.author_id == current_user.id
    is_moderator = any(category.id == thread.category_id for category in current_user.moderated_categories)
    
    if not (is_author or current_user.is_admin or is_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this thread"
        )
    
    update_data = thread_data.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(thread, field, value)
    
    db.commit()
    db.refresh(thread)
    
    return thread


@router.delete("/{thread_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    删除主题
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    # 检查权限：作者、版主或管理员可以删除
    is_author = thread.author_id == current_user.id
    is_moderator = any(category.id == thread.category_id for category in current_user.moderated_categories)
    
    if not (is_author or current_user.is_admin or is_moderator):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this thread"
        )
    
    db.delete(thread)
    db.commit()


@router.post("/{thread_id}/pin", response_model=ThreadWithAuthor)
def pin_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_category_moderator)
):
    """
    置顶主题（仅版主或管理员）
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    thread.is_pinned = True
    db.commit()
    db.refresh(thread)
    
    return thread


@router.post("/{thread_id}/unpin", response_model=ThreadWithAuthor)
def unpin_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_category_moderator)
):
    """
    取消置顶主题（仅版主或管理员）
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    thread.is_pinned = False
    db.commit()
    db.refresh(thread)
    
    return thread


@router.post("/{thread_id}/lock", response_model=ThreadWithAuthor)
def lock_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_category_moderator)
):
    """
    锁定主题（仅版主或管理员）
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    thread.is_locked = True
    db.commit()
    db.refresh(thread)
    
    return thread


@router.post("/{thread_id}/unlock", response_model=ThreadWithAuthor)
def unlock_thread(
    thread_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_category_moderator)
):
    """
    解锁主题（仅版主或管理员）
    """
    thread = db.query(Thread).filter(Thread.id == thread_id).first()
    if not thread:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thread not found"
        )
    
    thread.is_locked = False
    db.commit()
    db.refresh(thread)
    
    return thread