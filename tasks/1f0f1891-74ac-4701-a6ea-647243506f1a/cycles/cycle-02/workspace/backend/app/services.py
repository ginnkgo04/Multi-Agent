from typing import List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models, schemas


class SnackService:
    """Service layer for snack-related business logic."""

    @staticmethod
    def get_snacks(db: Session, skip: int = 0, limit: int = 100) -> List[models.Snack]:
        """Retrieve a list of snacks with pagination."""
        return db.query(models.Snack).offset(skip).limit(limit).all()

    @staticmethod
    def get_snack_by_id(db: Session, snack_id: int) -> models.Snack:
        """Retrieve a specific snack by its ID."""
        snack = db.query(models.Snack).filter(models.Snack.id == snack_id).first()
        if not snack:
            raise HTTPException(status_code=404, detail="Snack not found")
        return snack

    @staticmethod
    def create_snack(db: Session, snack_data: schemas.SnackCreate) -> models.Snack:
        """Create a new snack in the database."""
        # Convert list of ingredients to a comma-separated string for storage
        ingredients_str = ",".join(snack_data.ingredients) if snack_data.ingredients else ""
        
        db_snack = models.Snack(
            name=snack_data.name,
            description=snack_data.description,
            ingredients=ingredients_str,
            origin=snack_data.origin,
            popularity=snack_data.popularity
        )
        db.add(db_snack)
        db.commit()
        db.refresh(db_snack)
        return db_snack

    @staticmethod
    def update_snack(db: Session, snack_id: int, snack_data: schemas.SnackUpdate) -> models.Snack:
        """Update an existing snack by ID."""
        snack = SnackService.get_snack_by_id(db, snack_id)
        
        update_data = snack_data.dict(exclude_unset=True)
        
        # Handle ingredients list conversion if present
        if "ingredients" in update_data and update_data["ingredients"] is not None:
            update_data["ingredients"] = ",".join(update_data["ingredients"])
        
        for field, value in update_data.items():
            setattr(snack, field, value)
        
        db.commit()
        db.refresh(snack)
        return snack

    @staticmethod
    def delete_snack(db: Session, snack_id: int) -> dict:
        """Delete a snack by ID."""
        snack = SnackService.get_snack_by_id(db, snack_id)
        db.delete(snack)
        db.commit()
        return {"message": "Snack deleted successfully"}

    @staticmethod
    def search_snacks(db: Session, name: Optional[str] = None, origin: Optional[str] = None) -> List[models.Snack]:
        """Search snacks by name or origin."""
        query = db.query(models.Snack)
        
        if name:
            query = query.filter(models.Snack.name.ilike(f"%{name}%"))
        if origin:
            query = query.filter(models.Snack.origin.ilike(f"%{origin}%"))
        
        return query.all()

    @staticmethod
    def get_popular_snacks(db: Session, threshold: int = 80) -> List[models.Snack]:
        """Get snacks with popularity above a certain threshold."""
        return db.query(models.Snack).filter(models.Snack.popularity >= threshold).order_by(models.Snack.popularity.desc()).all()