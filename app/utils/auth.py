from fastapi import Header, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.user import User

def get_current_user(
    authorization: str = Header(...),
    db: Session = Depends(get_db)
):
    try:
        token = authorization.split(" ")[1]  # Bearer <token>
    except:
        raise HTTPException(status_code=401, detail="Invalid token format")

    user = db.query(User).filter(User.token == token).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user