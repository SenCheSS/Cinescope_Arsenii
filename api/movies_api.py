from constants.constants import MOVIES_BASE_URL
from custom_requester.custom_requester import CustomRequester


class MoviesAPI(CustomRequester):

    def __init__(self, session):
        super().__init__(session, MOVIES_BASE_URL)

    def get_all_movies(self, params=None, expected_status=200, **kwargs):
        """GET /movies - Получение списка всех фильмов"""
        return self.send_request(
            method="GET",
            endpoint="/movies",
            params=params,
            expected_status=expected_status,
            **kwargs
        )

    def get_movie_by_id(self, movie_id, expected_status=200):
        """GET /movies/{id} - Получение фильма по ID"""
        return self.send_request(
            method="GET",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )

    def create_movie(self, movie_data, expected_status=201):
        """POST /movies - Создание нового фильма"""
        return self.send_request(
            method="POST",
            endpoint="/movies",
            data=movie_data,
            expected_status=expected_status
        )

    def update_movie(self, movie_id, update_data, expected_status=200):
        """PATCH /movies/{id} - Обновление фильма"""
        return self.send_request(
            method="PATCH",
            endpoint=f"/movies/{movie_id}",
            data=update_data,
            expected_status=expected_status
        )

    def delete_movie(self, movie_id, expected_status=200):
        """DELETE /movies/{id} - Удаление фильма"""
        return self.send_request(
            method="DELETE",
            endpoint=f"/movies/{movie_id}",
            expected_status=expected_status
        )
