from database.db_example import get_session
from database.models import Message

def send_message(match_id, sender_id, content):
    db = get_session()
    try:
        msg = Message(
            match_id=match_id,
            sender_id=sender_id,
            content=content
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg
    except Exception as e:
        db.rollback()
        return None

def get_messages(match_id):
    db = get_session()
    messages = (
        db.query(Message)
        .filter_by(match_id=match_id)
        .order_by(Message.sent_at.asc())
        .all()
    )
    for m in messages:
        db.expunge(m)
    return messages