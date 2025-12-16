'''from constants.constants import AUTH_BASE_URL
from custom_requester.custom_requester import CustomRequester

class UserAPI(CustomRequester):
    """Класс для работы с API пользователей."""
    def __init__(self, session):
        super().__init__(session=session, base_url=AUTH_BASE_URL)
        self.session = session

    def get_user_info(self, user_id, expected_status=200):
        """
        Получение информации о пользователе.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="GET",
            endpoint=f'/user/{user_id}',
            expected_status=expected_status
        )

    def delete_user(self, user_id, expected_status=204):
        """
        Удаление пользователя.
        :param user_id: ID пользователя.
        :param expected_status: Ожидаемый статус-код.
        """
        return self.send_request(
            method="DELETE",
            endpoint=f'/user/{user_id}',
            expected_status=expected_status
        )

    def clean_up_user(self, user_id):
        """
        Безопасное удаление пользователя для очистки после тестов.
        Не выбрасывает исключение если пользователь уже удален.
        :param user_id:
        """
        try:
            self.delete_user(user_id, expected_status=204)
            print(f'Пользователь {user_id} успешно удален')
        except ValueError as e:
            if '404' in str(e):
                print(f'Пользователь {user_id} уже удален')
            else:
                print(f'Ошибка при удалении пользователя {user_id}: {e}')'''