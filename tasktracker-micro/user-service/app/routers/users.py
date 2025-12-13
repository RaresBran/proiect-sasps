from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.services.user_service import AuthService
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with email, username, and password."
)
def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
) -> UserResponse:
    """
    Register a new user.
    
    Args:
        user_create: User registration data (email, username, password, full_name)
        db: Database session
        
    Returns:
        Created user information (without password)
        
    Raises:
        HTTPException: If username or email already exists
    """
    auth_service = AuthService(db)
    
    # Attempt to register user
    user = auth_service.register(user_create)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user and return access token."
)
def login(
    user_login: UserLogin,
    db: Session = Depends(get_db)
) -> Token:
    """
    Login user and generate access token.
    
    Args:
        user_login: User login credentials (username, password)
        db: Database session
        
    Returns:
        Access token for authenticated requests
        
    Raises:
        HTTPException: If credentials are invalid or user is inactive
    """
    auth_service = AuthService(db)
    
    # Attempt to login
    token = auth_service.login(user_login)
    
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return token


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get information about the currently authenticated user."
)
def get_me(
    current_user: User = Depends(get_current_active_user)
) -> UserResponse:
    """
    Get current authenticated user information.
    
    Args:
        current_user: Current authenticated user (from JWT token)
        
    Returns:
        Current user information (without password)
    """
    return UserResponse.model_validate(current_user)

