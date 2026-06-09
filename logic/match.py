from sqlalchemy.orm import joinedload
from database.db_example import get_session
from database.models import Match, Listing, User


def send_match_request(listing_id, buyer_id,
                       payment_type: str = "points",
                       swap_offer: str = ""):
    """
    Send a match request.

    payment_type options
    --------------------
      "points"     – buyer pays listing.points_value in points (sell mode)
      "money"      – buyer pays listing.price in ₹        (sell mode, accepts_money=1)
      "cloth_swap" – buyer offers a cloth                  (swap mode, swap_type=cloth)
      "points_swap"– buyer pays listing.points_value       (swap mode, swap_type=points)
    """
    db = get_session()
    try:
        existing = db.query(Match).filter_by(
            listing_id=listing_id, buyer_id=buyer_id
        ).first()
        if existing:
            return None, "You already sent a request for this listing"

        listing = db.query(Listing).get(listing_id)
        if not listing:
            return None, "Listing not found"

        # ── Points balance check ───────────────────────────────────
        if payment_type in ("points", "points_swap"):
            buyer = db.query(User).get(buyer_id)
            if not buyer:
                return None, "Buyer account not found"
            needed = listing.points_value or 0
            have   = buyer.points_balance or 0
            if have < needed:
                return None, (
                    f"Not enough points!  "
                    f"You have {have:.0f} pts but need {needed:.0f} pts."
                )

        # Fee only applies to money transactions
        fee = (
            round((listing.price or 0) * 0.05, 2)
            if payment_type == "money"
            else 0.0
        )

        match = Match(
            listing_id=listing_id,
            buyer_id=buyer_id,
            status="pending",
            payment_type=payment_type,
            swap_offer=swap_offer,
            fee_on_match=fee,
            fee_on_complete=fee,
        )
        db.add(match)
        db.commit()
        db.refresh(match)
        return match, "Match request sent! 💌"
    except Exception as e:
        db.rollback()
        return None, str(e)


def get_matches_for_seller(seller_user_id):
    db = get_session()
    matches = (
        db.query(Match)
        .join(Listing, Match.listing_id == Listing.id)
        .filter(Listing.seller_id == seller_user_id)
        .all()
    )
    for m in matches:
        db.expunge(m)
    return matches


def get_matches_for_buyer(buyer_id):
    db = get_session()
    matches = db.query(Match).filter_by(buyer_id=buyer_id).all()
    for m in matches:
        db.expunge(m)
    return matches


def accept_match(match_id):
    db = get_session()
    try:
        match = db.query(Match).get(match_id)
        if match:
            match.status = "accepted"
            listing = db.query(Listing).get(match.listing_id)
            if listing:
                listing.status = "matched"
            db.commit()
    except Exception:
        db.rollback()


def complete_transaction(match_id):
    """
    Mark the transaction complete and transfer points.

    Points flow
    -----------
      money       → seller earns  listing.points_value  (reward for selling)
      points      → buyer  loses  listing.points_value
                    seller earns  listing.points_value
      cloth_swap  → seller earns  listing.points_value  (reward for giving away item)
      points_swap → buyer  loses  listing.points_value
                    seller earns  listing.points_value
    """
    db = get_session()
    try:
        match = db.query(Match).get(match_id)
        if not match:
            return

        listing = db.query(Listing).get(match.listing_id)
        seller  = db.query(User).get(listing.seller_id) if listing else None
        buyer   = db.query(User).get(match.buyer_id)

        match.status = "completed"
        if listing:
            listing.status = "sold"

        # ── Points transfer ────────────────────────────────────────
        if listing and seller and buyer:
            pts = listing.points_value or 0
            pt  = match.payment_type  or "money"

            if pt == "money":
                # Seller earns points as a reward for the sale
                seller.points_balance = (seller.points_balance or 0) + pts

            elif pt in ("points", "points_swap"):
                buyer.points_balance  = (buyer.points_balance  or 0) - pts
                seller.points_balance = (seller.points_balance or 0) + pts

            elif pt == "cloth_swap":
                # Seller earns points for giving away their item
                seller.points_balance = (seller.points_balance or 0) + pts

        db.commit()
    except Exception as e:
        db.rollback()
        raise e