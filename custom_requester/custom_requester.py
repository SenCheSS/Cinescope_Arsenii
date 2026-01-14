import json
from typing import Optional, Type
from pydantic import ValidationError
import logging
import os


class CustomRequester:
    """Кастомный реквестер для стандартизации и упрощения отправки HTTP-запросов."""
    base_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    def __init__(self, session, base_url):
        """
        Инициализация кастомного реквестера.
        :param session: Объект requests.Session.
        :param base_url: Базовый URL API.
        """
        self.session = session
        self.base_url = base_url
        self.headers = self.base_headers.copy()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

    def send_request(self, method, endpoint, data=None, params=None,
                     expected_status=200, need_logging=True,
                     response_model: Optional[Type] = None):
        """
        Универсальный метод для отправки запросов.
        :param method: HTTP метод (GET, POST, PUT, DELETE и т.д.).
        :param endpoint: Эндпоинт (например, "/login").
        :param data: Тело запроса (JSON-данные).
        :param params: Query параметры.
        :param expected_status: Ожидаемый статус-код или список статусов.
        :param need_logging: Флаг для логирования (по умолчанию True).
        :param response_model: Pydantic модель для валидации ответа (опционально).
        :return: Объект ответа requests.Response.
        """
        url = f'{self.base_url}{endpoint}'
        response = self.session.request(
            method,
            url,
            json=data,
            params=params,
            headers=self.headers)
        if need_logging:
            self.log_request_and_response(response)

        # Поддержка как одиночного статуса, так и списка статусов
        if isinstance(expected_status, int):
            expected_statuses = [expected_status]
        else:
            expected_statuses = expected_status

        if response.status_code not in expected_statuses:
            raise ValueError(
                f'Unexpected status code: {response.status_code}. '
                f'Expected: {expected_statuses}. '
                f'Response: {response.text[:200]}'
            )

        return response

    def _update_session_headers(self, **kwargs):
        """
        Обновление заголовков сессии.
        :param session: Объект requests.Session, предоставленный API-классом.
        :param kwargs: Дополнительные заголовки.
        """
        self.headers.update(kwargs)                # Обновляем базовые заголовки
        self.session.headers.update(self.headers)  # Обновляем заголовки в текущей сессии

    def log_request_and_response(self, response):
        try:
            request = response.request
            GREEN = '\033[32m'
            RED = '\033[31m'
            RESET = '\033[0m'
            headers = " \\\n".join([f"-H '{header}: {value}'" for header, value in request.headers.items()])
            full_test_name = f"pytest {os.environ.get('PYTEST_CURRENT_TEST', '').replace(' (call)', '')}"

            body = ""
            if hasattr(request, 'body') and request.body is not None:
                if isinstance(request.body, bytes):
                    body = request.body.decode('utf-8')
                body = f"-d '{body}' \n" if body != '{}' else ''

            self.logger.info(f"\n{'=' * 40} REQUEST {'=' * 40}")
            self.logger.info(
                f"{GREEN}{full_test_name}{RESET}\n"
                f"curl -X {request.method} '{request.url}' \\\n"
                f"{headers} \\\n"
                f"{body}"
            )

            response_data = response.text
            try:
                response_data = json.dumps(json.loads(response.text), indent=4, ensure_ascii=False)
            except json.JSONDecodeError:
                pass

            self.logger.info(f"\n{'=' * 40} RESPONSE {'=' * 40}")
            if not response.ok:
                self.logger.info(
                    f"\tSTATUS_CODE: {RED}{response.status_code}{RESET}\n"
                    f"\tDATA: {RED}{response_data}{RESET}"
                )
            else:
                self.logger.info(
                    f"\tSTATUS_CODE: {GREEN}{response.status_code}{RESET}\n"
                    f"\tDATA:\n{response_data}"
                )
            self.logger.info(f"{'=' * 80}\n")
        except Exception as e:
            self.logger.error(f"\nLogging failed: {type(e)} - {e}")
