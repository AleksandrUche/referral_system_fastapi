from datetime import timedelta, datetime

from pydantic import BaseModel


class ReferralCodeDTO(BaseModel):
    code: str


class ReferralCodeRequestDTO(ReferralCodeDTO):
    expires_date: timedelta


class ReferralCodeResponseDTO(ReferralCodeDTO):
    expires_date: datetime
