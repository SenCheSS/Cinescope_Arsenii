import pytest
import requests
from faker import Faker
from api.api_manager import ApiManager
from constants.constants import AUTH_BASE_URL, MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester
from entities.user import User
from constants.roles import Roles
from models.user_models import RegistrationUserData, LoginRequest, LoginResponse, UserCreateRequest
from utils.data_generator import DataGenerator
from resources.user_creds import SuperAdminCreds

faker = Faker()

def get_auth_token():
    """Получение токена"""
    auth_url = f"{AUTH_BASE_URL}login"
    auth_data = {
        "email": "api1@gmail.com",
        "password": "asdqwe123Q"
    }

    try:
        response = requests.post(auth_url, json=auth_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get('accessToken')
            print("Token obtained successfully")
            return token
        else:
            print(f"Auth failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Auth error: {e}")
        return None

@pytest.fixture(scope='session')
def auth_token():
    """Фикстура для получения auth token"""
    return get_auth_token()

@pytest.fixture(scope='session')
def session(auth_token):
    """Фикстура для создания HTTP-сессии с авторизацией"""
    http_session = requests.Session()
    http_session.base_url = MOVIES_BASE_URL
    http_session.base_url = AUTH_BASE_URL
    http_session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })

    # Добавляем авторизацию если токен получен
    if auth_token:
        http_session.headers.update({"Authorization": f"Bearer {auth_token}"})
        print("Authorization header added to session")
    else:
        print("No authorization token - only public endpoints will work")

    yield http_session
    http_session.close()

@pytest.fixture(scope='session')
def api_manager(session):
    """Фикстура для создания экземпляра ApiManager."""
    return ApiManager(session)

@pytest.fixture
def movie_data():
    """Фикстура с данными для создания фильма"""
    return DataGenerator.generate_movie_data()

@pytest.fixture
def created_movie(api_manager, movie_data):
    """Фикстура для создания тестового фильма с последующим удалением"""
    movie_id = None
    try:
        response = api_manager.movies_api.create_movie(movie_data)
        if response.status_code == 201:
            movie_data = response.json()
            movie_id = movie_data["id"]
            yield movie_data
        else:
            yield None

    finally:
        # Удаляем фильм после теста
        if movie_id:
            try:
                api_manager.movies_api.delete_movie(movie_id)
            except:
                pass

@pytest.fixture(scope="session")
def requester():
    """Фикстура для создания экземпляра CustomRequester."""
    session = requests.Session()
    return CustomRequester(session=session, base_url=AUTH_BASE_URL)

@pytest.fixture
def user_session():
    user_pool = []

    def _create_user_session():
        session = requests.Session()
        session.base_uel = AUTH_BASE_URL
        user_session = ApiManager(session)
        user_pool.append(user_session)
        return user_session

    yield _create_user_session

    for user in user_pool:
        user.close_session()

@pytest.fixture
def super_admin(user_session):
    new_session = user_session()

    super_admin = User(
        SuperAdminCreds.USERNAME,
        SuperAdminCreds.PASSWORD,
        [Roles.SUPER_ADMIN.value],
        new_session)

    super_admin.api.auth_api.authenticate(super_admin.creds)
    return super_admin

@pytest.fixture
def registration_user_data() -> RegistrationUserData:
    random_password = DataGenerator.generate_random_password()

    registration_data = RegistrationUserData(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.USER]
    )

    return registration_data

@pytest.fixture
def create_user_data(registration_user_data: RegistrationUserData) -> RegistrationUserData:
    """Алиас для registration_user_data для обратной совместимости.
    Используется в фикстуре common_user."""
    return registration_user_data

@pytest.fixture
def common_user(user_session, super_admin, registration_user_data: RegistrationUserData):
    """Фикстура для создания обычного пользователя."""
    new_session = user_session()

    # Создаем UserCreateRequest с обязательными полями
    user_request = UserCreateRequest(
        email=registration_user_data.email,
        fullName=registration_user_data.fullName,
        password=registration_user_data.password,
        roles=registration_user_data.roles,
        verified=True,
        banned=False
    )

    user_data = user_request.model_dump()
    user_data['roles'] = [role.value for role in user_request.roles]

    # Создаем пользователя через API суперадмина
    super_admin.api.user_api.create_user(user_data)

    # Создаем объект User для common_user
    common_user = User(
        registration_user_data.email,
        registration_user_data.password,
        [role.value for role in registration_user_data.roles],
        new_session
    )

    common_user.api.auth_api.authenticate(common_user.creds)
    return common_user

@pytest.fixture
def admin_user(user_session, super_admin):
    """Фикстура для создания пользователя с ролью ADMIN."""
    new_session = user_session()

    # Создаем RegistrationUserData для админа
    random_password = DataGenerator.generate_random_password()

    admin_registration_data = RegistrationUserData(
        email=DataGenerator.generate_random_email(),
        fullName=DataGenerator.generate_random_name(),
        password=random_password,
        passwordRepeat=random_password,
        roles=[Roles.ADMIN]
    )

    # Создаем UserCreateRequest с обязательными полями
    admin_request = UserCreateRequest(
        email=admin_registration_data.email,
        fullName=admin_registration_data.fullName,
        password=admin_registration_data.password,
        roles=admin_registration_data.roles,
        verified=True,
        banned=False
    )

    # Преобразуем модель в словарь и Enum в строки
    admin_data = admin_request.model_dump()
    admin_data['roles'] = [role.value for role in admin_request.roles]

    # Создаем админа через API
    super_admin.api.user_api.create_user(admin_data)

    # Создаем объект User для админа
    admin_user = User(
        admin_registration_data.email,
        admin_registration_data.password,
        [role.value for role in admin_registration_data.roles],
        new_session
    )

    admin_user.api.auth_api.authenticate(admin_user.creds)

    yield admin_user

    # Очистка после теста
    try:
        if hasattr(super_admin.api.user_api, 'delete_user'):
            super_admin.api.user_api.delete_user(admin_user.email)
    except Exception as e:
        print(f"Cleanup error for admin {admin_user.email}: {e}")

@pytest.fixture(scope="function")
def registered_user(api_manager, registration_user_data: RegistrationUserData):
    """Фикстура для регистрации пользователя с автоматической очисткой."""
    user_id = None

    try:
        # Для регистрации через auth_api используем RegistrationUserData
        user_data_dict = registration_user_data.model_dump()

        # Преобразуем Enum в строки
        if 'roles' in user_data_dict:
            user_data_dict['roles'] = [role.value for role in registration_user_data.roles]

        # Регистрируем пользователя через API
        response = api_manager.auth_api.register_user(
            user_data_dict,
            expected_status=201
        )
        response_data = response.json()

        # Создаем копию с ID для возврата
        registered_user = registration_user_data.model_copy()
        registered_user._id = response_data["id"]
        user_id = response_data["id"]

        yield registered_user

    except ValueError as e:
        # Если пользователь уже существует (409), пробуем получить его через логин
        if "409" in str(e):
            try:
                login_response = api_manager.auth_api.login_user(
                    {
                        "email": registration_user_data.email,
                        "password": registration_user_data.password
                    },
                    expected_status=200
                )
                login_data = login_response.json()

                # Создаем копию с ID
                registered_user = registration_user_data.model_copy()
                registered_user._id = login_data["user"]["id"]
                user_id = login_data["user"]["id"]

                yield registered_user

            except Exception as login_error:
                print(f"Login failed for existing user: {login_error}")
                yield registration_user_data
        else:
            print(f"Registration error: {e}")
            raise
    finally:
        # Очистка
        if user_id:
            try:
                if hasattr(api_manager.user_api, 'delete_user'):
                    api_manager.user_api.delete_user(user_id)
            except Exception as cleanup_error:
                print(f"Cleanup error for user {user_id}: {cleanup_error}")