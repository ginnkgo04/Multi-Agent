from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session

from app import schemas, services
from app.database import get_db

router = APIRouter()

@router.get("/snacks", response_model=List[schemas.Snack])
def get_snacks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve a list of all Wuhan specialty snacks.
    """
    snacks = services.get_snacks(db, skip=skip, limit=limit)
    return snacks

@router.get("/snacks/{snack_id}", response_model=schemas.Snack)
def get_snack(snack_id: int, db: Session = Depends(get_db)):
    """
    Retrieve details of a specific snack by ID.
    """
    snack = services.get_snack(db, snack_id=snack_id)
    if snack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snack not found")
    return snack

@router.post("/snacks", response_model=schemas.Snack, status_code=status.HTTP_201_CREATED)
def create_snack(snack: schemas.SnackCreate, db: Session = Depends(get_db)):
    """
    Add a new snack to the collection.
    """
    return services.create_snack(db=db, snack=snack)

@router.put("/snacks/{snack_id}", response_model=schemas.Snack)
def update_snack(snack_id: int, snack_update: schemas.SnackUpdate, db: Session = Depends(get_db)):
    """
    Update an existing snack by ID.
    """
    snack = services.update_snack(db, snack_id=snack_id, snack_update=snack_update)
    if snack is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snack not found")
    return snack

@router.delete("/snacks/{snack_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snack(snack_id: int, db: Session = Depends(get_db)):
    """
    Delete a snack by ID.
    """
    success = services.delete_snack(db, snack_id=snack_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Snack not found")
    return None