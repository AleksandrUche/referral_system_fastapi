from datetime import timedelta

from alembic.util import status
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.user.models import UserOrm
from app.user.schemas import UserDTO, UserCreateDTO, Token
from app.user.services.jwt_service import create_access_token
from app.user.services.security import get_current_user
from app.user.services.service import get_user_by_email, create_user, authenticate_user
from core.settings import ACCESS_TOKEN_EXPIRE_MINUTES
from app.referral.service import get_referral_code

router = APIRouter()


@router.post('/register', response_model=UserDTO)
async def register_user(
    user_in: UserCreateDTO,
    session: AsyncSession = Depends(get_session),
):
    """Создание нового пользователя."""
    check_user = await get_user_by_email(session, email=user_in.email)
    if check_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Пользователь с таким email уже существует в системе.',
        )

    if user_in.code:
        code = await get_referral_code(user_in.code, session)
        return await create_user(user_in, session, code)

    return await create_user(user_in, session)



@router.post('/login', response_model=Token)
async def login_access_token(
    session: AsyncSession = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Войти в систему и получить токен доступа для будущих запросов."""
    user = await authenticate_user(
        session, email=form_data.username, password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail='Неверный пароль'
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        'access_token': create_access_token(
            data={'user_id': user.id}, expires_delta=access_token_expires
        ),
        'token_type': 'bearer',
    }


@router.get('/profile', response_model=UserDTO)
def read_user_me(
    current_user: UserOrm = Depends(get_current_user),
):
    """Получить текущего пользователя."""
    return current_user
