from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session
from ..database import engine, get_db
from typing import List

router = APIRouter(
    prefix='/users',
    tags=['Users']
)


@router.get("/", response_model=List[schemas.User])
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    
    #hash the password
    hashed_password = utils.hash(user.password)
    user.password = hashed_password
    
    
    new_user = models.User(**user.dict())
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.get('/{id}', response_model=schemas.User)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if not user:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"user with id {id} was not found"
            )
    
    return user


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id: int, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    user = db.query(models.User).filter(models.User.id == id).first()
    
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with id {id} does not exist"
        )
        
    db.delete(user)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.User)
def update_user(id: int, updated_user: schemas.UserCreate, db: Session = Depends(get_db), user_id: int = Depends(oauth2.get_current_user)):
    
    hashed_password = utils.hash(updated_user.password)
    updated_user.password = hashed_password
    
    user_query = db.query(models.User).filter(models.User.id == id)
    user = user_query.first()
    
    
    if user == None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"user with is {id} does not exit"
        )
        
    user_query.update(updated_user.dict(), synchronize_session=False)
    db.commit()
    
    return user_query.first()