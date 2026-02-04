"""
crud.py
CRUD (Create, Read, Update, Delete) operations for transactions.
Handles all database interactions for transaction management.
"""

from datetime import datetime
from database import Transaction, get_db
from sqlalchemy import func


def add_transaction(user_id, date, amount, category, description, transaction_type):
    """
    Add a single transaction to the database.
    
    Args:
        user_id (int): ID of the user
        date (datetime.date): Transaction date
        amount (float): Transaction amount
        category (str): Transaction category
        description (str): Transaction description
        transaction_type (str): 'Income' or 'Expense'
    
    Returns:
        tuple: (success: bool, message: str)
    """
    db = get_db()
    try:
        new_transaction = Transaction(
            user_id=user_id,
            date=date,
            amount=float(amount),
            category=category,
            description=description,
            transaction_type=transaction_type
        )
        db.add(new_transaction)
        db.commit()
        return True, "Transaction added successfully!"
    except Exception as e:
        db.rollback()
        return False, f"Error adding transaction: {str(e)}"
    finally:
        db.close()


def bulk_add_transactions(user_id, transactions_list):
    """
    Add multiple transactions to the database at once.
    Used for CSV/PDF uploads.
    
    Args:
        user_id (int): ID of the user
        transactions_list (list): List of transaction dictionaries with keys:
                                 'date', 'amount', 'category', 'description', 'transaction_type'
    
    Returns:
        tuple: (success: bool, message: str, count: int)
    """
    db = get_db()
    try:
        added_count = 0
        for trans_data in transactions_list:
            new_transaction = Transaction(
                user_id=user_id,
                date=trans_data['date'],
                amount=float(trans_data['amount']),
                category=trans_data['category'],
                description=trans_data.get('description', ''),
                transaction_type=trans_data['transaction_type']
            )
            db.add(new_transaction)
            added_count += 1
        
        db.commit()
        return True, f"Successfully added {added_count} transactions!", added_count
    except Exception as e:
        db.rollback()
        return False, f"Error adding transactions: {str(e)}", 0
    finally:
        db.close()


def get_all_transactions(user_id):
    """
    Retrieve all transactions for a specific user.
    
    Args:
        user_id (int): ID of the user
    
    Returns:
        list: List of Transaction objects
    """
    db = get_db()
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id
        ).order_by(Transaction.date.desc()).all()
        return transactions
    except Exception as e:
        print(f"Error fetching transactions: {e}")
        return []
    finally:
        db.close()


def get_transactions_by_type(user_id, transaction_type):
    """
    Retrieve transactions filtered by type (Income/Expense).
    
    Args:
        user_id (int): ID of the user
        transaction_type (str): 'Income' or 'Expense'
    
    Returns:
        list: List of Transaction objects
    """
    db = get_db()
    try:
        transactions = db.query(Transaction).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type
        ).order_by(Transaction.date.desc()).all()
        return transactions
    except Exception as e:
        print(f"Error fetching {transaction_type} transactions: {e}")
        return []
    finally:
        db.close()


def get_total_by_type(user_id, transaction_type):
    """
    Calculate total amount for a specific transaction type.
    
    Args:
        user_id (int): ID of the user
        transaction_type (str): 'Income' or 'Expense'
    
    Returns:
        float: Total amount
    """
    db = get_db()
    try:
        total = db.query(func.sum(Transaction.amount)).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type
        ).scalar()
        return total if total else 0.0
    except Exception as e:
        print(f"Error calculating total {transaction_type}: {e}")
        return 0.0
    finally:
        db.close()


def get_expense_by_category(user_id):
    """
    Get expense breakdown by category for a user.
    
    Args:
        user_id (int): ID of the user
    
    Returns:
        dict: Dictionary with categories as keys and total amounts as values
    """
    db = get_db()
    try:
        results = db.query(
            Transaction.category,
            func.sum(Transaction.amount).label('total')
        ).filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == 'Expense'
        ).group_by(Transaction.category).all()
        
        # Convert to dictionary
        expense_dict = {category: float(total) for category, total in results}
        return expense_dict
    except Exception as e:
        print(f"Error fetching expense by category: {e}")
        return {}
    finally:
        db.close()


def delete_transaction(transaction_id, user_id):
    """
    Delete a specific transaction.
    
    Args:
        transaction_id (int): ID of the transaction to delete
        user_id (int): ID of the user (for verification)
    
    Returns:
        tuple: (success: bool, message: str)
    """
    db = get_db()
    try:
        transaction = db.query(Transaction).filter(
            Transaction.id == transaction_id,
            Transaction.user_id == user_id
        ).first()
        
        if transaction:
            db.delete(transaction)
            db.commit()
            return True, "Transaction deleted successfully!"
        else:
            return False, "Transaction not found or unauthorized!"
    except Exception as e:
        db.rollback()
        return False, f"Error deleting transaction: {str(e)}"
    finally:
        db.close()


def get_transaction_summary(user_id):
    """
    Get summary statistics for user's transactions.
    
    Args:
        user_id (int): ID of the user
    
    Returns:
        dict: Dictionary containing total_income, total_expense, balance, transaction_count
    """
    db = get_db()
    try:
        total_income = get_total_by_type(user_id, 'Income')
        total_expense = get_total_by_type(user_id, 'Expense')
        balance = total_income - total_expense
        
        transaction_count = db.query(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id
        ).scalar()
        
        return {
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'transaction_count': transaction_count if transaction_count else 0
        }
    except Exception as e:
        print(f"Error getting transaction summary: {e}")
        return {
            'total_income': 0.0,
            'total_expense': 0.0,
            'balance': 0.0,
            'transaction_count': 0
        }
    finally:
        db.close()