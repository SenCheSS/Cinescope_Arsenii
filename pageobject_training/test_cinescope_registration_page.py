import time
from playwright.sync_api import sync_playwright

from alfa_page_object_models import CinescopRegisterPage
from utils.data_generator import DataGenerator


def test_register_by_ui():
    with sync_playwright() as playwright:
        random_email = DataGenerator.generate_random_email()
        random_name = DataGenerator.generate_random_name()
        random_password = DataGenerator.generate_random_password()

        # Запуск браузера
        browser = playwright.chromium.launch(headless=False)  # headless=False для визуального отображения
        page = browser.new_page()

        # Создаем объект страницы регистрации cinescope
        register_page = CinescopRegisterPage(page)

        # Открываем страницу
        register_page.open()
        register_page.register(f"PlaywrightTest {random_name}", random_email, random_password, random_password)

        # Проверка редиректа на страницу /login
        register_page.wait_redirect_to_login_page()

        # Проверка появления и исчезновения алерта
        register_page.check_allert()

        # Пауза для визуальной проверки (нужно удалить в реальном тестировании)
        time.sleep(5)

        # Закрываем браузер
        browser.close()