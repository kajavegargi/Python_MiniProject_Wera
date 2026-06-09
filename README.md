# Wera 🌿
### Swap. Style. Sustain.

A peer-to-peer clothing platform for Indian college students and young 
working professionals. Buy, sell, or swap clothes sustainably.

Built with Python, CustomTkinter, MySQL and SQLAlchemy.

---

## What it does

- Register and log in securely
- List clothing items to sell or swap with photos
- Browse listings with filters (mode, size, category)
- Send match requests to sellers
- Accept matches and chat inside the platform
- 10% platform fee split across match and completion

---


## Tech Stack

| Layer    | Technology              |
|----------|-------------------------|
| UI       | Python, CustomTkinter   |
| Backend  | Python (OOP modules)    |
| Database | MySQL + SQLAlchemy ORM  |
| Auth     | bcrypt password hashing |
| Images   | Pillow (PIL)            |

---

## How to run this locally

### Prerequisites
- Python 3.10+
- MySQL installed and running

### 1. Clone the repo
git clone https://github.com/IlishaShah2413/Wera.git
cd Wera

### 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install customtkinter sqlalchemy pymysql bcrypt pillow

### 4. Set up MySQL
Open your MySQL command line and run:
```sql
CREATE DATABASE wera_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'wera_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON wera_db.* TO 'wera_user'@'localhost';
FLUSH PRIVILEGES;
```

### 5. Configure database connection
copy database\db_example.py database\db.py
Open `database/db.py` and fill in your MySQL username and password.

### 6. Run
python main.py
Tables are created automatically on first run.

---

## Project Structure
Wera/
├── main.py              — app entry point
├── database/
│   ├── models.py        — SQLAlchemy table definitions
│   ├── db.py            — connection (not on GitHub, create from db_example)
│   └── db_example.py    — connection template
├── logic/
│   ├── auth.py          — register, login, session
│   ├── listings.py      — create, browse, filter, delete
│   ├── match.py         — match requests, fee logic
│   └── chat.py          — in-app messaging
├── ui/
│   ├── theme.py         — Wera brand colors and fonts
│   ├── login_screen.py
│   ├── register_screen.py
│   ├── home_screen.py
│   ├── match_screen.py
│   └── chat_screen.py
└── assets/
└── uploads/         — clothing photos 

---

## Made by
ILISHA SHAH — (www.linkedin.com/in/ilisha-shah)