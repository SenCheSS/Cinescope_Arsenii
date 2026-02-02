import allure
from playwright.sync_api import Page
from pages.page_object_basepage import BasePage


class CinescopLoginPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f"{self.home_url}login"

        # Локаторы элементов
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.login_button = "button[type='submit']"
        self.register_button = "a[href='/register' and text()='Зарегистрироваться']"

        self.email_validation = "input[name='email'] + .text-red-500"
        self.password_validation = "input[name='password'] + .text-red-500"

        self.validation_messages = ".text-red-500.text-sm.mt-1"

    # Локальные action методы
    def open(self):
        self.open_url(self.url)
        self.wait_for_page_load()

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)
        self.wait_for_text("Вы вошли в аккаунт", timeout=10000)

    def assert_was_redirect_to_home_page(self):
        self.wait_redirect_for_url(self.home_url)

    def assert_stay_on_login_page(self):
        self.assert_url_contains("/login")

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text("Вы вошли в аккаунт")

    def assert_error_message_pop_up(self):
        self.check_pop_up_element_with_text("Неверная почта или пароль")

    @allure.step("Проверка валидации email поля")
    def assert_email_validation_displayed(self, expected_text: str = None):
        """Проверяет отображение валидационного сообщения для email"""
        self.assert_validation_message(self.email_input, expected_text)

    @allure.step("Проверка валидации password поля")
    def assert_password_validation_displayed(self, expected_text: str = None):
        """Проверяет отображение валидационного сообщения для пароля"""
        self.assert_validation_message(self.password_input, expected_text)

    @allure.step("Проверка, что отображаются сообщения валидации")
    def assert_validation_messages_displayed(self):
        """Проверяет, что есть хотя бы одно сообщение валидации"""
        validation_elements = self.page.locator(self.validation_messages)
        count = validation_elements.count()
        assert count > 0, "Сообщения валидации не отображаются"

    @allure.step("Получение текста валидации email")
    def get_email_validation_text(self) -> str:
        """Возвращает текст валидационного сообщения для email"""
        return self.get_validation_message(self.email_input)

    @allure.step("Получение текста валидации пароля")
    def get_password_validation_text(self) -> str:
        """Возвращает текст валидационного сообщения для пароля"""
        return self.get_validation_message(self.password_input)