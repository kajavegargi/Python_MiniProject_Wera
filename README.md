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


## Project Structure
```text
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
```
## Made by
- ILISHA SHAH - www.linkedin.com/in/ilisha-shah
- GARGI KAJAVE - www.linkedin.com/in/gargikajave
- ARYA DIXIT - www.linkedin.com/in/arya-dixit-0485b2308
- JANHAVI KHARE - www.linkedin.com/in/janhavi-khare0911
