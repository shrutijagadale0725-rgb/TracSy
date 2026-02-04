"""
file_parser.py
File parsing module for CSV and PDF transaction files.
Handles parsing, validation, and data extraction from uploaded files.
"""

import pandas as pd
import re
from datetime import datetime
from pypdf import PdfReader


def parse_csv(file):
    """
    Parse CSV file containing transaction data.
    Supports multiple column name variations.
    
    Args:
        file: Uploaded CSV file object
    
    Returns:
        pandas.DataFrame or None: Parsed DataFrame with standardized columns
                                  (date, amount, description, category)
                                  Returns None if parsing fails
    """
    try:
        # Read CSV file
        df = pd.read_csv(file)
        
        # Standardize column names (convert to lowercase for matching)
        df.columns = df.columns.str.strip().str.lower()
        
        # Column name mappings for different variations
        date_columns = ['date', 'transaction_date', 'trans_date', 'dt', 'transaction date', 'txn_date']
        amount_columns = ['amount', 'amt', 'value', 'price', 'total']
        description_columns = ['description', 'desc', 'details', 'particular', 'particulars', 'narration', 'remarks']
        category_columns = ['category', 'cat', 'type', 'expense_type', 'income_type']
        
        # Find matching columns
        date_col = None
        amount_col = None
        description_col = None
        category_col = None
        
        for col in df.columns:
            if col in date_columns and date_col is None:
                date_col = col
            elif col in amount_columns and amount_col is None:
                amount_col = col
            elif col in description_columns and description_col is None:
                description_col = col
            elif col in category_columns and category_col is None:
                category_col = col
        
        # Check if required columns found
        if date_col is None or amount_col is None:
            return None
        
        # Create standardized DataFrame
        result_df = pd.DataFrame()
        result_df['date'] = df[date_col]
        result_df['amount'] = df[amount_col]
        
        # Add optional columns
        if description_col:
            result_df['description'] = df[description_col]
        else:
            result_df['description'] = 'Imported from CSV'
        
        if category_col:
            result_df['category'] = df[category_col]
        else:
            result_df['category'] = None  # Will be set by user
        
        # Clean amount column - remove currency symbols and convert to float
        result_df['amount'] = result_df['amount'].astype(str).str.replace('[₹$,]', '', regex=True).str.strip()
        result_df['amount'] = pd.to_numeric(result_df['amount'], errors='coerce')
        
        # Parse dates with multiple format support
        result_df['date'] = pd.to_datetime(result_df['date'], errors='coerce', infer_datetime_format=True)
        
        # Drop rows with invalid dates or amounts
        result_df = result_df.dropna(subset=['date', 'amount'])
        
        # Convert date to date object (remove time component)
        result_df['date'] = result_df['date'].dt.date
        
        # Fill empty descriptions
        result_df['description'] = result_df['description'].fillna('Imported from CSV')
        
        return result_df
        
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return None


def parse_pdf(file, max_transactions=20):
    """
    Parse PDF file to extract transaction amounts and descriptions.
    Uses regex patterns to find monetary amounts.
    
    Args:
        file: Uploaded PDF file object
        max_transactions (int): Maximum number of transactions to extract
    
    Returns:
        list or None: List of dictionaries with 'amount', 'description', 'date'
                     Returns None if parsing fails
    """
    try:
        # Read PDF
        pdf_reader = PdfReader(file)
        
        # Extract text from all pages
        full_text = ""
        for page in pdf_reader.pages:
            full_text += page.extract_text() + "\n"
        
        if not full_text.strip():
            return None
        
        # Regex patterns for finding amounts
        # Matches: ₹1234.56, $500, Rs. 1234, Rs 1234.56, 1234.56, 12,345.67
        amount_patterns = [
            r'[₹$]\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # ₹1234.56, $500.00
            r'Rs\.?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Rs. 1234, Rs 1234.56
            r'INR\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',    # INR 1234.56
            r'(?<!\d)(\d{1,3}(?:,\d{3})*\.\d{2})(?!\d)',  # 1234.56, 12,345.67
            r'(?<!\d)(\d{3,})(?!\d)'                       # 1234 (3+ digits)
        ]
        
        transactions = []
        lines = full_text.split('\n')
        
        for line in lines:
            if len(transactions) >= max_transactions:
                break
            
            line = line.strip()
            if not line:
                continue
            
            # Try each pattern
            for pattern in amount_patterns:
                matches = re.findall(pattern, line)
                
                for match in matches:
                    if len(transactions) >= max_transactions:
                        break
                    
                    # Clean amount (remove commas)
                    amount_str = match.replace(',', '')
                    
                    try:
                        amount = float(amount_str)
                        
                        # Filter out unrealistic amounts
                        if amount < 1 or amount > 10000000:
                            continue
                        
                        # Extract description (context around the amount)
                        description = line[:100]  # First 100 characters of the line
                        
                        # Try to extract date from the line
                        date_match = re.search(r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})', line)
                        if date_match:
                            try:
                                date_str = date_match.group(1)
                                parsed_date = pd.to_datetime(date_str, errors='coerce')
                                if pd.notna(parsed_date):
                                    trans_date = parsed_date.date()
                                else:
                                    trans_date = datetime.today().date()
                            except:
                                trans_date = datetime.today().date()
                        else:
                            trans_date = datetime.today().date()
                        
                        transactions.append({
                            'amount': amount,
                            'description': description if description else 'Extracted from PDF',
                            'date': trans_date
                        })
                        
                    except ValueError:
                        continue
        
        return transactions if transactions else None
        
    except Exception as e:
        print(f"Error parsing PDF: {e}")
        return None


def validate_csv_structure(df):
    """
    Validate if the parsed CSV DataFrame has the required structure.
    
    Args:
        df (pandas.DataFrame): Parsed DataFrame
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if df is None or df.empty:
        return False, "CSV file is empty or could not be parsed!"
    
    required_columns = ['date', 'amount']
    for col in required_columns:
        if col not in df.columns:
            return False, f"Missing required column: '{col}'"
    
    # Check for at least one valid row
    if len(df) == 0:
        return False, "No valid transactions found in CSV!"
    
    # Check for null values in required columns
    if df['date'].isnull().any():
        return False, "Some date values are invalid!"
    
    if df['amount'].isnull().any():
        return False, "Some amount values are invalid!"
    
    return True, "CSV structure is valid!"


def validate_pdf_transactions(transactions):
    """
    Validate extracted PDF transactions.
    
    Args:
        transactions (list): List of transaction dictionaries
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not transactions or len(transactions) == 0:
        return False, "No transactions found in PDF! Make sure the PDF contains monetary amounts."
    
    # Check each transaction has required fields
    for trans in transactions:
        if 'amount' not in trans or 'description' not in trans or 'date' not in trans:
            return False, "Invalid transaction structure!"
        
        if trans['amount'] <= 0:
            return False, "Invalid amount found in transactions!"
    
    return True, f"Successfully extracted {len(transactions)} transactions from PDF!"


def clean_amount(amount_str):
    """
    Clean and convert amount string to float.
    Handles currency symbols, commas, etc.
    
    Args:
        amount_str (str or float): Amount as string or number
    
    Returns:
        float: Cleaned amount value
    """
    try:
        if isinstance(amount_str, (int, float)):
            return float(amount_str)
        
        # Remove currency symbols and commas
        cleaned = str(amount_str).replace('₹', '').replace('$', '').replace('Rs.', '').replace('Rs', '').replace(',', '').strip()
        return float(cleaned)
    except:

        return 0.0
