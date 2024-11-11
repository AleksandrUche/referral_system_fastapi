import jwt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import PyJWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_session
from app.user.schemas import TokenPayload
from app.user.services.jwt_service import ALGORITHM
from app.user.services.service import get_user_by_id
from core.settings import SECRET_KEY

reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Security(reusable_oauth2)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        token_data = TokenPayload(**payload)
    except PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не удалось подтвердить учетные данные"
        )
    user = await get_user_by_id(session, id=token_data.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user
