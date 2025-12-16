from api.api_manager import ApiManager

class User:
    def __init__(self, email: str, password: str, roles: list, api: ApiManager):
        """
        :param email: email пользователя
        :param password: password
        :param roles: список ролей пользователя
        :param api: экземпляр ApiManager
        """
        self.email = email
        self.password = password
        self.roles = roles
        self.api = api

    @property
    def creds(self):
        """Возвращаем кортеж (email, password)"""
        return self.email, self.password