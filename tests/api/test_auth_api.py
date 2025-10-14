from multiprocessing.resource_tracker import register
from tkinter import BaseWidget

import pytest
import requests
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from api.api_manager import ApiManager


class TestAuthApi:
    def test_register_user(self, api_manager: ApiManager, test_user):
        """
        Тест на регистрацию пользователя.
        """
        response = api_manager.auth_api.register_user(test_user)
        response_data = response.json()

        assert response_data["email"] == test_user["email"], "Email не совпадает"
        assert "id" in response_data, "ID пользователя отсутствует в ответе"
        assert "roles" in response_data, "Роли пользователя отсутствуют в ответе"
        assert "USER" in response_data["roles"], "Роль USER должна быть у пользователя"

    def test_register_and_login_user(self, api_manager: ApiManager, registered_user):
        """Тест на регистрацию и авторизацию пользователя."""
        login_data = {
            "email": registered_user["email"],
            "password": registered_user["password"]
        }
        response = api_manager.auth_api.login_user(login_data)
        response_data = response.json()

        assert "accessToken" in response_data, "Токен доступа отсутствует в ответе"
        assert response_data["user"]["email"] == registered_user["email"], "Email не совпадает"

    def test_login_wrong_password(self, api_manager: ApiManager, registered_user):
        """Тест на авторизацию с неправильным паролем."""
        try:
            api_manager.auth_api.login_user(
                {
                    'email': registered_user['email'],
                    'password': 'wrong_password_123!'
                },
                expected_status=200
            )
            assert False, 'Ожидается ошибка 401, но запрос прошел успешно'
        except ValueError as e:
            assert '401' in str(e), f'Должна быть ошибка 401, но получили: {e}'

    def test_login_nonexistent_user(self, api_manager: ApiManager):
        """Тест на авторизацию несуществующего пользователя."""
        try:
            api_manager.auth_api.login_user(
                {
                    "email": "nonexistent_user@example.com",
                    "password": "some_password_123!"
                },
                expected_status=200
            )
            assert False, "Ожидалась ошибка 404 или 401, но запрос прошел успешно"
        except ValueError as e:
            error_message = str(e)
            assert "404" in error_message or "401" in error_message, \
                f"Должна быть ошибка 404 или 401, но получили: {error_message}"

    def test_login_without_password(self, api_manager: ApiManager, registered_user):
        """Тест на авторизацию без пароля"""
        try:
            api_manager.auth_api.login_user(
                {"email": registered_user["email"]},  # Без пароля
                expected_status=200
            )
            assert False, "Ожидалась ошибка 400 или 500, но запрос прошел успешно"
        except ValueError as e:
            # ASSERT
            error_message = str(e)
            assert "400" in error_message or "500" in error_message, \
                f"Должна быть ошибка 400 или 500, но получили: {error_message}"