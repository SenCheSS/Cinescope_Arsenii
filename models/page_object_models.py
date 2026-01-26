import allure

from playwright.sync_api import Page


class PageAction:
    def __init__(self, page: Page):
        self.page = page

    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str) -> None:
        self.page.wait_for_url(url)
        assert self.page.url == url, 'Редирект на домашнюю страницу не произошел'

    @allure.step("Проверка, что текущий URL содержит: {expected_path}")
    def assert_url_contains(self,expected_path: str):
        assert expected_path in self.page.url, f"URL {self.page.url} не содержит {expected_path}"

    @allure.step("Проверка, что текущий URL не содержит: {not_expected_path}")
    def assert_url_not_contains(self, not_expected_path: str):
        assert not_expected_path not in self.page.url, f"URL {self.page.url} содержит {not_expected_path}"

    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

    @allure.step("Ожидание появления или исчезновения элемента: {locator}, state = {state}")
    def wait_for_element(self, locator: str, state: str = 'visible'):
        self.page.locator(locator).wait_for(state=state)

    @allure.step("Скриншот текущей страницы")
    def make_screenshot_and_attach_to_allure(self):
        screenshot_path = 'screenshot.png'
        self.page.screenshot(path=screenshot_path, full_page=True)  # full_page=True для скриншота всей страницы

        # Прикрепление скриншота к Allure-отчёту
        with open(screenshot_path, "rb") as file:
            allure.attach(file.read(), name="Screenshot after redirect", attachment_type=allure.attachment_type.PNG)

    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:
        with allure.step("Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text)
            # Ждем появления элемента
            notification_locator.wait_for(state="visible")
            assert notification_locator.is_visible(), f"Уведомление с текстом {text} не появилось"

        with allure.step("Проверка исчезновения алерта с текстом: '{text}'"):
            # Ждем, пока алерт исчезнет
            notification_locator.wait_for(state="hidden")
            assert notification_locator.is_visible() == False, f"Уведомление с текстом {text} не исчезло"
            return True

    @allure.step("Очистка поля: {locator}")
    def clear_field(self, locator: str):
            self.page.fill(locator, "")

    @allure.step("Проверка видимости элемента: {locator}")
    def is_element_visible(self, locator: str) -> bool:
        return self.page.locator(locator).is_visible()

    @allure.step("Проверка наличия текста '{text}' на странице")
    def is_text_present(self, text: str) -> bool:
        """Проверяет, присутствует ли текст на странице"""
        try:
            return self.page.locator(f"text={text}").is_visible()
        except:
            return False

    @allure.step("Получение текста валидационного сообщения для поля: {locator}")
    def get_validation_message(self, locator: str) -> str:
        """Получает текст валидационного сообщения рядом с полем"""
        # Ищем элемент с классом text-red-500 после поля ввода
        validation_locator = f"{locator} + .text-red-500"
        try:
            if self.page.locator(validation_locator).is_visible():
                return self.page.locator(validation_locator).text_content()
        except:
            pass
        return ""

    @allure.step("Проверка валидационного сообщения для поля: {locator}")
    def assert_validation_message(self, locator: str, expected_text: str = None):
        """
        Проверяет наличие валидационного сообщения.
        Если передан expected_text - проверяет конкретный текст.
        """
        validation_locator = f"{locator} + .text-red-500"

        # Ждем появления элемента валидации
        try:
            self.page.locator(validation_locator).wait_for(state="visible", timeout=5000)
        except:
            pass

        is_visible = self.page.locator(validation_locator).is_visible()
        assert is_visible, f"Валидационное сообщение для поля {locator} не отображается"

        if expected_text:
            actual_text = self.page.locator(validation_locator).text_content()
            assert expected_text in actual_text, \
                f"Ожидался текст: '{expected_text}', получен: '{actual_text}'"


class BasePage(PageAction): #Базова логика доступная для всех страниц на сайте
    def __init__(self, page:Page):
        super().__init__(page)
        self.home_url = 'https://dev-cinescope.coconutqa.ru/'

        #Общие локаторы для всех страниц на сайте
        self.home_button = "a[href='/' and text()='Cinescope']"
        self.all_movies_button = "a[href='/movies' and text()='Все фильмы']"

    @allure.step("Переход на главную страницу, из шапки сайта")
    def go_to_home_page(self):
        self.click_element(self.home_button)
        self.wait_redirect_for_url(self.home_url)

    @allure.step("Переход на страницу 'Все фильмы, из шапки сайта'")
    def go_to_all_movies(self):
        self.click_element(self.all_movies_button)
        self.wait_redirect_for_url(f'{self.home_url}movies')

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

    def login(self, email: str, password: str):
        self.enter_text_to_element(self.password_input, password)
        self.enter_text_to_element(self.email_input, email)
        self.click_element(self.login_button)

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