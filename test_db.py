from database.db import init_db, get_session
from database.models import User

init_db()
print("✅ Tables created!")
db = get_session()
print(f"✅ Connected! Users: {db.query(User).count()}")