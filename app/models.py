from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from app.database import Base


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True)

    # --- Feature 1: Submit a claim ---
    text = Column(Text, nullable=False)
    source_platform = Column(String(20), nullable=False)   # WhatsApp / X / Instagram / Other
    category = Column(String(20), nullable=False)          # Politics / Health / Finance / Other
    source_link = Column(String(500), nullable=True)        # optional — absence triggers "Unsourced" flag

    # --- Feature 2: Risk flags (computed, stored so feed/detail don't recompute every read) ---
    flags = Column(JSON, default=list)          # e.g. ["Sensational", "Unsourced"]
    risk_level = Column(String(20), default="Normal")  # "High Risk" or "Normal"

    # --- Feature 3: Review workflow ---
    status = Column(String(20), default="Unverified")  # Unverified / Verified True / Verified False / Misleading
    reviewer_note = Column(Text, nullable=True)

    # --- Timestamps (feed ordering + detail view) ---
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
