import pytest
from api.api_manager import ApiManager
from constants.roles import Roles
from models.user_models import (RegisterUserResponse, RegistrationUserData,
                                LoginResponse, LoginRequest, UserCreateRequest)


class TestAuthApi:
    def test_register_user(self, api_manager: ApiManager,
                           registration_user_data: RegistrationUserData):
        # Преобразуем в словарь
        user_data_dict = registration_user_data.model_dump()
        # Преобразуем Roles enum в строки
        if 'roles' in user_data_dict:
            user_data_dict['roles'] = [role.value for role in registration_user_data.roles]
        # Регистрируем пользователя
        response = api_manager.auth_api.register_user(
            user_data=user_data_dict,
            expected_status=201
        )
        # Валидируем ответ
        register_response = RegisterUserResponse(**response.json())

        assert register_response.email == registration_user_data.email
        assert register_response.fullName == registration_user_data.fullName
        assert register_response.roles == registration_user_data.roles
        # Проверяем, что ID не пустой
        assert isinstance(register_response.id, str) and len(register_response.id) > 0
        # Проверяем verified
        assert register_response.verified is True
        assert register_response.banned is False

    def test_register_and_login_user(self, api_manager: ApiManager,
                                     registered_user: RegistrationUserData):
        """Тест на регистрацию и авторизацию пользователя."""
        login_request = LoginRequest(
            email=registered_user.email,
            password=registered_user.password
        )
        login_data = login_request.model_dump()
        response = api_manager.auth_api.login_user(login_data)
        # Валидируем ответ с помощью Pydantic модели
        login_response = LoginResponse(**response.json())

        # Проверяем токен
        assert login_response.accessToken is not None
        assert isinstance(login_response.accessToken, str)
        assert len(login_response.accessToken) > 0
        # Проверяем данные пользователя в ответе
        assert login_response.user.email == registered_user.email
        assert login_response.user.id is not None

        expected_roles = [role.value for role in registered_user.roles]
        actual_roles = []
        for role in login_response.user.roles:
            if hasattr(role, 'value'):
                actual_roles.append(role.value)
            else:
                actual_roles.append(str(role))

        assert actual_roles == expected_roles

    def test_login_wrong_password(self, api_manager: ApiManager,
                                  registered_user: RegistrationUserData):
        """Тест на авторизацию с неправильным паролем."""
        wrong_login_data = {
            "email": registered_user.email,
            "password": 'wrong_password_123!'
        }

        try:
            api_manager.auth_api.login_user(
                wrong_login_data,
                expected_status=200
            )
            pytest.fail('Ожидается ошибка 401, но запрос прошел успешно')
        except ValueError as e:
            error_str = str(e)
            # Проверяем, что в ошибке есть код 401
            assert '401' in error_str, f'Должна быть ошибка 401, но получили: {error_str}'

    def test_login_nonexistent_user(self, api_manager: ApiManager):
        """Тест на авторизацию несуществующего пользователя."""
        nonexistent_login = {
            "email": "nonexistent_user@example.com",
            "password": "some_password_123!"
        }

        try:
            api_manager.auth_api.login_user(
                nonexistent_login,
                expected_status=200
            )
            pytest.fail("Ожидалась ошибка 404 или 401, но запрос прошел успешно")
        except ValueError as e:
            error_message = str(e)
            assert "404" in error_message or "401" in error_message, \
                f"Должна быть ошибка 404 или 401, но получили: {error_message}"

    def test_login_without_password(self, api_manager: ApiManager):
        """Тест на авторизацию без пароля"""
        try:
            # Попытка отправить неполные данные (без пароля)
            incomplete_data = {"email": "test@example.com"}

            api_manager.auth_api.login_user(
                incomplete_data,
                expected_status=200
            )
            pytest.fail("Ожидалась ошибка 400 или 500, но запрос прошел успешно")
        except ValueError as e:
            error_message = str(e)
            # Может быть 400 (валидация) или 500 (ошибка сервера)
            assert "400" in error_message or "500" in error_message, \
                f"Должна быть ошибка 400 или 500, но получили: {error_message}"

    def test_register_with_mismatched_passwords(self):
        """Тест на регистрацию с несовпадающими паролями (валидация Pydantic)."""
        with pytest.raises(ValueError) as exc_info:
            RegistrationUserData(
                email="test@example.com",
                fullName="Test User",
                password="Password123!",
                passwordRepeat="DifferentPassword123!",
                roles=[Roles.USER]
            )

        assert "Passwords do not match" in str(exc_info.value)

    def test_register_with_weak_password(self):
        """Тест на регистрацию со слабым паролем (валидация Pydantic)."""
        with pytest.raises(ValueError) as exc_info:
            RegistrationUserData(
                email="test@example.com",
                fullName="Test User",
                password="12345678",  # Только цифры
                passwordRepeat="12345678",
                roles=[Roles.USER]
            )

        assert "Password cannot consist only of digits" in str(exc_info.value)