from typing import Optional
from datetime import timedelta
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.models.user import User
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    """
    Service for authentication operations.
    Handles business logic for user registration and login.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the service with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.user_repository = UserRepository(db)
    
    def register(self, user_create: UserCreate) -> Optional[UserResponse]:
        """
        Register a new user.
        
        Args:
            user_create: User registration data
            
        Returns:
            UserResponse if registration successful, None if username/email already exists
        """
        # Check if email already exists
        if self.user_repository.get_by_email(user_create.email):
            return None
        
        # Check if username already exists
        if self.user_repository.get_by_username(user_create.username):
            return None
        
        # Create user
        db_user = self.user_repository.create(user_create)
        if not db_user:
            return None
        
        # Return user response (without password)
        return UserResponse.model_validate(db_user)
    
    def login(self, user_login: UserLogin) -> Optional[Token]:
        """
        Authenticate a user and generate access token.
        
        Args:
            user_login: User login credentials
            
        Returns:
            Token object if authentication successful, None otherwise
        """
        # Get user by username
        db_user = self.user_repository.get_by_username(user_login.username)
        if not db_user:
            return None
        
        # Check if user is active
        if not db_user.is_active:
            return None
        
        # Verify password
        if not verify_password(user_login.password, db_user.hashed_password):
            return None
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(db_user.id)},
            expires_delta=access_token_expires
        )
        
        return Token(access_token=access_token, token_type="bearer")
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate a user by username and password.
        
        Args:
            username: The username
            password: The plain password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        db_user = self.user_repository.get_by_username(username)
        if not db_user:
            return None
        
        if not db_user.is_active:
            return None
        
        if not verify_password(password, db_user.hashed_password):
            return None
        
        return db_user
    
    def get_user_by_id(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            UserResponse if user found, None otherwise
        """
        db_user = self.user_repository.get_by_id(user_id)
        if not db_user:
            return None
        
        return UserResponse.model_validate(db_user)

