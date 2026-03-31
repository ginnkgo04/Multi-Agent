from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Category, User, Thread
from app.schemas import CategoryCreate, CategoryInDB, CategoryUpdate, PaginationParams, PaginatedResponse
from app.auth import get_current_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=CategoryInDB, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    创建新分类（仅管理员）
    """
    # 检查分类名是否已存在
    db_category = db.query(Category).filter(Category.name == category_data.name).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists"
        )
    
    # 生成slug
    slug = category_data.name.lower().replace(' ', '-')
    
    # 检查slug是否已存在
    db_category = db.query(Category).filter(Category.slug == slug).first()
    if db_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category slug already exists"
        )
    
    # 创建分类
    db_category = Category(
        name=category_data.name,
        slug=slug,
        description=category_data.description,
        color=category_data.color,
        icon=category_data.icon,
        order=category_data.order
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


@router.get("/", response_model=List[CategoryInDB])
def read_categories(
    db: Session = Depends(get_db)
):
    """
    获取所有分类列表
    """
    categories = db.query(Category).filter(Category.is_active == True)\
                    .order_by(Category.order, Category.name)\
                    .all()
    
    # 为每个分类添加主题数量
    for category in categories:
        thread_count = db.query(func.count(Thread.id)).filter(
            Thread.category_id == category.id
        ).scalar()
        category.thread_count = thread_count
    
    return categories


@router.get("/{category_id}", response_model=CategoryInDB)
def read_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    """
    获取指定分类信息
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 添加主题数量
    thread_count = db.query(func.count(Thread.id)).filter(
        Thread.category_id == category.id
    ).scalar()
    category.thread_count = thread_count
    
    return category


@router.get("/slug/{slug}", response_model=CategoryInDB)
def read_category_by_slug(
    slug: str,
    db: Session = Depends(get_db)
):
    """
    通过slug获取分类信息
    """
    category = db.query(Category).filter(Category.slug == slug).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 添加主题数量
    thread_count = db.query(func.count(Thread.id)).filter(
        Thread.category_id == category.id
    ).scalar()
    category.thread_count = thread_count
    
    return category


@router.put("/{category_id}", response_model=CategoryInDB)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新分类信息（仅管理员）
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    update_data = category_data.dict(exclude_unset=True)
    
    # 如果更新名称，需要更新slug
    if "name" in update_data:
        update_data["slug"] = update_data["name"].lower().replace(' ', '-')
        
        # 检查新slug是否已存在
        existing_category = db.query(Category).filter(
            Category.slug == update_data["slug"],
            Category.id != category_id
        ).first()
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category slug already exists"
            )
    
    for field, value in update_data.items():
        setattr(category, field, value)
    
    db.commit()
    db.refresh(category)
    
    # 添加主题数量
    thread_count = db.query(func.count(Thread.id)).filter(
        Thread.category_id == category.id
    ).scalar()
    category.thread_count = thread_count
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    删除分类（仅管理员）
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # 检查分类中是否有主题
    thread_count = db.query(func.count(Thread.id)).filter(
        Thread.category_id == category_id
    ).scalar()
    
    if thread_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete category with threads. Please move or delete threads first."
        )
    
    db.delete(category)
    db.commit()


@router.post("/{category_id}/moderators/{user_id}", status_code=status.HTTP_200_OK)
def add_category_moderator(
    category_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    添加分类版主（仅管理员）
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查是否已经是版主
    if user in category.moderators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a moderator of this category"
        )
    
    category.moderators.append(user)
    db.commit()
    
    return {"message": "Moderator added successfully"}


@router.delete("/{category_id}/moderators/{user_id}", status_code=status.HTTP_200_OK)
def remove_category_moderator(
    category_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    移除分类版主（仅管理员）
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查是否是版主
    if user not in category.moderators:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not a moderator of this category"
        )
    
    category.moderators.remove(user)
    db.commit()
    
    return {"message": "Moderator removed successfully"}