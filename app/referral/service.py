from datetime import datetime, timezone
from typing import Optional, List

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.referral.models import ReferralCodeOrm, ReferralOrm
from app.referral.schemas import ReferralCodeRequestDTO
from app.user.models import UserOrm
from app.user.schemas import UserDTO


async def get_referral_code_by_user_id(
    current_user: UserDTO, session: AsyncSession,
) -> Optional[ReferralCodeOrm]:
    return await session.scalar(
        select(ReferralCodeOrm).filter(ReferralCodeOrm.user_id == current_user.id)
    )


async def get_referral_code_by_email(
    referrer_email, session: AsyncSession,
) -> ReferralCodeOrm | HTTPException:
    """Возвращает реферальный код по email рефера"""
    referral_code = await session.scalar(
        select(UserOrm).options(joinedload(UserOrm.referral_code)).filter(
            UserOrm.email == referrer_email
        )
    )
    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Реферального кода по данному email нет"
        )
    return referral_code.referral_code


async def get_user_referral_code(
    current_user: UserDTO, session: AsyncSession,
) -> ReferralCodeOrm | HTTPException:
    """Возвращает реферальный код текущего пользователя"""
    referral_code = await get_referral_code_by_user_id(current_user, session)
    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У пользователя нет реферального кода."
        )
    return referral_code


async def add_referral_code(
    request_data: ReferralCodeRequestDTO, current_user: UserDTO, session: AsyncSession,
) -> ReferralCodeOrm | HTTPException:
    """
    Проверяет, есть ли у пользователя код. Если нет, создает новый реферальный код.
    """
    current_date = datetime.now().replace(tzinfo=timezone.utc)

    existing_code = await get_referral_code_by_user_id(current_user, session)
    if existing_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="У пользователя уже есть активный реферальный код."
        )

    db_item = ReferralCodeOrm(
        code=request_data.code,
        expires_date=current_date + request_data.expires_date,
        user_id=current_user.id
    )
    session.add(db_item)
    await session.commit()

    await session.refresh(db_item)
    return db_item


async def remove_referral_code(
    current_user: UserDTO, session: AsyncSession
) -> None:
    """Удаляет промокод текущего пользователя"""
    stmt = delete(ReferralCodeOrm).filter(ReferralCodeOrm.user_id == current_user.id)
    res = await session.execute(stmt)

    if res.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У пользователя еще нет промокодов."
        )

    await session.commit()


async def get_referral_code(
    referral_code: str, session: AsyncSession
) -> ReferralCodeOrm | HTTPException:
    """Возвращает объект кода по его названию"""
    referral_code = await session.scalar(
        select(ReferralCodeOrm).filter(ReferralCodeOrm.code == referral_code)
    )
    if not referral_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Код не найден'
        )

    current_date = datetime.now().replace(tzinfo=timezone.utc)
    if current_date > referral_code.expires_date:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='Срок действия кода истек'
        )
    return referral_code


async def add_referral_user(
    referral_code: ReferralCodeOrm, new_user: UserOrm, session: AsyncSession
) -> ReferralOrm | HTTPException:
    """Добавляет реферала"""
    referral = ReferralOrm(
        referrer_id=referral_code.user_id,
        referral_code=referral_code.id,
        referral_user_id=new_user.id,
    )
    session.add(referral)
    await session.commit()

    await session.refresh(referral)
    return referral


async def get_information_referrals_by_referrer(
    current_user: UserDTO, session: AsyncSession,
) -> List[UserDTO] | HTTPException:
    """Получить рефералов по id реферера"""
    referrals = await session.scalars(
        select(ReferralOrm)
        .options(selectinload(ReferralOrm.referral))
        .filter(ReferralOrm.referrer_id == current_user.id)
    )

    if not referrals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="У данного пользователя нет рефералов"
        )

    referral_names = \
        [UserDTO(id=elem.referral.id, name=elem.referral.name) for elem in referrals.all()]

    return referral_names
