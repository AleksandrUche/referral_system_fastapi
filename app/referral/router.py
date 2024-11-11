from fastapi import APIRouter, Depends, status
from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.dependencies import get_session
from app.referral import service
from app.referral.schemas import (
    ReferralCodeDTO,
    ReferralCodeRequestDTO,
    ReferralCodeResponseDTO,
)
from app.user.schemas import UserDTO
from app.user.services.security import get_current_user

router = APIRouter()


@router.post(
    '/code',
    status_code=status.HTTP_201_CREATED,
    response_model=ReferralCodeResponseDTO,
    summary='Добавление промокода',
    description='Создает промокод у текущего пользователя, формат ввода даты использует'
                ' timedelta: P[DD]D + если есть время то добавить T[HH]H[MM]M[SS]S'
)
async def add_referral_code(
    request: ReferralCodeRequestDTO,
    current_user: UserDTO = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.add_referral_code(request, current_user, session)


@router.get(
    '/code',
    status_code=status.HTTP_200_OK,
    response_model=ReferralCodeResponseDTO,
    summary='Получение промокода текущего пользователя',
)
async def get_referral_code(
    current_user: UserDTO = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_user_referral_code(current_user, session)


@router.delete(
    '/code',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удаление промокода у текущего пользователя',
    description='Удаляет промокод у текущего пользователя'
)
async def remove_referral_code(
    current_user: UserDTO = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await service.remove_referral_code(current_user, session)


@router.get(
    '/code-search',
    status_code=status.HTTP_200_OK,
    response_model=ReferralCodeDTO,
    summary='Получение реферального кода по email рефера',
)
async def get_referral_code_by_email(
    referrer_email: EmailStr,
    session: AsyncSession = Depends(get_session),
):
    return await service.get_referral_code_by_email(referrer_email, session)


@router.get(
    '/my-referrals',
    status_code=status.HTTP_200_OK,
    response_model= List[UserDTO],
    summary='Получить рефералов текущего пользователя',
)
async def get_my_referral(
    current_user: UserDTO = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_information_referrals_by_referrer(current_user, session)
