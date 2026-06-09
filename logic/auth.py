import bcrypt
from database.db_example import get_session
from database.models import User

session_user = None

def register(name, email, password, city, college_or_company):
    db = get_session()
    try:
        if db.query(User).filter_by(email=email).first():
            return False, "Email already registered!"
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        user = User(
            name=name,
            email=email,
            password_hash=hashed.decode(),
            city=city,
            college_or_company=college_or_company
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return True, user
    except Exception as e:
        db.rollback()
        return False, str(e)

def login(email, password):
    global session_user
    db = get_session()
    try:
        user = db.query(User).filter_by(email=email).first()
        if user and bcrypt.checkpw(password.encode(), user.password_hash.encode()):
            # Expunge so user object lives outside session safely
            db.expunge(user)
            session_user = user
            return True, user
        return False, "Invalid email or password"
    except Exception as e:
        return False, str(e)

def get_current_user():
    return session_user

def logout():
    global session_user
    session_user = None