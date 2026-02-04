"""
auth.py
Authentication module for user registration and login.
Uses hashlib (SHA-256) for password hashing with salt.
"""

import hashlib
import os
from database import User, get_db
from sqlalchemy.exc import IntegrityError


def hash_password(password, salt=None):
    """
    Hash a password using SHA-256 with salt.
    
    Args:
        password (str): Plain text password
        salt (str, optional): Salt for hashing. If None, generates new salt.
    
    Returns:
        str: Hashed password in format 'salt$hash'
    """
    if salt is None:
        # Generate a random 32-character salt
        salt = os.urandom(16).hex()
    
    # Combine salt and password, then hash using SHA-256
    pwd_hash = hashlib.sha256((salt + password).encode('utf-8')).hexdigest()
    
    # Return salt and hash combined (salt$hash format)
    return f"{salt}${pwd_hash}"


def verify_password(stored_password, provided_password):
    """
    Verify a provided password against the stored hashed password.
    
    Args:
        stored_password (str): Stored password in 'salt$hash' format
        provided_password (str): Plain text password to verify
    
    Returns:
        bool: True if password matches, False otherwise
    """
    try:
        # Split stored password to get salt and hash
        salt, stored_hash = stored_password.split('$')
        
        # Hash the provided password with the same salt
        provided_hash = hashlib.sha256((salt + provided_password).encode('utf-8')).hexdigest()
        
        # Compare hashes
        return provided_hash == stored_hash
    except Exception as e:
        print(f"Error verifying password: {e}")
        return False


def register_user(username, password):
    """
    Register a new user in the database.
    
    Args:
        username (str): Username (must be unique)
        password (str): Plain text password
    
    Returns:
        tuple: (success: bool, message: str)
    """
    # Input validation
    if not username or not password:
        return False, "Username and password cannot be empty!"
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters long!"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters long!"
    
    # Hash the password
    hashed_pwd = hash_password(password)
    
    # Create new user
    db = get_db()
    try:
        new_user = User(username=username.strip(), password=hashed_pwd)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return True, f"User '{username}' registered successfully!"
    except IntegrityError:
        db.rollback()
        return False, f"Username '{username}' already exists! Please choose another."
    except Exception as e:
        db.rollback()
        return False, f"Registration failed: {str(e)}"
    finally:
        db.close()


def login_user(username, password):
    """
    Authenticate a user with username and password.
    
    Args:
        username (str): Username
        password (str): Plain text password
    
    Returns:
        tuple: (success: bool, message: str, user_id: int or None, username: str or None)
    """
    # Input validation
    if not username or not password:
        return False, "Username and password cannot be empty!", None, None
    
    # Query database for user
    db = get_db()
    try:
        user = db.query(User).filter(User.username == username.strip()).first()
        
        if user is None:
            return False, "Invalid username or password!", None, None
        
        # Verify password
        if verify_password(user.password, password):
            return True, f"Welcome back, {username}!", user.id, user.username
        else:
            return False, "Invalid username or password!", None, None
    except Exception as e:
        return False, f"Login failed: {str(e)}", None, None
    finally:
        db.close()