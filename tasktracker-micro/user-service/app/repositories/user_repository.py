from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository for user data access operations.
    Handles all database operations related to users.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create(self, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user in the database.
        
        Args:
            user_create: User creation data
            
        Returns:
            Created user object, or None if creation failed
        """
        try:
            db_user = User(
                email=user_create.email,
                username=user_create.username,
                hashed_password=get_password_hash(user_create.password),
                full_name=user_create.full_name,
                is_active=True,
                is_superuser=False
            )
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            return None
    
    def get_by_id(self, user_id: int) -> Optional[User]:
        """
        Get a user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email address.
        
        Args:
            email: The user's email address
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The username
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def update(self, user_id: int, **kwargs) -> Optional[User]:
        """
        Update a user's information.
        
        Args:
            user_id: The user's ID
            **kwargs: Fields to update
            
        Returns:
            Updated user object if found, None otherwise
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        for key, value in kwargs.items():
            if hasattr(db_user, key):
                setattr(db_user, key, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user by ID.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if user was deleted, False otherwise
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True

