from typing import Optional

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.referral.models import ReferralCodeOrm, ReferralOrm
from app.user.models import UserOrm
from app.user.schemas import UserCreateDTO

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_user_by_email(session: AsyncSession, email: str) -> Optional[UserOrm]:
    stmt = select(UserOrm).filter(UserOrm.email == email)
    res = await session.execute(stmt)
    return res.scalar()


async def get_user_by_id(session: AsyncSession, id: int) -> Optional[UserOrm]:
    stmt = select(UserOrm).filter(UserOrm.id == id)
    res = await session.execute(stmt)
    return res.scalar()


async def create_user(
    user: UserCreateDTO,
    session: AsyncSession,
    referral_code: Optional[ReferralCodeOrm] = None,
) -> UserOrm:

    new_user = UserOrm(
        name=user.name,
        email=user.email,
        hashed_password=get_password_hash(user.password),
    )
    session.add(new_user)
    await session.flush()

    if referral_code:
        referral = ReferralOrm(
            referrer_id=referral_code.user_id,
            referral_code_id=referral_code.id,
            referral_user_id=new_user.id,
        )
        session.add(referral)

    try:
        await session.commit()

    except SQLAlchemyError as error:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ошибка при регистрации: {error}"
        )
    await session.refresh(new_user)

    return new_user


async def authenticate_user(
    session: AsyncSession, email: str, password: str,
) -> Optional[UserOrm]:
    user = await get_user_by_email(session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
