from asyncio import timeout

import allure
import pytest
import time
from playwright.sync_api import Page, sync_playwright

from conftest import browser
from models.page_object_models import CinescopLoginPage


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Login")
@pytest.mark.ui
class TestloginPage:
    @allure.title("Проведение успешного входа в систему")
    def test_login_by_ui(self, registered_user):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(
                headless=False)  # Запуск браузера headless=False для визуального отображения
            page = browser.new_page()
            login_page = CinescopLoginPage(page)  # Создаем объект страницы Login

            login_page.open()
            login_page.login(registered_user.email, registered_user.password)  # Осуществяем вход

            login_page.assert_was_redirect_to_home_page()  # Проверка редиректа на домашнюю страницу
            login_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
            login_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта

            # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
            time.sleep(10)
            browser.close()


@allure.epic('Негативное Тестирование Страницы Login')
@allure.feature('Негативное Тестирование Страницы Login')
@pytest.mark.ui
@pytest.mark.negative
class TestLoginPageNegative:
    @allure.title('Тест авторизации с неправильным паролем')
    def test_login_wrong_password(self, registered_user):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            login_page = CinescopLoginPage(page)
            login_page.open()

            wrong_password = 'Wrong_password_123'
            login_page.login(registered_user.email, wrong_password)

            login_page.assert_error_message_pop_up()
            login_page.assert_stay_on_login_page()

            login_page.make_screenshot_and_attach_to_allure()

            time.sleep(5)
            browser.close()

    @allure.title("Попытка входа с несуществующим пользователем")
    def test_login_with_nonexistent_user(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            login_page = CinescopLoginPage(page)

            login_page.open()
            # Генерируем несуществующие данные
            nonexistent_email = "nonexistent_user@example.com"
            random_password = "RandomPass123"
            login_page.login(nonexistent_email, random_password)

            # Проверяем отображение ошибки
            login_page.assert_error_message_pop_up()
            # Проверяем, что не произошел редирект
            login_page.assert_stay_on_login_page()

            login_page.make_screenshot_and_attach_to_allure()

            time.sleep(5)
            browser.close()

    @allure.title('Тест авторизации с пустыми полями - проверка валидации')
    def test_login_empty_fields_validation(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()
            login_page = CinescopLoginPage(page)
            login_page.open()

            # Пытаемся войти с пустыми полями
            login_page.login("", "")

            # Проверяем, что остались на странице логина
            login_page.assert_stay_on_login_page()

            # Проверяем сообщения валидации под полями
            login_page.assert_validation_messages_displayed()

            # Проверяем конкретные сообщения валидации (если знаете текст)
            login_page.assert_email_validation_displayed()
            login_page.assert_password_validation_displayed()

            # Получаем и логируем текст валидации
            email_validation_text = login_page.get_email_validation_text()
            password_validation_text = login_page.get_password_validation_text()

            allure.attach(
                f"Email валидация: {email_validation_text}\nPassword валидация: {password_validation_text}",
                name="Текст валидационных сообщений",
                attachment_type=allure.attachment_type.TEXT
            )

            login_page.make_screenshot_and_attach_to_allure()

            time.sleep(2)