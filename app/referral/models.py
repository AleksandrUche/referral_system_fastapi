from __future__ import annotations

from sqlalchemy import ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ReferralCodeOrm(Base):
    __tablename__ = 'referral_code'
    id: Mapped[int] = mapped_column(primary_key=True)

    code: Mapped[str] = mapped_column('Код', unique=True, index=True)
    created_date = mapped_column(
        'Дата создания', DateTime(timezone=True), server_default=func.now()
    )
    updated_date = mapped_column(
        'Дата обновления', DateTime(timezone=True), server_default=func.now(),
        onupdate=func.now()
    )
    expires_date = mapped_column(
        'Дата окончания', DateTime(timezone=True), nullable=False
    )
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'), unique=True,
                                         nullable=False)

    user = relationship('UserOrm', back_populates='referral_code', uselist=False)
    referrals = relationship('ReferralOrm', back_populates='referral_code')


class ReferralOrm(Base):
    __tablename__ = 'referral'
    id: Mapped[int] = mapped_column(primary_key=True)

    referrer_id: Mapped[int] = mapped_column(
        'Привлекающий пользователь', ForeignKey('user.id')
    )
    referral_user_id: Mapped[int] = mapped_column(
        'Участник программы', ForeignKey('user.id')
    )
    referral_code_id: Mapped[int] = mapped_column('Код', ForeignKey('referral_code.id'))

    referral_code = relationship('ReferralCodeOrm', back_populates='referrals')
    referral = relationship(
        'UserOrm', foreign_keys=[referral_user_id], back_populates='referrals'
    )
