import pytest
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from models.user_models import RegistrationUserData, RegisterUserResponse, UserCreateRequest
from constants.roles import Roles


class TestUser:
    def test_create_user(self, super_admin, registration_user_data: RegistrationUserData):

        # Преобразуем RegistrationUserData в UserCreateRequest для API
        user_request = UserCreateRequest(
            email=registration_user_data.email,
            fullName=registration_user_data.fullName,
            password=registration_user_data.password,
            roles=registration_user_data.roles,
            verified=True,
            banned=False
        )

        # Создаем пользователя
        response = super_admin.api.user_api.create_user(user_request.to_api_dict())
        # Валидируем ответ через Pydantic
        user_response = RegisterUserResponse(**response.json())
        # Проверки
        assert user_response.id and user_response.id != '', "ID должен быть не пустым"
        assert user_response.email == registration_user_data.email
        assert user_response.fullName == registration_user_data.fullName
        # Преобразуем роли для сравнения
        expected_roles = [role.value for role in registration_user_data.roles]
        actual_roles = []
        for role in user_response.roles:
            if hasattr(role, 'value'):
                actual_roles.append(role.value)
            else:
                actual_roles.append(str(role))

        assert actual_roles == expected_roles

        assert user_response.verified is True
        assert user_response.banned is False

    def test_get_user_by_locator(self, super_admin, registration_user_data: RegistrationUserData):
        # Создаем пользователя
        user_request = UserCreateRequest(
            email=registration_user_data.email,
            fullName=registration_user_data.fullName,
            password=registration_user_data.password,
            roles=registration_user_data.roles,
            verified=True,
            banned=False
        )
        created_user_response = super_admin.api.user_api.create_user(
            user_request.to_api_dict()).json()
        created_user = RegisterUserResponse(**created_user_response)
        # Получаем пользователя по ID
        response_by_id = super_admin.api.user_api.get_user(created_user.id).json()
        user_by_id = RegisterUserResponse(**response_by_id)
        # Получаем пользователя по email
        response_by_email = super_admin.api.user_api.get_user(registration_user_data.email).json()
        user_by_email = RegisterUserResponse(**response_by_email)
        # Проверяем, что данные одинаковые
        assert user_by_id.id == user_by_email.id
        assert user_by_id.email == user_by_email.email
        assert user_by_id.fullName == user_by_email.fullName

        def get_role_strings(roles):
            return [
                role.value if hasattr(role, 'value') else str(role)
                for role in roles
            ]

        user_by_id_roles = get_role_strings(user_by_id.roles)
        user_by_email_roles = get_role_strings(user_by_email.roles)
        assert user_by_id_roles == user_by_email_roles

        assert user_by_id.verified == user_by_email.verified
        assert user_by_id.banned == user_by_email.banned
        # Проверяем конкретные значения
        assert user_by_id.id and user_by_id.id != '', "ID должен быть не пустым"
        assert user_by_id.email == registration_user_data.email
        assert user_by_id.fullName == registration_user_data.fullName

        expected_roles = [role.value for role in registration_user_data.roles]
        actual_roles = get_role_strings(user_by_id.roles)
        assert actual_roles == expected_roles, \
            f"Roles don't match. Expected: {expected_roles}, Got: {actual_roles}"
        assert user_by_id.verified is True
        assert user_by_id.banned is False

    def test_get_user_by_id_common_user(self, common_user):
        # Тест на попытку получения пользователя без прав
        common_user.api.user_api.get_user(common_user.email, expected_status=403)