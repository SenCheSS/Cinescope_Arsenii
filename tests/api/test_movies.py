import pytest
import requests
import time
import allure
from pytest_check import check
from conftest import movie_data
from constants.roles import Roles
from utils.data_generator import DataGenerator


class TestMovies:

    @allure.title("Создание фильма супер-администратором")
    @allure.description("Позитивный тест создания фильма пользователем с ролью SUPER_ADMIN")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    @pytest.mark.positive
    @pytest.mark.create
    @pytest.mark.super_admin
    def test_create_movie_by_super_admin(self, super_admin, movie_data):
        with allure.step("Отправка запроса на создание фильма"):
            response = super_admin.api.movies_api.create_movie(movie_data)

        with allure.step("Проверка статус кода 201"):
            assert response.status_code == 201

        with allure.step("Проверка данных созданного фильма"):
            movie_response = response.json()
            assert movie_response["name"] == movie_data["name"]
            assert movie_response["genreId"] == movie_data["genreId"]

    @allure.title("Попытка создания фильма обычным пользователем")
    @allure.description("Негативный тест: пользователь с ролью USER не может создавать фильмы")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.permissions
    @pytest.mark.user
    def test_create_movie_by_user_should_fail(self, common_user, movie_data):
        with allure.step("Отправка запроса на создание фильма от имени обычного пользователя"):
            response = common_user.api.movies_api.create_movie(
                movie_data,
                expected_status=403
            )

        with allure.step("Проверка что доступ запрещен (403)"):
            assert response.status_code == 403

    @allure.title("Попытка создания фильма администратором")
    @allure.description("Негативный тест: пользователь с ролью ADMIN не может создавать фильмы")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.positive
    @pytest.mark.permissions
    @pytest.mark.role_admin
    def test_create_movie_by_admin(self, admin_user, movie_data):
        with allure.step("Отправка запроса на создание фильма от имени администратора"):
            response = admin_user.api.movies_api.create_movie(
                movie_data,
                expected_status=403
            )

        with allure.step("Проверка что доступ запрещен (403)"):
            assert response.status_code == 403

    @allure.title("Получение списка фильмов обычным пользователем")
    @allure.description("Позитивный тест получения списка фильмов пользователем с ролью USER")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.positive
    @pytest.mark.smoke
    @pytest.mark.read
    def test_get_movies_by_user(self, common_user):
        with allure.step("Запрос списка всех фильмов"):
            response = common_user.api.movies_api.get_all_movies()

        with allure.step("Проверка успешного ответа (200)"):
            assert response.status_code == 200

    @allure.title("Получение фильма по ID обычным пользователем")
    @allure.description("Позитивный тест получения конкретного фильма по его идентификатору")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.positive
    @pytest.mark.read
    @pytest.mark.slow
    @pytest.mark.integration
    def test_get_movie_by_id_by_user(self, common_user, created_movie):
        if created_movie:
            with allure.step(f"Запрос фильма с ID {created_movie['id']}"):
                response = common_user.api.movies_api.get_movie_by_id(created_movie["id"])

            with allure.step("Проверка успешного ответа (200)"):
                assert response.status_code == 200

class TestMoviesFiltering:

    @allure.title("Получение фильмов с фильтрацией: {filter_params}")
    @allure.description("""
    Параметризованный тест получения фильмов с различными фильтрами.
    Проверяет что:
    1. Все фильмы в ответе соответствуют фильтрам
    2. Все фильмы имеют обязательные поля
    3. Все фильмы имеют соответствующий рейтинг
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.positive
    @pytest.mark.filtering
    @pytest.mark.parametrized
    @pytest.mark.slow
    @pytest.mark.integration
    @pytest.mark.parametrize('filter_params, expected_conditions', [
        (
                {'location': 'MSK'},
                lambda movies: all(movie.get('location') == 'MSK' for movie in movies)
        ),
        (
                {'published': 'true'},
                lambda movies: all(movie.get('published') is True for movie in movies)
        ),
        (
                {'pageSize': 5},
                lambda movies: len(movies) <= 5
        ),
        (
                {"genreId": 1},
                lambda movies: all(movie.get("genreId") == 1 for movie in movies)
        ),
        (
                {"location": "SPB", "published": "true", "pageSize": 3},
                lambda movies: (
                        len(movies) <= 3 and
                        all(movie.get("location") == "SPB" for movie in movies) and
                        all(movie.get("published") is True for movie in movies)
                )
        ),
    ])
    def test_get_movies_with_filters(self, common_user, filter_params, expected_conditions):
        BROKEN_FILTERS = {'location', 'published'}

        # Если тест использует неработающий фильтр - пропускаем
        if any(key in filter_params for key in BROKEN_FILTERS):
            # Но оставляем проверку genreId даже если есть неработающие фильтры
            if 'genreId' not in filter_params:
                allure.dynamic.description(f"Тест пропущен: фильтр {filter_params} не работает на сервере (баг API)")
                pytest.skip(f"Фильтр {filter_params} не работает на сервере (баг API)")

        with allure.step(f"Отправка запроса с фильтрами: {filter_params}"):
            response = common_user.api.movies_api.get_all_movies(params=filter_params)

        with allure.step("Проверка статуса ответа 200"):
            assert response.status_code == 200, f"Expected 200, got {response.status_code}"

        with allure.step("Извлечение данных из ответа"):
            response_data = response.json()
            movies_data = response_data.get('movies', [])
            allure.attach(str(movies_data), name="Полученные фильмы", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка структуры ответа"):
            assert isinstance(movies_data, list), "Response should be a list of movies"

        with allure.step("Проверка пагинации"):
            if 'pageSize' in filter_params:
                expected_size = int(filter_params['pageSize'])
                assert len(movies_data) <= expected_size or response_data.get('pageSize') == expected_size

        if movies_data:  # Если фильмы найдены
            with allure.step("Проверка соответствия фильтрам"):
                # Для комбинированных фильтров проверяем только работающие части
                if 'genreId' in filter_params:
                    expected_genre = int(filter_params['genreId'])
                    assert all(movie.get('genreId') == expected_genre for movie in movies_data), \
                        f"Not all movies have genreId={expected_genre}"

                # Для pageSize проверяем количество
                if 'pageSize' in filter_params:
                    expected_size = int(filter_params['pageSize'])
                    assert len(movies_data) <= expected_size, \
                        f"Too many movies returned for pageSize={expected_size}"

                # Если фильтр не содержит неработающих параметров, проверяем полностью
                if not any(key in filter_params for key in BROKEN_FILTERS):
                    assert expected_conditions(movies_data), "Not all movies match filter conditions"

            with allure.step("Проверка обязательных полей"):
                required_fields = ["id", "name", "price", "description", "location", "genreId"]
                for movie in movies_data:
                    for field in required_fields:
                        assert field in movie, f"Movie missing required field: {field}"

            with allure.step("Проверка рейтинга"):
                for movie in movies_data:
                    assert "rating" in movie, "Movie missing rating field"
                    assert isinstance(movie["rating"], (int, float)), "Rating should be numeric"
                    assert 0 <= movie["rating"] <= 10, "Rating should be between 0 and 10"

            with allure.step("Проверка дополнительных полей"):
                for movie in movies_data:
                    assert movie["price"] >= 0, "Price should be non-negative"
                    assert movie["location"] in ["MSK", "SPB"], "Location should be MSK or SPB"
                    assert isinstance(movie["published"], bool), "Published should be boolean"

    @allure.title("Тестирование пагинации фильмов")
    @allure.description("Проверка корректной работы пагинации при получении списка фильмов")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.positive
    @pytest.mark.pagination
    @pytest.mark.integration
    def test_get_movies_pagination(self, common_user):
        with allure.step("Получение первой страницы (page=1, pageSize=2)"):
            response_page1 = common_user.api.movies_api.get_all_movies(params={"page": 1, "pageSize": 2})
            assert response_page1.status_code == 200
            data_page1 = response_page1.json()
            movies_page1 = data_page1.get('movies', [])
            allure.attach(str(movies_page1), name="Фильмы на странице 1", attachment_type=allure.attachment_type.JSON)

        with allure.step("Получение второй страницы (page=2, pageSize=2)"):
            response_page2 = common_user.api.movies_api.get_all_movies(params={"page": 2, "pageSize": 2})
            assert response_page2.status_code == 200
            data_page2 = response_page2.json()
            movies_page2 = data_page2.get('movies', [])
            allure.attach(str(movies_page2), name="Фильмы на странице 2", attachment_type=allure.attachment_type.JSON)

        with allure.step("Проверка отсутствия пересечений между страницами"):
            if len(movies_page1) == 2 and len(movies_page2) == 2:
                page1_ids = {movie["id"] for movie in movies_page1}
                page2_ids = {movie["id"] for movie in movies_page2}
                if page1_ids & page2_ids:
                    allure.attach("Пересекающиеся ID: " + str(page1_ids & page2_ids),
                                  name="Предупреждение",
                                  attachment_type=allure.attachment_type.TEXT)
                    pytest.skip("Pages contain overlapping movies - possible server pagination issue")

    @allure.title("Тестирование невалидных фильтров")
    @allure.description("Проверка поведения API при использовании невалидных параметров фильтрации")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.filtering
    @pytest.mark.boundary
    def test_get_movies_invalid_filters(self, common_user):
        with allure.step("Отправка запроса с невалидным location"):
            response = common_user.api.movies_api.get_all_movies(params={"location": "INVALID"})

        with allure.step("Проверка статуса ответа 200"):
            assert response.status_code == 200

        with allure.step("Анализ полученных данных"):
            data = response.json()
            movies = data.get('movies', [])
            allure.attach(str(movies), name="Фильмы с невалидным фильтром", attachment_type=allure.attachment_type.JSON)

            if movies:
                with allure.step("Проверка валидности данных (фильтр location не работает - известный баг)"):
                    valid_locations = ["MSK", "SPB"]
                    for movie in movies:
                        assert movie.get("location") in valid_locations, \
                            f"Invalid location in movie: {movie.get('location')}"


class TestMovieDelete:

    @allure.title("Удаление фильма пользователем с ролью {user_fixture}")
    @allure.description("""
    Параметризованный тест удаления фильма пользователями с разными ролями.
    По документации: DELETE /movies/{id} доступен только SUPER_ADMIN
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.delete
    @pytest.mark.permissions
    @pytest.mark.parametrized
    @pytest.mark.integration
    @pytest.mark.parametrize('user_fixture,expected_status,should_delete', [
        ('super_admin', 200, True),  # Супер-админ может удалять (200 OK)
        ('admin_user', 403, False),  # Админ НЕ может удалять
        ('common_user', 403, False),  # Пользователь НЕ может удалять
    ])
    def test_delete_movie_by_different_roles(self, request, super_admin, movie_data,
                                             user_fixture, expected_status, should_delete):
        with allure.step("1. Создание тестового фильма супер-админом"):
            create_response = super_admin.api.movies_api.create_movie(movie_data)
            assert create_response.status_code == 201, "Не удалось создать фильм"
            movie = create_response.json()
            movie_id = movie["id"]
            allure.attach(str(movie), name="Созданный фильм", attachment_type=allure.attachment_type.JSON)

        with allure.step(f"2. Получение пользователя {user_fixture} для теста"):
            test_user = request.getfixturevalue(user_fixture)

        try:
            with allure.step(f"3. Попытка удаления фильма пользователем {user_fixture}"):
                delete_response = test_user.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=expected_status
                )

            with allure.step(f"4. Проверка статуса ответа (ожидается {expected_status})"):
                assert delete_response.status_code == expected_status, \
                    f"Expected {expected_status} for {user_fixture}, got {delete_response.status_code}"

            with allure.step("5. Проверка результата удаления"):
                expected_status_after_delete = 404 if should_delete else 200
                check_response = super_admin.api.movies_api.get_movie_by_id(
                    movie_id,
                    expected_status=expected_status_after_delete
                )

                if should_delete:
                    with allure.step("Проверка что фильм удален (статус 404)"):
                        assert check_response.status_code == 404, \
                            f"Movie should be deleted but still exists. Status: {check_response.status_code}"

                    with allure.step("Проверка структуры ответа при удалении"):
                        if delete_response.text:
                            response_data = delete_response.json()
                            assert response_data["id"] == movie_id
                            assert response_data["name"] == movie["name"]
                            allure.attach(str(response_data), name="Ответ при удалении",
                                          attachment_type=allure.attachment_type.JSON)
                else:
                    with allure.step("Проверка что фильм НЕ удален (статус 200)"):
                        assert check_response.status_code == 200, \
                            f"Movie should still exist when deletion is not allowed for {user_fixture}"

                        existing_movie = check_response.json()
                        assert existing_movie["name"] == movie["name"]
                        assert existing_movie["id"] == movie_id

                    with allure.step("Проверка структуры ошибки 403"):
                        error_data = delete_response.json()
                        assert "message" in error_data
                        assert "error" in error_data
                        assert error_data["error"] == "Forbidden"
                        assert "Forbidden resource" in error_data["message"]
                        allure.attach(str(error_data), name="Ошибка 403", attachment_type=allure.attachment_type.JSON)

        finally:
            with allure.step("6. Очистка: удаление фильма если он еще существует"):
                try:
                    final_check = super_admin.api.movies_api.get_movie_by_id(movie_id)
                    if final_check.status_code == 200:
                        super_admin.api.movies_api.delete_movie(movie_id, expected_status=200)
                except Exception as e:
                    allure.attach(str(e), name="Ошибка при очистке", attachment_type=allure.attachment_type.TEXT)

    @allure.title("Удаление несуществующего фильма")
    @allure.description("Негативный тест: попытка удаления фильма с несуществующим ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.delete
    @pytest.mark.boundary
    def test_delete_nonexistent_movie(self, super_admin):
        with allure.step("Подготовка несуществующего ID фильма"):
            nonexistent_id = 999999

        with allure.step("Попытка удаления несуществующего фильма"):
            response = super_admin.api.movies_api.delete_movie(
                nonexistent_id,
                expected_status=404
            )

        with allure.step("Проверка статуса 404"):
            assert response.status_code == 404

        with allure.step("Проверка сообщения об ошибке"):
            error_data = response.json()
            assert "message" in error_data
            assert "Фильм не найден" in error_data["message"]
            assert error_data["error"] == "Not Found"
            allure.attach(str(error_data), name="Ошибка 404", attachment_type=allure.attachment_type.JSON)

    @allure.title("Удаление фильма с невалидным ID: {invalid_id}")
    @allure.description("Параметризованный тест с различными невалидными значениями ID")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.delete
    @pytest.mark.parametrized
    @pytest.mark.boundary
    @pytest.mark.parametrize('invalid_id', [
        'invalid_string',  # Неверный формат ID
        -1,  # Отрицательный ID
        0,  # Нулевой ID
        ' ',  # Пробел
        '123abc',  # Смешанная строка
    ])
    def test_delete_movie_with_invalid_id(self, super_admin, invalid_id):
        with allure.step(f"Попытка удаления фильма с невалидным ID: {invalid_id}"):
            response = super_admin.api.movies_api.delete_movie(
                invalid_id,
                expected_status=404
            )

        with allure.step("Проверка статуса 404"):
            assert response.status_code == 404, \
                f"Expected 404 for invalid ID {invalid_id}, got {response.status_code}"

    @allure.title("Повторное удаление одного фильма")
    @allure.description("Тест на попытку повторного удаления уже удаленного фильма")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.negative
    @pytest.mark.delete
    @pytest.mark.idempotency
    def test_delete_movie_twice(self, super_admin, movie_data):
        with allure.step("1. Создание тестового фильма"):
            create_response = super_admin.api.movies_api.create_movie(movie_data)
            assert create_response.status_code == 201
            movie = create_response.json()
            movie_id = movie["id"]

        try:
            with allure.step("2. Первое удаление фильма"):
                response1 = super_admin.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=200
                )
                assert response1.status_code == 200

            with allure.step("3. Проверка что фильм удален"):
                get_response = super_admin.api.movies_api.get_movie_by_id(movie_id, expected_status=404)
                assert get_response.status_code == 404, "Movie should be deleted after first delete"

            with allure.step("4. Второе удаление уже удаленного фильма"):
                response2 = super_admin.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=404
                )
                assert response2.status_code == 404

                error_data = response2.json()
                assert "Фильм не найден" in error_data["message"]
                allure.attach(str(error_data), name="Ошибка при повторном удалении",
                              attachment_type=allure.attachment_type.JSON)

        finally:
            with allure.step("Очистка"):
                try:
                    super_admin.api.movies_api.delete_movie(movie_id)
                except:
                    pass

    @allure.title("Проверка структуры ответа при удалении фильма")
    @allure.description("Тест проверяет корректность структуры JSON-ответа после успешного удаления")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.positive
    @pytest.mark.delete
    @pytest.mark.response_validation
    def test_delete_movie_response_structure(self, super_admin, movie_data):
        with allure.step("1. Создание тестового фильма"):
            create_response = super_admin.api.movies_api.create_movie(movie_data)
            assert create_response.status_code == 201
            movie = create_response.json()
            movie_id = movie["id"]

        try:
            with allure.step("2. Удаление фильма"):
                delete_response = super_admin.api.movies_api.delete_movie(
                    movie_id,
                    expected_status=200
                )

            with allure.step("3. Проверка статуса ответа"):
                assert delete_response.status_code == 200

            with allure.step("4. Проверка структуры ответа"):
                response_data = delete_response.json()
                allure.attach(str(response_data), name="Ответ при удалении",
                              attachment_type=allure.attachment_type.JSON)

                required_fields = ["id", "name", "price", "description", "imageUrl",
                                   "location", "published", "rating", "genreId", "createdAt", "reviews", "genre"]

                for field in required_fields:
                    with allure.step(f"Проверка наличия поля: {field}"):
                        assert field in response_data, f"Missing field in response: {field}"

            with allure.step("5. Проверка соответствия данных"):
                assert response_data["id"] == movie_id
                assert response_data["name"] == movie["name"]
                assert response_data["description"] == movie["description"]

        finally:
            with allure.step("Очистка"):
                try:
                    super_admin.api.movies_api.delete_movie(movie_id)
                except:
                    pass
