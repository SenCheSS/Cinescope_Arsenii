import allure
import pytest

from playwright.sync_api import Page, sync_playwright
from models.page_object_models import CinescopRegisterPage
from utils.data_generator import DataGenerator


@allure.epic("Тестирование UI")
@allure.feature("Тестирование Страницы Register")
@pytest.mark.ui
class TestRegisterPage:
    @allure.title("Проведение успешной регистрации")
    def test_register_by_ui(self):
        with sync_playwright() as playwright:
            # Подготовка данных для регистрации
            random_email = DataGenerator.generate_random_email()
            random_name = DataGenerator.generate_random_name()
            random_password = DataGenerator.generate_random_password()

            browser = playwright.chromium.launch(
                headless=False)  # Запуск браузера headless=False для визуального отображения
            page = browser.new_page()

            register_page = CinescopRegisterPage(page)  # Создаем объект страницы регистрации cinescope
            register_page.open()
            register_page.register(f"PlaywrightTest {random_name}", random_email, random_password,
                                   random_password)  # Выполняем регистрацию

            register_page.assert_was_redirect_to_login_page()  # Проверка редиректа на страницу /login
            register_page.make_screenshot_and_attach_to_allure()  # Прикрепляем скриншот
            register_page.assert_allert_was_pop_up()  # Проверка появления и исчезновения алерта

            # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
            #time.sleep(5)
            browser.close()
