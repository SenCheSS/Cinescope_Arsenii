from typing import Optional, List
import datetime
import re
from typing import List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from constants.roles import Roles


class TestUser(BaseModel):
    """Модель для тестового пользователя"""
    model_config = ConfigDict(
        json_encoders={
            Roles: lambda v: v.value  # Преобразуем Enum в строку
        },
        str_strip_whitespace=True
    )

    email: str = Field(..., pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    fullName: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=50)
    passwordRepeat: str = Field(..., min_length=8, max_length=50)
    roles: List[Roles] = Field(default_factory=lambda: [Roles.USER])
    verified: Optional[bool] = None
    banned: Optional[bool] = None

    @field_validator("passwordRepeat")
    @classmethod
    def check_password_repeat(cls, value: str, info) -> str:
        """Проверяем, совпадение паролей"""
        if "password" in info.data and value != info.data["password"]:
            raise ValueError("Пароли не совпадают")
        return value

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Проверка сложности пароля"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if v.isdigit():
            raise ValueError('Password cannot consist only of digits')
        if v.isalpha():
            raise ValueError('Password must contain both letters and numbers/symbols')
        if v.islower():
            raise ValueError('Password should contain at least one uppercase letter')
        return v

class RegisterUserResponse(BaseModel):
    """Модель ответа при регистрации пользователя"""
    model_config = ConfigDict(
        json_encoders={
            Roles: lambda v: v.value
        }
    )

    id: str
    email: str = Field(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
    fullName: str = Field(min_length=1, max_length=100)
    verified: bool
    banned: bool
    roles: List[Roles]
    createdAt: str

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидация формата даты"""
        try:
            datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается ISO 8601.")
        return value
