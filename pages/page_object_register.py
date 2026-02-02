import allure

from playwright.sync_api import Page
from pages.page_object_basepage import BasePage


class CinescopRegisterPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)
        self.url = f'{self.home_url}register'

        # Локаторы элементов

        self.full_name_input = "input[name='fullName']"
        self.email_input = "input[name='email']"
        self.password_input = "input[name='password']"
        self.repeat_password_input = "input[name='passwordRepeat']"

        self.register_button = "button[type='submit']"
        self.sign_button = "a[href='/login' and text()='Войти']"


    # Локальный action методы
    def open(self):
        self.open_url(self.url)

    def register(self, full_name: str, email: str, password: str, confirm_password: str):
        self.enter_text_to_element(self.full_name_input, full_name)
        self.enter_text_to_element(self.email_input, email)
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.repeat_password_input, confirm_password)

        self.click_element(self.register_button)

    def assert_was_redirect_to_login_page(self):
        self.wait_redirect_for_url(f'{self.home_url}login')

    def assert_allert_was_pop_up(self):
        self.check_pop_up_element_with_text('Подтвердите свою почту')
