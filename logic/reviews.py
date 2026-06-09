"""
logic/reviews.py
─────────────────
Create, fetch, and summarise seller reviews.

The `reviews` table already exists in the DB with columns:
  id, match_id, reviewer_id, seller_id, rating (1-5), comment, created_at

This module wraps all review-related operations.
"""

from database.db import get_session
from database.models import Review, Match, User


# ── Write ─────────────────────────────────────────────────────────────────

def submit_review(
    match_id: int,
    reviewer_id: int,
    seller_id: int,
    rating: int,
    comment: str = "",
) -> tuple[bool, str]:
    """
    Submit a rating + optional comment after a completed match.

    Rules
    ─────
    • Rating must be 1–5.
    • Match must exist and be 'completed'.
    • reviewer_id must be the buyer in that match (not the seller).
    • Can only review once per match.

    Returns (True, "Review submitted!") on success,
            (False, error_message) on failure.
    """
    if not (1 <= rating <= 5):
        return False, "Rating must be between 1 and 5."

    db = get_session()

    match = db.query(Match).filter_by(id=match_id).first()
    if not match:
        return False, "Match not found."
    if match.status != "completed":
        return False, "You can only review after a match is completed."
    if match.buyer_id != reviewer_id:
        return False, "Only the buyer can leave a review."

    existing = (
        db.query(Review)
        .filter_by(match_id=match_id, reviewer_id=reviewer_id)
        .first()
    )
    if existing:
        return False, "You have already reviewed this transaction."

    try:
        db.add(
            Review(
                match_id=match_id,
                reviewer_id=reviewer_id,
                seller_id=seller_id,
                rating=rating,
                comment=comment[:500],
            )
        )
        db.commit()
        return True, "Review submitted! Thank you."
    except Exception as e:
        db.rollback()
        return False, f"Something went wrong: {e}"


# ── Read ──────────────────────────────────────────────────────────────────

def get_reviews_for_seller(seller_id: int) -> list:
    """Return all Review rows for a seller, newest first."""
    db = get_session()
    return (
        db.query(Review)
        .filter_by(seller_id=seller_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def get_average_rating(seller_id: int) -> float | None:
    """Return average rating (float) or None if no reviews yet."""
    reviews = get_reviews_for_seller(seller_id)
    if not reviews:
        return None
    return round(sum(r.rating for r in reviews) / len(reviews), 1)


def get_review_summary(seller_id: int) -> dict:
    """
    Returns a summary dict:
    {
        "average": 4.3,          # float or None
        "count": 12,
        "distribution": {1:0, 2:1, 3:2, 4:5, 5:4},
        "reviews": [...]          # full Review objects, newest first
    }
    """
    reviews = get_reviews_for_seller(seller_id)
    dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    for r in reviews:
        dist[r.rating] = dist.get(r.rating, 0) + 1

    avg = (
        round(sum(r.rating for r in reviews) / len(reviews), 1)
        if reviews
        else None
    )
    return {
        "average": avg,
        "count": len(reviews),
        "distribution": dist,
        "reviews": reviews,
    }


def can_review(match_id: int, reviewer_id: int) -> bool:
    """True if this user can still leave a review for this match."""
    db = get_session()
    match = db.query(Match).filter_by(id=match_id).first()
    if not match or match.status != "completed":
        return False
    if match.buyer_id != reviewer_id:
        return False
    existing = (
        db.query(Review)
        .filter_by(match_id=match_id, reviewer_id=reviewer_id)
        .first()
    )
    return existing is None
