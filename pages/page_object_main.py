import allure
from playwright.sync_api import Page, expect


class PageAction:
    def __init__(self, page: Page):
        self.page = page
        self.expect = expect  # Добавляем для явных ожиданий

    # === Основные действия ===
    @allure.step("Переход на страницу: {url}")
    def open_url(self, url: str):
        self.page.goto(url)

    @allure.step("Ввод текста '{text}' в поле '{locator}'")
    def enter_text_to_element(self, locator: str, text: str):
        self.page.fill(locator, text)

    @allure.step("Клик по элементу '{locator}'")
    def click_element(self, locator: str):
        self.page.click(locator)

    @allure.step("Очистка поля: {locator}")
    def clear_field(self, locator: str):
        self.page.fill(locator, "")

    # === Проверки URL ===
    @allure.step("Ожидание загрузки страницы: {url}")
    def wait_redirect_for_url(self, url: str) -> None:
        self.page.wait_for_url(url)
        assert self.page.url == url, f'Редирект на страницу {url} не произошел'

    @allure.step("Проверка, что текущий URL содержит: {expected_path}")
    def assert_url_contains(self, expected_path: str):
        assert expected_path in self.page.url, f"URL {self.page.url} не содержит {expected_path}"

    @allure.step("Проверка, что текущий URL не содержит: {not_expected_path}")
    def assert_url_not_contains(self, not_expected_path: str):
        assert not_expected_path not in self.page.url, f"URL {self.page.url} содержит {not_expected_path}"

    # === Работа с элементами ===
    @allure.step("Получение текста элемента: {locator}")
    def get_element_text(self, locator: str) -> str:
        return self.page.locator(locator).text_content()

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

    # === Ожидания ===
    @allure.step("Ожидание загрузки страницы")
    def wait_for_page_load(self):
        """Ждет полной загрузки страницы"""
        self.page.wait_for_load_state("networkidle")

    @allure.step("Ожидание элемента: {locator}")
    def wait_for_element(self, locator: str, state: str = "visible", timeout: int = 10000):
        """Явное ожидание элемента"""
        self.page.locator(locator).wait_for(state=state, timeout=timeout)

    @allure.step("Ожидание появления элемента: {locator}")
    def expect_element_to_be_visible(self, locator: str, timeout: int = 10000):
        """Ожидает, что элемент станет видимым"""
        self.expect(self.page.locator(locator)).to_be_visible(timeout=timeout)

    @allure.step("Ожидание исчезновения элемента: {locator}")
    def expect_element_to_be_hidden(self, locator: str, timeout: int = 10000):
        """Ожидает, что элемент станет скрытым"""
        self.expect(self.page.locator(locator)).to_be_hidden(timeout=timeout)

    @allure.step("Ожидание текста: {text}")
    def expect_text_to_be_present(self, text: str, timeout: int = 10000):
        """Ожидает появления текста на странице"""
        self.expect(self.page.get_by_text(text)).to_be_visible(timeout=timeout)

    @allure.step("Ожидание URL: {url}")
    def wait_for_url(self, url: str, timeout: int = 10000):
        """Ожидает перехода на конкретный URL"""
        self.page.wait_for_url(url, timeout=timeout)

    @allure.step("Ожидание любого изменения URL")
    def wait_for_navigation(self, timeout: int = 10000):
        """Ожидает навигации на другую страницу"""
        self.page.wait_for_event("load", timeout=timeout)

    @allure.step("Ожидание элемента с текстом: {text}")
    def wait_for_text(self, text: str, timeout: int = 10000):
        """Ожидает появления текста на странице"""
        self.page.get_by_text(text).wait_for(state="visible", timeout=timeout)

    # === Валидация форм ===
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

    # === Всплывающие сообщения ===
    @allure.step("Проверка всплывающего сообщения c текстом: {text}")
    def check_pop_up_element_with_text(self, text: str) -> bool:
        """Только проверка появления (без ожидания исчезновения)"""
        with allure.step(f"Проверка появления алерта с текстом: '{text}'"):
            notification_locator = self.page.get_by_text(text, exact=False)
            notification_locator.first.wait_for(state="visible", timeout=2000)

            if notification_locator.count() == 0:
                raise AssertionError(f"Уведомление с текстом '{text}' не появилось")
            return True

    # === Скриншоты ===
    @allure.step("Скриншот текущей страницы")
    def make_screenshot_and_attach_to_allure(self, screenshot_name: str = None):
        """Делает скриншот и прикрепляет к Allure"""
        # Генерируем имя файла
        if screenshot_name:
            filename = f"screenshot_{screenshot_name.replace(' ', '_')}.png"
        else:
            filename = "screenshot.png"

        # Делаем скриншот
        self.page.screenshot(path=filename, full_page=True)

        # Прикрепляем к отчету
        with open(filename, "rb") as file:
            allure.attach(
                file.read(),
                name=screenshot_name or "Screenshot",
                attachment_type=allure.attachment_type.PNG
            )
