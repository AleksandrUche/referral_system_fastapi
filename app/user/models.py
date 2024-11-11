from __future__ import annotations

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserOrm(Base):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)
    email: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(nullable=False)

    referral_code = relationship(
        'ReferralCodeOrm', back_populates='user', uselist=False
    )
    referrals = relationship(
        'ReferralOrm', back_populates='referral', foreign_keys='ReferralOrm.referral_user_id', cascade="all, delete"
    )
