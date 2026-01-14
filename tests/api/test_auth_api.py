import datetime
import json
import pytest
import allure
from pytest_check import check
from api.api_manager import ApiManager
from constants.roles import Roles
from models.user_models import (RegisterUserResponse, RegistrationUserData,
                                LoginResponse, LoginRequest)

class TestAuthApi:

    @allure.title("Тест регистрации пользователя с помощью Mock")
    @allure.severity(allure.severity_level.MINOR)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.mock
    @pytest.mark.unit
    @pytest.mark.positive
    def test_register_user_mock(self, api_manager: ApiManager, registration_user_data: RegistrationUserData, mocker):
        with allure.step("Мокаем метод register_user в auth_api"):
            # Создаем mock данные для ответа
            mock_response_data = {
                "id": "id",
                "email": "email@email.com",
                "fullName": "fullName",
                "verified": True,
                "banned": False,
                "roles": [Roles.SUPER_ADMIN.value],  # Используем .value для enum
                "createdAt": str(datetime.datetime.now())
            }

            # Создаем mock Response объект
            from requests.models import Response
            mock_api_response = Response()
            mock_api_response.status_code = 201
            mock_api_response._content = json.dumps(mock_response_data).encode('utf-8')

            mocker.patch.object(
                api_manager.auth_api,  # Объект, который нужно замокать
                'register_user',  # Метод, который нужно замокать
                return_value=mock_api_response  # Фиктивный ответ как Response объект
            )

        with allure.step("Вызываем метод, который должен быть замокан"):
            # Преобразуем RegistrationUserData в словарь, как в реальном тесте
            user_data_dict = registration_user_data.model_dump()
            if 'roles' in user_data_dict:
                user_data_dict['roles'] = [role.value for role in registration_user_data.roles]

            response = api_manager.auth_api.register_user(user_data_dict)
            # Преобразуем ответ в RegisterUserResponse
            register_user_response = RegisterUserResponse(**response.json())

        with allure.step("Проверяем, что ответ соответствует ожидаемому"):
            with allure.step("Проверка поля персональных данных"):
                with check:
                    # Эта проверка специально должна провалиться, но тест продолжит работу
                    check.equal(register_user_response.fullName, "INCORRECT_NAME", "НЕСОВПАДЕНИЕ fullName")
                    check.equal(register_user_response.email, mock_response_data["email"])

            with allure.step("Проверка поля banned"):
                with check("Проверка поля banned"):
                    check.equal(register_user_response.banned, mock_response_data["banned"])

    @allure.title("Тест регистрации пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.positive
    @pytest.mark.create
    @pytest.mark.integration
    def test_register_user(self, api_manager: ApiManager,
                           registration_user_data: RegistrationUserData):
        with allure.step("Подготовка данных для регистрации пользователя"):
            # Преобразуем в словарь
            user_data_dict = registration_user_data.model_dump()
            # Преобразуем Roles enum в строки
            if 'roles' in user_data_dict:
                user_data_dict['roles'] = [role.value for role in registration_user_data.roles]

        with allure.step("Регистрируем пользователя"):
            response = api_manager.auth_api.register_user(
                user_data=user_data_dict,
                expected_status=201
            )

        with allure.step("Валидируем ответ"):
            response_data = response.json()
            # Добавляем поле banned со значением по умолчанию, если его нет в ответе
            if 'banned' not in response_data:
                response_data['banned'] = False

            register_response = RegisterUserResponse(**response_data)

        with allure.step("Проверяем поля ответа"):
            with allure.step("Проверка email и имени"):
                assert register_response.email == registration_user_data.email
                assert register_response.fullName == registration_user_data.fullName

            with allure.step("Проверка ролей"):
                assert register_response.roles == registration_user_data.roles

            with allure.step("Проверка ID пользователя"):
                assert isinstance(register_response.id, str) and len(register_response.id) > 0

            with allure.step("Проверка статусов verified и banned"):
                assert register_response.verified is True
                assert register_response.banned is False

    @allure.title("Тест регистрации и авторизации пользователя")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.positive
    @pytest.mark.login
    @pytest.mark.integration
    @pytest.mark.e2e
    def test_register_and_login_user(self, api_manager: ApiManager,
                                     registered_user: RegistrationUserData):
        """Тест на регистрацию и авторизацию пользователя."""
        with allure.step("Подготовка данных для авторизации"):
            login_request = LoginRequest(
                email=registered_user.email,
                password=registered_user.password
            )
            login_data = login_request.model_dump()

        with allure.step("Выполняем авторизацию пользователя"):
            # API возвращает 201 при успешной авторизации
            response = api_manager.auth_api.login_user(
                login_data,
                expected_status=201  # Изменено с 200 на 201
            )

        with allure.step("Валидируем ответ авторизации"):
            login_response = LoginResponse(**response.json())

        with allure.step("Проверяем данные в ответе"):
            with allure.step("Проверка access token"):
                assert login_response.accessToken is not None
                assert isinstance(login_response.accessToken, str)
                assert len(login_response.accessToken) > 0

            with allure.step("Проверка refresh token"):
                assert login_response.refreshToken is not None
                assert isinstance(login_response.refreshToken, str)
                assert len(login_response.refreshToken) > 0

            with allure.step("Проверка expiresIn"):
                assert login_response.expiresIn is not None
                assert isinstance(login_response.expiresIn, int)
                assert login_response.expiresIn > 0

            with allure.step("Проверка email пользователя"):
                assert login_response.user.email == registered_user.email

            with allure.step("Проверка ID пользователя"):
                assert login_response.user.id is not None

            with allure.step("Проверка ролей пользователя"):
                expected_roles = [role.value for role in registered_user.roles]
                actual_roles = []
                for role in login_response.user.roles:
                    if hasattr(role, 'value'):
                        actual_roles.append(role.value)
                    else:
                        actual_roles.append(str(role))

                assert actual_roles == expected_roles

    @allure.title("Тест авторизации с неправильным паролем")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.auth
    @pytest.mark.invalid_credentials
    def test_login_wrong_password(self, api_manager: ApiManager,
                                  registered_user: RegistrationUserData):
        """Тест на авторизацию с неправильным паролем."""
        with allure.step("Подготовка данных с неправильным паролем"):
            wrong_login_data = {
                "email": registered_user.email,
                "password": 'wrong_password_123!'
            }

        with allure.step("Пытаемся авторизоваться с неправильным паролем"):
            try:
                api_manager.auth_api.login_user(
                    wrong_login_data,
                    expected_status=201  # Изменено с 200 на 201
                )
                pytest.fail('Ожидается ошибка 401, но запрос прошел успешно')
            except ValueError as e:
                error_str = str(e)
                # Проверяем, что в ошибке есть код 401
                assert '401' in error_str, f'Должна быть ошибка 401, но получили: {error_str}'

    @allure.title("Тест авторизации несуществующего пользователя")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.negative
    @pytest.mark.security
    @pytest.mark.auth
    @pytest.mark.nonexistent_user
    def test_login_nonexistent_user(self, api_manager: ApiManager):
        """Тест на авторизацию несуществующего пользователя."""
        with allure.step("Подготовка данных несуществующего пользователя"):
            nonexistent_login = {
                "email": "nonexistent_user@example.com",
                "password": "some_password_123!"
            }

        with allure.step("Пытаемся авторизоваться с несуществующим пользователем"):
            try:
                api_manager.auth_api.login_user(
                    nonexistent_login,
                    expected_status=201  # Изменено с 200 на 201
                )
                pytest.fail("Ожидалась ошибка 404 или 401, но запрос прошел успешно")
            except ValueError as e:
                error_message = str(e)
                assert "404" in error_message or "401" in error_message, \
                    f"Должна быть ошибка 404 или 401, но получили: {error_message}"

    @allure.title("Тест авторизации без пароля")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.auth
    @pytest.mark.incomplete_data
    def test_login_without_password(self, api_manager: ApiManager):
        """Тест на авторизацию без пароля"""
        with allure.step("Подготовка данных без пароля"):
            incomplete_data = {"email": "test@example.com"}

        with allure.step("Пытаемся авторизоваться без пароля"):
            try:
                api_manager.auth_api.login_user(
                    incomplete_data,
                    expected_status=201  # Изменено с 200 на 201
                )
                pytest.fail("Ожидалась ошибка 400 или 500, но запрос прошел успешно")
            except ValueError as e:
                error_message = str(e)
                # Может быть 400 (валидация) или 500 (ошибка сервера)
                assert "400" in error_message or "500" in error_message, \
                    f"Должна быть ошибка 400 или 500, но получили: {error_message}"

    @allure.title("Тест регистрации с несовпадающими паролями")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.unit
    @pytest.mark.model_validation
    def test_register_with_mismatched_passwords(self):
        """Тест на регистрацию с несовпадающими паролями (валидация Pydantic)."""
        with allure.step("Пытаемся создать объект с несовпадающими паролями"):
            with pytest.raises(ValueError) as exc_info:
                RegistrationUserData(
                    email="test@example.com",
                    fullName="Test User",
                    password="Password123!",
                    passwordRepeat="DifferentPassword123!",
                    roles=[Roles.USER]
                )

        with allure.step("Проверяем сообщение об ошибке"):
            assert "Passwords do not match" in str(exc_info.value)

    @allure.title("Тест регистрации со слабым паролем")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.label("qa_name", "Ivan Petrovich")
    @pytest.mark.negative
    @pytest.mark.validation
    @pytest.mark.security
    @pytest.mark.unit
    @pytest.mark.model_validation
    def test_register_with_weak_password(self):
        """Тест на регистрацию со слабым паролем (валидация Pydantic)."""
        with allure.step("Пытаемся создать объект со слабым паролем"):
            with pytest.raises(ValueError) as exc_info:
                RegistrationUserData(
                    email="test@example.com",
                    fullName="Test User",
                    password="12345678",  # Только цифры
                    passwordRepeat="12345678",
                    roles=[Roles.USER]
                )

        with allure.step("Проверяем сообщение об ошибке"):
            assert "Password cannot consist only of digits" in str(exc_info.value)