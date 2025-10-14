from faker import Faker
import pytest
import requests

from api.api_manager import ApiManager
from constants import BASE_URL, HEADERS, REGISTER_ENDPOINT, LOGIN_ENDPOINT
from custom_requester.custom_requester import CustomRequester
from utils.data_generator import DataGenerator

faker = Faker()

@pytest.fixture(scope='session')
def test_user():
    """
    Генерация случайного пользователя для тестов.
    """
    random_email = DataGenerator.generate_random_email()
    random_name = DataGenerator.generate_random_name()
    random_password = DataGenerator.generate_random_password()

    return {
        'email': random_email,
        'fullName': random_name,
        'password': random_password,
        'passwordRepeat': random_password,
        'roles': ['USER']
    }
'''
@pytest.fixture(scope="session")
def registered_user(requester, test_user):
    """
    Фикстура для регистрации и получения данных зарегистрированного пользователя.
    """
    try:
        # Пытаемся зарегистрировать пользователя
        response = requester.send_request(
            method="POST",
            endpoint=REGISTER_ENDPOINT,
            data=test_user,
            expected_status=201
        )
        response_data = response.json()
        registered_user = test_user.copy()
        registered_user["id"] = response_data["id"]
        return registered_user

    except ValueError as e:
        # Если пользователь уже существует (409), просто возвращаем данные
        if "409" in str(e):
            print(f"Пользователь {test_user['email']} уже существует, используем существующие данные")
            # Попробуем получить ID через логин
            try:
                login_response = requester.session.post(
                    f"{BASE_URL}{LOGIN_ENDPOINT}",
                    json={"email": test_user["email"], "password": test_user["password"]}
                )
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    registered_user = test_user.copy()
                    registered_user["id"] = login_data["user"]["id"]
                    return registered_user
            except:
                pass

            # Если не удалось получить ID, возвращаем без него
            return test_user.copy()
        else:
            # Другие ошибки прокидываем дальше
            raise
'''
@pytest.fixture(scope='session')
def session():
    """ Фикстура для создания HTTP-сессии."""
    http_session = requests.Session()
    http_session.base_url = BASE_URL
    yield http_session
    http_session.close()

@pytest.fixture(scope='session')
def api_manager(session):
    """Фикстура для создания экземпляра ApiManager."""
    return ApiManager(session)

@pytest.fixture(scope="session")
def requester():
    """
    Фикстура для создания экземпляра CustomRequester.
    """
    session = requests.Session()
    return CustomRequester(session=session, base_url=BASE_URL)


@pytest.fixture(scope="function")  # меняем на function для очистки после каждого теста
def registered_user(api_manager, test_user):
    """Фикстура для регистрации пользователя с автоматической очисткой после теста."""
    user_id = None

    try:
        # Регистрируем пользователя
        response = api_manager.auth_api.register_user(test_user, expected_status=201)
        response_data = response.json()

        registered_user = test_user.copy()
        registered_user["id"] = response_data["id"]
        user_id = response_data["id"]

        yield registered_user

    except ValueError as e:
        # Если пользователь уже существует, получаем ID через логин
        if "409" in str(e):
            try:
                login_response = api_manager.auth_api.login_user(
                    {"email": test_user["email"], "password": test_user["password"]},
                    expected_status=200
                )
                login_data = login_response.json()
                registered_user = test_user.copy()
                registered_user["id"] = login_data["user"]["id"]
                user_id = login_data["user"]["id"]

                yield registered_user

            except:
                yield test_user.copy()
        else:
            raise
    finally:
        # ОЧИСТКА: удаляем пользователя после теста
        if user_id:
            api_manager.user_api.clean_up_user(user_id)