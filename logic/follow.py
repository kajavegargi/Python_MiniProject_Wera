"""
logic/follow.py
───────────────
All follow / unfollow / follower-count helpers.
"""

from database.db import get_session
from database.models import Follow          # Follow is the new model
from sqlalchemy.exc import IntegrityError


# ── Core actions ──────────────────────────────────────────────────────────

def follow_user(follower_id: int, following_id: int) -> bool:
    """
    Follow another user.
    Returns True on success, False if already following or same user.
    """
    if follower_id == following_id:
        return False

    db = get_session()
    existing = (
        db.query(Follow)
        .filter_by(follower_id=follower_id, following_id=following_id)
        .first()
    )
    if existing:
        return False  # already following

    try:
        db.add(Follow(follower_id=follower_id, following_id=following_id))
        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def unfollow_user(follower_id: int, following_id: int) -> bool:
    """
    Unfollow a user.
    Returns True if the follow row was deleted, False if it didn't exist.
    """
    db = get_session()
    row = (
        db.query(Follow)
        .filter_by(follower_id=follower_id, following_id=following_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def is_following(follower_id: int, following_id: int) -> bool:
    """Return True if follower_id already follows following_id."""
    db = get_session()
    return (
        db.query(Follow)
        .filter_by(follower_id=follower_id, following_id=following_id)
        .first()
    ) is not None


# ── Counts & lists ────────────────────────────────────────────────────────

def get_follower_count(user_id: int) -> int:
    """How many users follow user_id."""
    db = get_session()
    return db.query(Follow).filter_by(following_id=user_id).count()


def get_following_count(user_id: int) -> int:
    """How many users user_id is following."""
    db = get_session()
    return db.query(Follow).filter_by(follower_id=user_id).count()


def get_followers(user_id: int) -> list:
    """Return list of User objects who follow user_id."""
    from database.models import User
    db = get_session()
    rows = db.query(Follow).filter_by(following_id=user_id).all()
    ids = [r.follower_id for r in rows]
    return db.query(User).filter(User.id.in_(ids)).all()


def get_following(user_id: int) -> list:
    """Return list of User objects that user_id follows."""
    from database.models import User
    db = get_session()
    rows = db.query(Follow).filter_by(follower_id=user_id).all()
    ids = [r.following_id for r in rows]
    return db.query(User).filter(User.id.in_(ids)).all()
