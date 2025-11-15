from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash


class UserRepository:
    """
    Repository for User database operations.
    Implements the Repository Pattern for data access abstraction.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the repository with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
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
        Get a user by email.
        
        Args:
            email: The user's email
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_by_username(self, username: str) -> Optional[User]:
        """
        Get a user by username.
        
        Args:
            username: The user's username
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.username == username).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all users with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of User objects
        """
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def create(self, user_create: UserCreate) -> Optional[User]:
        """
        Create a new user.
        
        Args:
            user_create: User creation schema with user data
            
        Returns:
            Created User object if successful, None if username/email already exists
        """
        try:
            # Hash the password
            hashed_password = get_password_hash(user_create.password)
            
            # Create user object
            db_user = User(
                email=user_create.email,
                username=user_create.username,
                hashed_password=hashed_password,
                full_name=user_create.full_name,
                is_active=True,
                is_superuser=False,
            )
            
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
            
            return db_user
        except IntegrityError:
            self.db.rollback()
            return None
    
    def update(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """
        Update a user.
        
        Args:
            user_id: The user's ID
            user_update: User update schema with fields to update
            
        Returns:
            Updated User object if successful, None if user not found
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        # Update only provided fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Hash password if provided
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
            return db_user
        except IntegrityError:
            self.db.rollback()
            return None
    
    def delete(self, user_id: int) -> bool:
        """
        Delete a user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if deleted successfully, False if user not found
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
    
    def activate(self, user_id: int) -> Optional[User]:
        """
        Activate a user account.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Updated User object if successful, None if user not found
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.is_active = True
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def deactivate(self, user_id: int) -> Optional[User]:
        """
        Deactivate a user account.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Updated User object if successful, None if user not found
        """
        db_user = self.get_by_id(user_id)
        if not db_user:
            return None
        
        db_user.is_active = False
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

