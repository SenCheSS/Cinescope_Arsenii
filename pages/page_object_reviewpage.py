import allure
import time
from pages.page_object_basepage import BasePage
from playwright.sync_api import Page


class ReviewPage(BasePage):
    def __init__(self, page: Page):
        super().__init__(page)

        # Локаторы
        self.more_details_button = "text=Подробнее"
        self.review_textarea = "textarea"
        self.submit_review_button = "button:has-text('Отправить')"
        self.review_menu_button = ".lucide-more-vertical"
        self.delete_review_option = "[role='menuitem']:has-text('Удалить')"

        self.review_items = "div.p-6.pt-0"
        self.review_text = "div.p-6.pt-0 p"
        self.review_rating = "div.p-6.pt-0 h3"
        self.review_author = "text-xl w-fit"

        # Для поиска оценки
        self.rating_select = "select[name='rating'], select"
        self.rating_combobox = "[role='combobox']"
        self.rating_radio = "input[type='radio'][value]"

        # Сообщения
        self.success_popup = "[role='status']"
        self.success_message_create = "Отзыв успешно создан"
        self.success_message_delete = "Отзыв успешно удален"

        # Страница фильма
        self.movie_page_indicator = "h1, .movie-title, button:has-text('Купить билет')"

    @allure.step("Переход на страницу фильма")
    def go_to_movie_details(self):
        """Переходит на страницу деталей фильма - ИСПРАВЛЕННАЯ ВЕРСИЯ"""
        # Ждем загрузки главной страницы
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(1000)

        # Ищем ВСЕ кнопки "Подробнее"
        details_buttons = self.page.get_by_role("button", name="Подробнее")

        # Если не нашли через role, пробуем через текст
        if details_buttons.count() == 0:
            details_buttons = self.page.locator("text=Подробнее")

        if details_buttons.count() == 0:
            raise Exception("Не найдены кнопки 'Подробнее' на странице")

        print(f"Найдено кнопок 'Подробнее': {details_buttons.count()}")

        # Кликаем на ПЕРВУЮ ВИДИМУЮ кнопку
        for i in range(details_buttons.count()):
            try:
                if details_buttons.nth(i).is_visible(timeout=1000):
                    print(f"Кликаем на кнопку #{i + 1}")
                    details_buttons.nth(i).click()
                    break
            except:
                continue
        else:
            # Если ни одна не видна, кликаем на первую
            print("Ни одна кнопка не видна, кликаем на первую")
            details_buttons.first.click()

        # Ждем перехода на страницу фильма
        self.page.wait_for_url("**/movies/**", timeout=10000)
        self.page.wait_for_load_state("networkidle")
        self.page.wait_for_timeout(2000)

        current_url = self.page.url
        print(f"Успешно перешли на: {current_url}")

        if "/movies/" not in current_url:
            raise Exception(f"Не удалось перейти на страницу фильма. Текущий URL: {current_url}")

    @allure.step("Создание отзыва")
    def create_review(self, review_text: str, rating: int = 5):
        """Создает отзыв с указанным текстом и оценкой"""
        self.page.locator(self.review_textarea).first.wait_for(state="visible", timeout=5000)
        self.enter_text_to_element(self.review_textarea, review_text)       # Заполняем текстовое поле
        self._select_rating(rating)     # Выбираем оценку
        self.expect_element_to_be_visible(self.submit_review_button)        # Проверяем, что кнопка отправки доступна
        self.click_element(self.submit_review_button)       # Отправляем форму
        self.page.wait_for_load_state("networkidle")        # Ждем ответа от сервера

    def _select_rating(self, rating: int):
        """Выбирает оценку"""
        rating_value = str(rating)

        # Ждем элементы выбора оценки
        try:
            self.page.locator("select, [role='combobox']").first.wait_for(state="visible", timeout=5000)
        except:
            pass

        # 1. Если есть select элемент
        select_elements = self.page.locator("select")
        if select_elements.count() > 0:
            select_elements.first.select_option(value=rating_value)
            return

        # 2. Ищем другие элементы
        rating_button = self.page.get_by_role('option', name=rating_value)
        if rating_button.count() > 0:
            rating_button.first.click()

    @allure.step("Проверка успешного создания отзыва")
    def assert_review_created_successfully(self):
        """Проверяет появление сообщения об успешном создании"""
        self.check_pop_up_element_with_text(self.success_message_create)

    @allure.step("Удаление отзыва")
    def delete_review(self, review_index: int = 0):
        """Удаляет отзыв по индексу"""
        # Используем не-strict подход
        menu_buttons = self.page.locator(self.review_menu_button)

        if menu_buttons.count() == 0:
            raise Exception("Не найдены кнопки меню отзывов")

        if review_index >= menu_buttons.count():
            review_index = 0

        # Проверяем видимость конкретной кнопки, а не всех
        if menu_buttons.nth(review_index).is_visible():
            menu_buttons.nth(review_index).click()

            # Ждем опцию удаления
            delete_option = self.page.locator(self.delete_review_option)
            if delete_option.count() > 0 and delete_option.first.is_visible():
                delete_option.first.click()
            else:
                raise Exception("Опция удаления не найдена")
        else:
            raise Exception(f"Кнопка меню с индексом {review_index} не видна")

    @allure.step("Проверка успешного удаления отзыва")
    def assert_review_deleted_successfully(self):
        """Проверяет появление сообщения об успешном удалении"""
        self.check_pop_up_element_with_text(self.success_message_delete)

    @allure.step("Проверка наличия отзыва с текстом")
    def has_review_with_text(self, text: str, timeout: int = 5000) -> bool:
        """Проверяет, есть ли на странице отзыв с указанным текстом"""
        try:
            review_with_text = self.page.locator(f"{self.review_text}:has-text('{text}')")
            review_with_text.wait_for(state="visible", timeout=timeout)
            return review_with_text.count() > 0
        except:
            return False

    @allure.step("Создание уникального отзыва")
    def create_unique_review(self, base_text: str = None, rating: int = 5) -> str:
        """
        Создает отзыв с уникальным текстом
        Возвращает текст созданного отзыва
        """
        if base_text is None:
            base_text = "Тестовый отзыв"

        unique_id = f"_{int(time.time())}"  # timestamp
        unique_review = f"{base_text} {unique_id}"

        self.create_review(unique_review, rating)
        return unique_review

    @allure.step("Проверка наличия формы отзыва")
    def assert_review_form_visible(self):
        """Проверяет, что форма отзыва отображается на странице"""
        assert self.page.locator(self.review_textarea).is_visible(), \
            "Текстовое поле для отзыва не найдено"
        assert self.page.locator(self.submit_review_button).is_visible(), \
            "Кнопка отправки отзыва не найдена"

    @allure.step("Получение количества отзывов")
    def get_reviews_count(self) -> int:
        """Возвращает количество отзывов на странице"""
        return self.page.locator(self.review_items).count()

    @allure.step("Получение текста первого отзыва")
    def get_first_review_text(self) -> str:
        """Возвращает текст первого отзыва"""
        try:
            return self.page.locator(self.review_text).first.text_content()
        except:
            return ""