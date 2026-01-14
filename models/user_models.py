from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
from typing import List, Optional, Dict, Any
from enum import Enum
from constants.roles import Roles
import logging
import datetime
import re

logger = logging.getLogger(__name__)


class RegistrationUserData(BaseModel):
    """Модель данных для регистрации пользователя с расширенной валидацией"""

    model_config = ConfigDict(str_strip_whitespace=True)

    email: EmailStr
    fullName: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=50)
    passwordRepeat: str = Field(..., min_length=8, max_length=50)
    roles: List[Roles] = Field(default_factory=lambda: [Roles.USER])
    verified: Optional[bool] = False
    banned: Optional[bool] = False

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        """Проверка наличия @ в email"""
        if '@' not in v:
            raise ValueError('Email must contain "@" symbol')
        return v.lower()

    @field_validator('email')
    @classmethod
    def email_must_be_valid(cls, v: str) -> str:
        """Строгая проверка формата email"""
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, v):
            raise ValueError('Invalid email format')
        return v

    @field_validator('password')
    @classmethod
    def password_length(cls, v: str) -> str:
        """Проверка минимальной длины пароля"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """Проверка сложности пароля"""
        if v.isdigit():
            raise ValueError('Password cannot consist only of digits')
        if v.isalpha():
            raise ValueError('Password must contain both letters and numbers/symbols')
        if v.islower():
            raise ValueError('Password should contain at least one uppercase letter')
        return v

    @field_validator('passwordRepeat')
    @classmethod
    def validate_password_repeat(cls, v: str) -> str:
        """Базовая валидация повторного пароля"""
        # Здесь только базовая проверка, сравнение сделаем в model_validator
        return v

    @model_validator(mode='after')
    def validate_passwords_match(self):
        """Проверка совпадения паролей - используем model_validator вместо field_validator"""
        if self.password != self.passwordRepeat:
            raise ValueError('Passwords do not match')
        return self

    @field_validator('roles')
    @classmethod
    def validate_roles(cls, v: List[Roles]) -> List[Roles]:
        """Проверка списка ролей"""
        if not v:
            raise ValueError('Roles list cannot be empty')
        return v

    def log_user_data(self):
        """Логирование данных пользователя (без пароля)"""
        logger.info(f"User registration data: "
                    f"email={self.email}, "
                    f"fullName={self.fullName}, "
                    f"roles={[role.value for role in self.roles]}, "
                    f"verified={self.verified}, "
                    f"banned={self.banned}")

    def to_registration_dict(self):
        """Преобразует модель в словарь для регистрации через auth API."""
        data = self.model_dump()
        # Преобразуем Enum в строки
        data['roles'] = [role.value for role in self.roles]
        return data

    def to_create_dict(self):
        """Преобразует модель в словарь для создания через user API."""
        data = self.model_dump()
        # Преобразуем Enum в строки
        data['roles'] = [role.value for role in self.roles]
        # Удаляем passwordRepeat
        if 'passwordRepeat' in data:
            data.pop('passwordRepeat')
        # Добавляем обязательные поля для создания
        data['verified'] = True
        data['banned'] = False
        return data


class UserInLoginResponse(BaseModel):
    """Модель пользователя в ответе на логин"""
    model_config = ConfigDict(
        json_encoders={
            Roles: lambda v: v.value
        }
    )

    id: str
    email: EmailStr
    fullName: str
    roles: List[Roles]

    @field_validator("roles", mode="before")
    @classmethod
    def validate_roles_before(cls, value: Any) -> List[Roles]:
        """Преобразует строки в Enum Roles перед валидацией."""
        if isinstance(value, list):
            result = []
            for role in value:
                if isinstance(role, str):
                    # Преобразуем строку в Enum
                    result.append(Roles(role))
                elif isinstance(role, Roles):
                    result.append(role)
                else:
                    raise ValueError(f"Invalid role type: {type(role)}")
            return result
        return value


class RegisterUserResponse(BaseModel):
    """Модель ответа после регистрации пользователя"""
    model_config = ConfigDict(
        json_encoders={
            Roles: lambda v: v.value
        }
    )

    id: str
    email: EmailStr
    fullName: str
    verified: bool
    banned: Optional[bool] = False
    roles: List[Roles]
    createdAt: str

    @field_validator("roles", mode="before")
    @classmethod
    def validate_roles_before(cls, value: Any) -> List[Roles]:
        """Преобразует строки в Enum Roles перед валидацией."""
        if isinstance(value, list):
            result = []
            for role in value:
                if isinstance(role, str):
                    # Преобразуем строку в Enum
                    result.append(Roles(role))
                elif isinstance(role, Roles):
                    result.append(role)
                else:
                    raise ValueError(f"Invalid role type: {type(role)}")
            return result
        return value

    @field_validator("createdAt")
    @classmethod
    def validate_created_at(cls, value: str) -> str:
        """Валидация формата даты"""
        try:
            datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Некорректный формат даты и времени. Ожидается ISO 8601.")
        return value

    def log_response(self):
        """Логирование ответа"""
        logger.info(f"User registered successfully: "
                    f"id={self.id}, "
                    f"email={self.email}, "
                    f"roles={[role.value for role in self.roles]}")


class LoginRequest(BaseModel):
    """Модель запроса для логина"""
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator('password')
    @classmethod
    def password_not_empty(cls, v: str) -> str:
        """Проверка, что пароль не пустой"""
        if not v or v.strip() == '':
            raise ValueError('Password cannot be empty')
        return v


class LoginResponse(BaseModel):
    """Модель ответа после логина"""
    accessToken: str
    refreshToken: str
    expiresIn: int
    user: UserInLoginResponse  # Используем новую модель вместо RegisterUserResponse

    def log_response(self):
        """Логирование ответа логина (без токена для безопасности)"""
        logger.info(f"User logged in successfully: email={self.user.email}")


class UserCreateRequest(BaseModel):
    """Модель для создания пользователя через API администратора"""
    model_config = ConfigDict(
        json_encoders={
            Roles: lambda v: v.value
        }
    )

    email: EmailStr
    fullName: str = Field(..., min_length=1, max_length=100)
    password: str = Field(..., min_length=8, max_length=50)
    roles: List[Roles] = Field(default_factory=lambda: [Roles.USER])
    verified: bool = True
    banned: bool = False

    @field_validator('email')
    @classmethod
    def email_must_contain_at(cls, v: str) -> str:
        if '@' not in v:
            raise ValueError('Email must contain "@" symbol')
        return v.lower()

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if v.isdigit():
            raise ValueError('Password cannot consist only of digits')
        return v

    def to_api_dict(self) -> Dict[str, Any]:
        """Преобразует модель в словарь для API с сериализацией Enum."""
        data = self.model_dump()
        # Преобразуем Enum Roles в строки
        data['roles'] = [role.value for role in self.roles]
        return data
