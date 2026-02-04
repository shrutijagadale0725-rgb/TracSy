# 💰 Personal Budget Monitoring System

A comprehensive personal finance management application built with Python and Streamlit for undergraduate final year project.

## 📋 Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Installation](#installation)
- [How to Run](#how-to-run)
- [Usage Guide](#usage-guide)
- [CSV Upload Format](#csv-upload-format)
- [PDF Upload](#pdf-upload)
- [Screenshots](#screenshots)
- [Project Architecture](#project-architecture)

## 🎯 Project Overview

**Project Title:** Personal Budget Monitoring System  
**Level:** Undergraduate / Fresher Level  
**Purpose:** Final Year Computer Science Project

This system allows users to track their income and expenses through manual entry or bulk upload via CSV/PDF files. It provides visual analytics and helps users monitor their financial health.

## ✨ Features

### Core Features
- ✅ User Registration & Login System
- ✅ Secure Password Hashing (SHA-256 with salt)
- ✅ Multi-user Support with Data Isolation
- ✅ Manual Transaction Entry (Income/Expense)
- ✅ Transaction Categorization
- ✅ Transaction History View
- ✅ Financial Analytics & Visualizations

### Advanced Features
- 📁 **CSV File Upload**
  - Automatic column detection
  - Support for multiple column name variations
  - Preview before saving
  - Bulk transaction import
  - Category mapping

- 📄 **PDF File Upload**
  - Automatic amount extraction using regex
  - Context-based description capture
  - Date detection
  - Limited preview (20 transactions)
  - Configurable categorization

### Visualizations
- 📊 Expense Breakdown Pie Chart
- 📈 Income vs Expense Bar Chart
- 📉 Financial Summary Chart

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.8+ |
| **UI Framework** | Streamlit |
| **ORM** | SQLAlchemy |
| **Database** | SQLite |
| **Visualization** | Matplotlib |
| **Data Processing** | Pandas |
| **PDF Parsing** | PyPDF2 |
| **Password Hashing** | hashlib (built-in) |

## 📁 Project Structure

```
finance_app/
├── main.py                # Streamlit UI (entry point)
├── database.py            # SQLAlchemy DB setup & models
├── auth.py                # Login & registration logic
├── crud.py                # Transaction DB operations
├── charts.py              # Matplotlib charts
├── file_parser.py         # CSV/PDF parsing module
├── finance.db             # SQLite database (auto-created)
├── requirements.txt       # Python dependencies
└── README.md              # Documentation
```

### File Descriptions

#### 1. **main.py**
- Entry point of the application
- Streamlit UI implementation
- User interface for login, registration, manual entry, file uploads
- Tab-based navigation
- Session state management

#### 2. **database.py**
- SQLAlchemy ORM setup
- Database models (User, Transaction)
- Database initialization
- Session management

#### 3. **auth.py**
- User authentication logic
- Password hashing with SHA-256 + salt
- Registration and login functions
- Password verification

#### 4. **crud.py**
- CRUD operations for transactions
- Single transaction operations
- Bulk transaction insert
- Query functions for analytics
- Summary calculations

#### 5. **charts.py**
- Matplotlib visualization functions
- Pie chart for expense breakdown
- Bar chart for income vs expense
- Summary chart generation

#### 6. **file_parser.py**
- CSV parsing with pandas
- PDF text extraction with PyPDF2
- Regex-based amount detection
- Validation functions
- Support for multiple column name variations

## 🗄️ Database Schema

### Users Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Auto-increment |
| username | String(50) | Unique, Not Null |
| password | String(128) | Not Null (Hashed) |

### Transactions Table
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | Primary Key, Auto-increment |
| user_id | Integer | Foreign Key (users.id), Not Null |
| date | Date | Not Null |
| amount | Float | Not Null |
| category | String(50) | Not Null |
| description | String(200) | Nullable |
| transaction_type | String(10) | Not Null ('Income' or 'Expense') |

### Relationships
- One User → Many Transactions
- Cascade delete: When user is deleted, all their transactions are deleted

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step-by-Step Installation

1. **Clone or Download the Project**
```bash
cd finance_app
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

**Note:** If you encounter installation issues on Windows, you may need to install Microsoft C++ Build Tools for some packages.

## ▶️ How to Run

1. **Navigate to Project Directory**
```bash
cd finance_app
```

2. **Run the Application**
```bash
streamlit run main.py
```

3. **Access the Application**
- The application will automatically open in your default browser
- Default URL: `http://localhost:8501`

4. **First Time Setup**
- Register a new account
- Login with your credentials
- Start adding transactions!

## 📖 Usage Guide

### 1. Registration & Login
- Click on "Register" tab
- Enter username (min 3 characters) and password (min 6 characters)
- After registration, login with your credentials

### 2. Manual Transaction Entry
- Navigate to "Add Transaction" tab
- Select transaction type (Income/Expense)
- Choose category
- Enter amount and description
- Click "Save Transaction"

### 3. CSV File Upload

#### Supported Column Names
The system automatically detects these column name variations:

**Date Column:**
- date, Date, transaction_date, trans_date, dt, transaction date, txn_date

**Amount Column:**
- amount, Amount, amt, value, price, total

**Description Column:**
- description, desc, details, particular, particulars, narration, remarks

**Category Column (Optional):**
- category, cat, type, expense_type, income_type

#### CSV Upload Steps
1. Go to "Upload Transactions" tab
2. Click "Browse files" and select CSV file
3. Review the preview of first 10 rows
4. Select transaction type (Income/Expense)
5. Choose to use CSV categories or override with a single category
6. Click "Save All Transactions"

#### Example CSV Format
```csv
date,amount,description,category
2024-01-15,5000,January Salary,Salary
2024-01-16,250,Grocery Shopping,Food
2024-01-17,1200,Electricity Bill,Bills
2024-01-18,500,Movie Night,Entertainment
```

#### CSV with Different Column Names
```csv
Date,Amount,Particulars
15-01-2024,5000,Salary Credit
16-01-2024,250,Grocery Store
```

### 4. PDF File Upload

#### How PDF Parsing Works
- Extracts text from all pages
- Uses regex patterns to find amounts:
  - ₹1234.56
  - $500
  - Rs. 1234
  - 1234.56
- Captures surrounding text as description
- Limited to 20 transactions for preview

#### PDF Upload Steps
1. Go to "Upload Transactions" tab
2. Upload PDF file containing transaction amounts
3. Review extracted transactions (max 20 shown)
4. Select transaction type and category for all
5. Click "Save All Transactions"

### 5. View Analytics
- Navigate to "View & Analyze" tab
- See expense breakdown by category (pie chart)
- Compare income vs expense (bar chart)
- View financial summary

### 6. Transaction History
- Go to "Transaction History" tab
- Filter by transaction type (All/Income/Expense)
- View complete transaction list in table format

## 📊 Categories

### Income Categories
- Salary
- Freelance
- Investment
- Gift
- Other

### Expense Categories
- Food
- Transport
- Shopping
- Bills
- Entertainment
- Healthcare
- Education
- Other

## 🏗️ Project Architecture

```
User (Browser)
    ↓
Streamlit UI (main.py)
    ↓
┌─────────────┬──────────────┬─────────────┐
│   Auth      │    CRUD      │   Charts    │
│  (auth.py)  │  (crud.py)   │ (charts.py) │
└─────────────┴──────────────┴─────────────┘
         ↓                              ↓
    Database Layer              File Parser
  (database.py)              (file_parser.py)
         ↓
    SQLite DB
   (finance.db)
```

## 🔐 Security Features

- **Password Hashing:** SHA-256 with random salt
- **Data Isolation:** Users can only access their own transactions
- **Session Management:** Secure session state using Streamlit
- **SQL Injection Prevention:** Using SQLAlchemy ORM

## 📝 Important Notes

### What's Included ✅
- User authentication system
- Manual transaction entry
- CSV/PDF bulk upload
- Data visualization
- Transaction history
- Multi-user support
- Data isolation per user

### What's NOT Included ❌
- Password reset functionality
- Email verification
- Export to Excel/PDF
- Budget limits/alerts
- Recurring transactions
- Multi-currency support
- Cloud storage
- Machine learning predictions
- Advanced analytics
- Mobile app

## 🐛 Troubleshooting

### Common Issues

**1. Database not created**
- The database is auto-created on first run
- Check if `finance.db` exists in the project directory

**2. Import errors**
- Make sure all dependencies are installed: `pip install -r requirements.txt`
- Use Python 3.8 or higher

**3. CSV upload fails**
- Check if CSV has 'date' and 'amount' columns
- Ensure date format is recognizable (YYYY-MM-DD, DD-MM-YYYY, etc.)
- Amounts should be numeric (₹, $, commas are automatically removed)

**4. PDF extraction returns no results**
- Ensure PDF contains extractable text (not scanned images)
- Check if amounts are in recognizable format
- PDFs with complex layouts may have issues

**5. Streamlit won't start**
- Check if port 8501 is already in use
- Try: `streamlit run main.py --server.port 8502`

## 👨‍💻 Developer Information

**Project Type:** Final Year Undergraduate Project  
**Suitable For:** Computer Science students  
**Difficulty Level:** Intermediate  
**Development Time:** 2-3 weeks  

## 📄 License

This project is developed for educational purposes as a final year project.

## 🤝 Contributing

This is a student project template. Feel free to:
- Add more features
- Improve UI/UX
- Enhance security
- Add export functionality
- Implement budget tracking

## 📞 Support

For issues or questions regarding this project:
1. Check the troubleshooting section
2. Review the code comments
3. Consult with your project guide

---

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** Production Ready for Academic Submission

## 🎓 Academic Usage

### Project Presentation Points
- Demonstrate user registration and login
- Show manual transaction entry
- Upload sample CSV file
- Upload sample PDF file
- Show data visualizations
- Explain database schema
- Discuss security implementation
- Talk about file parsing logic

### Viva Questions You Should Prepare For
1. Why SQLite instead of MySQL/PostgreSQL?
2. Why hashlib instead of bcrypt?
3. How does the CSV parsing handle different column names?
4. Explain the regex patterns used for PDF parsing
5. How is data isolation implemented?
6. What is the relationship between User and Transaction tables?
7. How does session management work?
8. What are the limitations of the current implementation?

---

**Good Luck with Your Project! 🎉**