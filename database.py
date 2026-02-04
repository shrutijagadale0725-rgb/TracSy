"""
database.py
SQLAlchemy database setup and models for Personal Budget Monitoring System.
Defines User and Transaction models with relationships.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

# Create Base class for declarative models
Base = declarative_base()

# Database file path
DB_FILE = 'finance.db'
DATABASE_URL = f'sqlite:///{DB_FILE}'

# Create database engine
engine = create_engine(DATABASE_URL, echo=False)

# Create session factory
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    """
    User model for storing user authentication information.
    Each user has a unique username and hashed password.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password = Column(String(128), nullable=False)  # Hashed password (SHA-256)
    
    # Relationship: One user can have many transactions
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Transaction(Base):
    """
    Transaction model for storing income and expense records.
    Each transaction belongs to a specific user.
    """
    __tablename__ = 'transactions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    date = Column(Date, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    transaction_type = Column(String(10), nullable=False)  # 'Income' or 'Expense'
    
    # Relationship: Many transactions belong to one user
    user = relationship('User', back_populates='transactions')
    
    def __repr__(self):
        return f"<Transaction(id={self.id}, user_id={self.user_id}, type={self.transaction_type}, amount={self.amount})>"


def init_db():
    """
    Initialize the database by creating all tables.
    This function is called when the application starts.
    """
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def get_db():
    """
    Get a database session.
    Returns a new database session for performing operations.
    """
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        db.close()
        raise e