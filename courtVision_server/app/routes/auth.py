"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserCreate, UserLogin
from app.utils.utils import hash_password, verify_password, create_jwt_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    hashed_pw = hash_password(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    return {"message": "User created"}

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    token = create_jwt_token(db_user.id)
    return {"access_token": token}
"""