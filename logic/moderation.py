"""
logic/moderation.py
────────────────────
Block / unblock and report helpers.
"""

from database.db import get_session
from database.models import Block, Report
from sqlalchemy.exc import IntegrityError


# ── BLOCKING ──────────────────────────────────────────────────────────────

def block_user(blocker_id: int, blocked_id: int) -> bool:
    """
    Block a user.
    Also removes any follow relationship between the two users.
    Returns True on success, False if already blocked or same user.
    """
    if blocker_id == blocked_id:
        return False

    db = get_session()
    existing = (
        db.query(Block)
        .filter_by(blocker_id=blocker_id, blocked_id=blocked_id)
        .first()
    )
    if existing:
        return False

    try:
        db.add(Block(blocker_id=blocker_id, blocked_id=blocked_id))

        # Remove any mutual follows
        from database.models import Follow
        for fk, fv in [
            (blocker_id, blocked_id),
            (blocked_id, blocker_id),
        ]:
            row = db.query(Follow).filter_by(
                follower_id=fk, following_id=fv
            ).first()
            if row:
                db.delete(row)

        db.commit()
        return True
    except IntegrityError:
        db.rollback()
        return False


def unblock_user(blocker_id: int, blocked_id: int) -> bool:
    """Unblock a previously blocked user."""
    db = get_session()
    row = (
        db.query(Block)
        .filter_by(blocker_id=blocker_id, blocked_id=blocked_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def is_blocked(blocker_id: int, blocked_id: int) -> bool:
    """True if blocker_id has blocked blocked_id."""
    db = get_session()
    return (
        db.query(Block)
        .filter_by(blocker_id=blocker_id, blocked_id=blocked_id)
        .first()
    ) is not None


def is_blocked_either_way(user_a: int, user_b: int) -> bool:
    """True if either user has blocked the other (used to hide content)."""
    return is_blocked(user_a, user_b) or is_blocked(user_b, user_a)


def get_blocked_ids(user_id: int) -> list[int]:
    """Return list of user IDs that user_id has blocked."""
    db = get_session()
    rows = db.query(Block).filter_by(blocker_id=user_id).all()
    return [r.blocked_id for r in rows]


# ── REPORTING ─────────────────────────────────────────────────────────────

VALID_REASONS = [
    "Spam or scam",
    "Inappropriate content",
    "Fake account",
    "Harassment",
    "Counterfeit item",
    "Other",
]


def report_user(
    reporter_id: int,
    reported_id: int,
    reason: str,
    details: str = "",
) -> tuple[bool, str]:
    """
    Submit a report against a user.

    Returns (True, "Report submitted") on success,
            (False, reason_string) on failure.
    """
    if reporter_id == reported_id:
        return False, "You cannot report yourself."

    if reason not in VALID_REASONS:
        return False, f"Invalid reason. Choose from: {', '.join(VALID_REASONS)}"

    db = get_session()
    # Prevent duplicate pending reports from the same user about the same user
    existing = (
        db.query(Report)
        .filter_by(reporter_id=reporter_id, reported_id=reported_id, status="pending")
        .first()
    )
    if existing:
        return False, "You already have a pending report against this user."

    try:
        db.add(
            Report(
                reporter_id=reporter_id,
                reported_id=reported_id,
                reason=reason,
                details=details[:500],
            )
        )
        db.commit()
        return True, "Report submitted. Our team will review it shortly."
    except Exception as e:
        db.rollback()
        return False, f"Something went wrong: {e}"


def get_reports_against(user_id: int) -> list:
    """Return all Report rows filed against user_id (admin use)."""
    db = get_session()
    return (
        db.query(Report)
        .filter_by(reported_id=user_id)
        .order_by(Report.created_at.desc())
        .all()
    )
