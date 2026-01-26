import random
import pytest
import requests
import uuid
from faker import Faker
from datetime import datetime
from typing import Dict,Any
from api.api_manager import ApiManager
from constants.constants import AUTH_BASE_URL, MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester
from entities.user import User
from constants.roles import Roles
from models.user_models import RegistrationUserData, LoginRequest, LoginResponse, UserCreateRequest
from tools import Tools
from utils.data_generator import DataGenerator
from resources.user_creds import SuperAdminCreds
from sqlalchemy.orm import Session
from db_requester.db_client import get_db_session
from db_requester.db_helpers import DBHelper, MovieDBHelper
from db_models.movies import MovieDBModel
from playwright.sync_api import sync_playwright


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
        if response.status_code in [200, 201]:
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

@pytest.fixture(scope="module")
def db_session() -> Session:
    """
    Фикстура, которая создает и возвращает сессию для работы с базой данных
    После завершения теста сессия автоматически закрывается
    """
    db_session = get_db_session()
    yield db_session
    db_session.close()

@pytest.fixture(scope="function")
def db_helper(db_session) -> DBHelper:
    """
    Фикстура для экземпляра хелпера
    """
    db_helper = DBHelper(db_session)
    return db_helper

@pytest.fixture(scope="function")
def created_test_user(db_helper):
    """
    Фикстура, которая создает тестового пользователя в БД
    и удаляет его после завершения теста
    """
    user = db_helper.create_test_user(DataGenerator.generate_user_data())
    yield user
    # Cleanup после теста
    if db_helper.get_user_by_id(user.id):
        db_helper.delete_user(user)


@pytest.fixture(scope="function")
def movie_helper(db_session) -> MovieDBHelper:
    """Фикстура для хелпера фильмов"""
    return MovieDBHelper(db_session)


@pytest.fixture(scope="function")
def sample_movie_data() -> Dict[str, Any]:
    """Тестовые данные фильма"""
    unique_id = str(uuid.uuid4())[:8]
    return {
        'id': int(str(uuid.uuid4().int)[:8]),  # Числовой ID
        'name': f"Тестовый фильм {uuid.uuid4().hex[:8]}",
        'price': random.randint(1, 50), # Целое число! int4
        'description': f'Описание тестового фильма {uuid.uuid4().hex[:8]}',
        'image_url': f'https://example.com/test_{uuid.uuid4().hex[:8]}.jpg',
        'location': random.choice(['SPB', 'MSK']),
        'published': True,
        'rating': round(random.uniform(1.0, 10.0), 1), #Дробное число! float8 в БД!
        'genre_id': random.randint(1, 10),  # Числовой ID от 1 до 10,
        'created_at': datetime.now()
    }


@pytest.fixture(scope="function")
def created_test_movie(movie_helper, sample_movie_data) -> MovieDBModel:
    """Создает и удаляет тестовый фильм"""
    movie = movie_helper.create_movie(sample_movie_data)
    yield movie

    # Cleanup
    if movie_helper.movie_exists(movie.id):
        movie_helper.delete_movie(movie.id)

#ФИКСТУРЫ PLAYWRIGHT

DEFAULT_UI_TIMEOUT = 30000  # Пример значения таймаута

@pytest.fixture(scope="session")  # Браузер запускается один раз для всей сессии
def browser(playwright):
    browser = playwright.chromium.launch(headless=False)  # headless=True для CI/CD, headless=False для локальной разработки
    yield browser  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    browser.close()  # Браузер закрывается после завершения всех тестов


@pytest.fixture(scope="function")
def context(browser):
    context = browser.new_context()
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    context.set_default_timeout(DEFAULT_UI_TIMEOUT)
    yield context
    log_name = f"trace_{Tools.get_timestamp()}.zip"
    trace_path = Tools.files_dir('playwright_trace', log_name)
    context.tracing.stop(path=trace_path)
    context.close()



@pytest.fixture(scope="function")  # Страница создается для каждого теста
def page(context):
    page = context.new_page()
    yield page  # yield возвращает значение фикстуры, выполнение теста продолжится после yield
    page.close()  # Страница закрывается после завершения теста
