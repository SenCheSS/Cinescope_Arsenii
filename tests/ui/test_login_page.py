import allure
import pytest

from playwright.sync_api import Page, sync_playwright
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
            #time.sleep(5)
            browser.close()
