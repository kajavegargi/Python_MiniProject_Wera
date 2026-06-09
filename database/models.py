from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

# ──────────────────────────────────────────────────────────────────────────────
# NOTE: If you already have an existing database, drop and recreate it so
# the new columns are picked up:
#   DROP DATABASE wera_db; CREATE DATABASE wera_db;
# Then restart the app — init_db() will recreate all tables.
# ──────────────────────────────────────────────────────────────────────────────


class User(Base):
    __tablename__ = "users"

    id                 = Column(Integer, primary_key=True)
    name               = Column(String(100), nullable=False)
    email              = Column(String(150), unique=True, nullable=False)
    password_hash      = Column(String(255), nullable=False)
    college_or_company = Column(String(150))
    city               = Column(String(50))
    points_balance     = Column(Float, default=500.0)   # 500 welcome points
    created_at         = Column(DateTime, default=datetime.utcnow)

    listings = relationship("Listing", back_populates="seller")


class Listing(Base):
    __tablename__ = "listings"

    id           = Column(Integer, primary_key=True)
    seller_id    = Column(Integer, ForeignKey("users.id"))
    mode         = Column(Enum("sell", "swap"), nullable=False)
    title        = Column(String(200), nullable=False)
    category     = Column(String(50))
    size         = Column(String(10))
    material     = Column(String(100))
    condition    = Column(String(50))

    # ── Points calculation inputs ──────────────────────────────
    og_price     = Column(Float,  default=0.0)                     # original / retail price
    wear_label   = Column(String(50),  default="Few times")        # how often worn
    brand_tier   = Column(String(100), default="No brand / Local") # brand bucket
    points_value = Column(Float,  default=0.0)                     # pre-computed result

    # ── Sell-mode extras ───────────────────────────────────────
    accepts_money = Column(Integer, default=0)   # 1 = yes, 0 = no
    price         = Column(Float,   default=0.0) # ₹ price shown when accepts_money=1

    # ── Swap-mode extras ───────────────────────────────────────
    swap_type      = Column(String(20),  default="cloth")  # "cloth" | "points"
    swap_condition = Column(String(300))                   # what cloth the seller wants

    # ──────────────────────────────────────────────────────────
    image_path = Column(String(2000))
    status     = Column(String(30), default="active")
    created_at = Column(DateTime,   default=datetime.utcnow)

    seller = relationship("User", back_populates="listings")


class Match(Base):
    __tablename__ = "matches"

    id           = Column(Integer, primary_key=True)
    listing_id   = Column(Integer, ForeignKey("listings.id"))
    buyer_id     = Column(Integer, ForeignKey("users.id"))
    status       = Column(String(30), default="pending")

    # payment_type: "money" | "points" | "cloth_swap" | "points_swap"
    payment_type = Column(String(30), default="points")
    swap_offer   = Column(String(500))   # buyer's cloth description (cloth_swap only)

    fee_on_match    = Column(Float, default=0.0)
    fee_on_complete = Column(Float, default=0.0)
    created_at      = Column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id        = Column(Integer, primary_key=True)
    match_id  = Column(Integer, ForeignKey("matches.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content   = Column(String(1000), nullable=False)
    sent_at   = Column(DateTime, default=datetime.utcnow)

class Wishlist(Base):
    __tablename__ = "wishlists"

    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    listing_id = Column(Integer, ForeignKey("listings.id"))
    saved_at   = Column(DateTime, default=datetime.utcnow)


class Review(Base):
    __tablename__ = "reviews"

    id          = Column(Integer, primary_key=True)
    match_id    = Column(Integer, ForeignKey("matches.id"), unique=True)
    reviewer_id = Column(Integer, ForeignKey("users.id"))   # buyer
    seller_id   = Column(Integer, ForeignKey("users.id"))   # seller being rated
    rating      = Column(Integer, nullable=False)            # 1–5
    comment     = Column(String(500), default="")
    created_at  = Column(DateTime, default=datetime.utcnow)



class Follow(Base):
   
    __tablename__ = "follows"
    __table_args__ = (
        UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )

    id           = Column(Integer, primary_key=True)
    follower_id  = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    following_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                          nullable=False)
    created_at   = Column(DateTime, default=datetime.utcnow)

    follower  = relationship("User", foreign_keys=[follower_id],
                             backref="following_list")
    following = relationship("User", foreign_keys=[following_id],
                             backref="followers_list")

    def __repr__(self):
        return f"<Follow {self.follower_id} → {self.following_id}>"

class Block(Base):
    """
    A blocking relationship between two users.
    blocker_id → the user who blocked
    blocked_id → the user who was blocked

    Effect: blocked user's listings and profile are hidden from blocker,
    and blocker's listings/messages are hidden from blocked user.
    """
    __tablename__ = "blocks"
    __table_args__ = (
        UniqueConstraint("blocker_id", "blocked_id", name="uq_block"),
    )

    id         = Column(Integer, primary_key=True)
    blocker_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    blocked_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                        nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    blocker = relationship("User", foreign_keys=[blocker_id],
                           backref="blocked_list")
    blocked = relationship("User", foreign_keys=[blocked_id],
                           backref="blocked_by_list")

    def __repr__(self):
        return f"<Block {self.blocker_id} blocked {self.blocked_id}>"


REPORT_REASONS = [
    "Spam or scam",
    "Inappropriate content",
    "Fake account",
    "Harassment",
    "Counterfeit item",
    "Other",
]

class Report(Base):
    """
    A report submitted by one user about another user.
    status: 'pending' | 'reviewed' | 'resolved'
    """
    __tablename__ = "reports"

    id          = Column(Integer, primary_key=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False)
    reported_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"),
                         nullable=False)
    reason      = Column(String(100), nullable=False)
    details     = Column(String(500), nullable=True)
    status      = Column(String(20), default="pending")   # pending/reviewed/resolved
    created_at  = Column(DateTime, default=datetime.utcnow)

    reporter = relationship("User", foreign_keys=[reporter_id],
                            backref="reports_made")
    reported = relationship("User", foreign_keys=[reported_id],
                            backref="reports_received")

    def __repr__(self):
        return f"<Report by={self.reporter_id} about={self.reported_id} reason={self.reason!r}>"



    