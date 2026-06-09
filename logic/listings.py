from sqlalchemy.orm import joinedload
from database.db_example import get_session
from database.models import Listing
from logic.points import calculate_points


def create_listing(seller_id, mode, title, category, size, material, condition,
                   og_price, wear_label, brand_tier,
                   accepts_money, price, swap_type, swap_condition, image_path):
    db = get_session()
    try:
        points_value = calculate_points(og_price, condition, wear_label, brand_tier)

        listing = Listing(
            seller_id=seller_id,
            mode=mode,
            title=title,
            category=category,
            size=size,
            material=material,
            condition=condition,
            og_price=float(og_price) if og_price else 0.0,
            wear_label=wear_label,
            brand_tier=brand_tier,
            points_value=points_value,
            accepts_money=1 if accepts_money else 0,
            price=float(price) if price else 0.0,
            swap_type=swap_type,
            swap_condition=swap_condition,
            image_path=image_path,
        )
        db.add(listing)
        db.commit()
        db.refresh(listing)
        return listing
    except Exception as e:
        db.rollback()
        raise e


def browse_listings(mode=None, size=None, category=None, exclude_user_id=None):
    db = get_session()
    query = (
        db.query(Listing)
        .options(joinedload(Listing.seller))
        .filter(Listing.status == "active")
    )
    if mode:
        query = query.filter(Listing.mode == mode)
    if size:
        query = query.filter(Listing.size == size)
    if category:
        query = query.filter(Listing.category == category)
    if exclude_user_id:
        query = query.filter(Listing.seller_id != exclude_user_id)
    results = query.order_by(Listing.created_at.desc()).all()
    for listing in results:
        db.expunge(listing)
    return results


def get_my_listings(user_id):
    db = get_session()
    results = (
        db.query(Listing)
        .options(joinedload(Listing.seller))
        .filter_by(seller_id=user_id)
        .order_by(Listing.created_at.desc())
        .all()
    )
    for listing in results:
        db.expunge(listing)
    return results


def delete_listing(listing_id, user_id):
    db = get_session()
    try:
        listing = db.query(Listing).filter_by(id=listing_id, seller_id=user_id).first()
        if listing:
            db.delete(listing)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False

def update_listing(listing_id, user_id, **fields):
    """Update editable fields on an owned listing."""
    from logic.points import calculate_points
    db = get_session()
    try:
        listing = db.query(Listing).filter_by(
            id=listing_id, seller_id=user_id).first()
        if not listing:
            return False, "Listing not found"
        for key, val in fields.items():
            if hasattr(listing, key):
                setattr(listing, key, val)
        # Recompute points if price/condition/wear/brand changed
        listing.points_value = calculate_points(
            listing.og_price or 0,
            listing.condition or "Good",
            listing.wear_label or "Few times",
            listing.brand_tier or "No brand / Local",
        )
        db.commit()
        return True, "Listing updated!"
    except Exception as e:
        db.rollback()
        return False, str(e)


def toggle_wishlist(user_id, listing_id):
    """Add to wishlist if not saved, remove if already saved. Returns (is_saved, msg)."""
    from database.models import Wishlist
    db = get_session()
    try:
        existing = db.query(Wishlist).filter_by(
            user_id=user_id, listing_id=listing_id).first()
        if existing:
            db.delete(existing)
            db.commit()
            return False, "Removed from wishlist"
        db.add(Wishlist(user_id=user_id, listing_id=listing_id))
        db.commit()
        return True, "Saved to wishlist ❤"
    except Exception as e:
        db.rollback()
        return False, str(e)


def get_wishlist(user_id):
    """Return all listings saved by a user."""
    from database.models import Wishlist
    from sqlalchemy.orm import joinedload
    db = get_session()
    entries = db.query(Wishlist).filter_by(user_id=user_id).all()
    listing_ids = [e.listing_id for e in entries]
    results = (
        db.query(Listing)
        .options(joinedload(Listing.seller))
        .filter(Listing.id.in_(listing_ids))
        .all()
    ) if listing_ids else []
    for l in results:
        db.expunge(l)
    return results


def is_in_wishlist(user_id, listing_id):
    from database.models import Wishlist
    db = get_session()
    return db.query(Wishlist).filter_by(
        user_id=user_id, listing_id=listing_id).first() is not None


def get_user_stats(user_id):
    """Return dict of stats for the profile page."""
    from database.models import Match, User as UserModel
    db = get_session()
    total_listings  = db.query(Listing).filter_by(seller_id=user_id).count()
    active_listings = db.query(Listing).filter_by(
        seller_id=user_id, status="active").count()
    sold_listings   = db.query(Listing).filter_by(
        seller_id=user_id, status="sold").count()
    matches_completed = (
        db.query(Match)
        .join(Listing, Match.listing_id == Listing.id)
        .filter(Listing.seller_id == user_id, Match.status == "completed")
        .count()
    )
    buys_completed = db.query(Match).filter_by(
        buyer_id=user_id, status="completed").count()
    user = db.query(UserModel).get(user_id)
    points = (user.points_balance or 0) if user else 0
    return {
        "total_listings":    total_listings,
        "active_listings":   active_listings,
        "sold_listings":     sold_listings,
        "matches_completed": matches_completed,
        "buys_completed":    buys_completed,
        "points":            points,
    }