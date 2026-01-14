"""Простой тест для проверки валидации без сложных зависимостей"""
import sys
import os

# Добавляем корень проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pydantic import ValidationError
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_user_model():
    """Создаём модель прямо в тесте для изоляции от других ошибок"""
    from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, ConfigDict
    from typing import List, Optional
    import re

    class Roles(str):
        USER = "USER"
        ADMIN = "ADMIN"

    class TestUserModel(BaseModel):
        """Упрощённая модель для тестирования"""
        model_config = ConfigDict(str_strip_whitespace=True)

        email: EmailStr
        fullName: str = Field(..., min_length=1, max_length=100)
        password: str = Field(..., min_length=8, max_length=50)
        passwordRepeat: str = Field(..., min_length=8, max_length=50)
        roles: List[str] = Field(default_factory=lambda: ["USER"])

        @field_validator('email')
        @classmethod
        def email_must_contain_at(cls, v: str) -> str:
            if '@' not in v:
                raise ValueError('Email must contain "@" symbol')
            return v.lower()

        @field_validator('password')
        @classmethod
        def password_length(cls, v: str) -> str:
            if len(v) < 8:
                raise ValueError('Password must be at least 8 characters long')
            return v

        @model_validator(mode='after')
        def validate_passwords_match(self):
            if self.password != self.passwordRepeat:
                raise ValueError('Passwords do not match')
            return self

    return TestUserModel

def test_basic_validation():
    """Базовый тест валидации"""
    print("\n=== Базовый тест валидации ===")

    TestUserModel = create_user_model()

    # Успешный случай
    valid_data = {
        "email": "test@example.com",
        "fullName": "John Doe",
        "password": "Password123",
        "passwordRepeat": "Password123",
        "roles": ["USER"]
    }

    user = TestUserModel(**valid_data)
    print(f"Успех: {user.email}, {user.fullName}")

    # Ошибка: email без @
    invalid_data = valid_data.copy()
    invalid_data["email"] = "invalid-email"

    try:
        TestUserModel(**invalid_data)
        print("Ошибка: Должна была быть ValidationError")
        return False
    except ValidationError as e:
        errors = [err["msg"] for err in e.errors()]
        print(f"Правильно отловили ошибку: {errors[0]}")

    # Ошибка: короткий пароль
    invalid_data = valid_data.copy()
    invalid_data["password"] = "short"
    invalid_data["passwordRepeat"] = "short"

    try:
        TestUserModel(**invalid_data)
        print("Ошибка: Должна была быть ValidationError")
        return False
    except ValidationError as e:
        errors = [err["msg"] for err in e.errors()]
        print(f"Правильно отловили ошибку: {errors[0]}")

    # Ошибка: пароли не совпадают
    invalid_data = valid_data.copy()
    invalid_data["passwordRepeat"] = "Different123"

    try:
        TestUserModel(**invalid_data)
        print("Ошибка: Должна была быть ValidationError")
        return False
    except ValidationError as e:
        errors = [err["msg"] for err in e.errors()]
        print(f"Правильно отловили ошибку: {errors[0]}")

    return True


def main():
    """Основная функция запуска тестов"""
    print("Запуск простого теста валидации")
    print("=" * 50)

    try:
        success = test_basic_validation()

        print("\n" + "=" * 50)
        if success:
            print("Все тесты пройдены успешно!")
        else:
            print("Есть проблемы с тестами")

    except Exception as e:
        print(f"\nКритическая ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()