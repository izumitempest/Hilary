from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..database import get_session
from ..models.user import User, UserCreate, UserRead, Token
from pydantic import BaseModel
from ..auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    decode_access_token,
    create_email_verification_token,
    decode_email_verification_token,
)
from ..services.email_service import email_service

router = APIRouter(prefix="/auth", tags=["Auth"])

class VerificationRequest(BaseModel):
    email: str


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/register")
def register(user_in: UserCreate, session: Session = Depends(get_session)):
    try:
        # Check if user exists (prevent UniqueViolation before it happens)
        existing_user = session.exec(select(User).where(User.email == user_in.email)).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="This email is already registered. Please log in instead.")
        
        db_user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            hashed_password=get_password_hash(user_in.password),
        )
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        token = create_email_verification_token(db_user.email)
        email_success = email_service.send_verification_email(db_user.email, token)

        if not email_success:
            # Do not throw a 500 error here. Allow the user record to stand, but tell them to retry.
            return {
                "status": "partial_success",
                "message": "Account created successfully, but your verification email failed to dispatch. Please use the resend option.",
                "user": db_user
            }

        return {"status": "success", "message": "User registered. Please confirm your email.", "user": db_user}
    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e).lower()
        if "unique violation" in error_msg or "already exists" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists.",
            ) from e
        
        # Log unexpected errors for debugging
        print(f"CRITICAL REGISTRATION ERROR: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"Registration Error: {str(e)}"
        ) from e

@router.get("/me", response_model=UserRead)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email before logging in.",
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify-email")
def verify_email(token: str, session: Session = Depends(get_session)):
    payload = decode_email_verification_token(token)
    if not payload:
        raise HTTPException(status_code=400, detail="Invalid or expired verification token.")
    email = payload.get("sub")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    if not user.is_verified:
        user.is_verified = True
        session.add(user)
        session.commit()
    return {"status": "verified"}


@router.post("/resend-verification")
def resend_verification(body: VerificationRequest, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == body.email)).first()
    if not user:
        return {"status": "ok"}
    if user.is_verified:
        return {"status": "already_verified"}
    token = create_email_verification_token(user.email)
    email_success = email_service.send_verification_email(user.email, token)
    if not email_success:
        raise HTTPException(status_code=500, detail="Failed to send verification email.")
    return {"status": "sent"}
