import allure
import pytest
import time
from playwright.sync_api import Page, sync_playwright
from models.page_object_models import CinescopLoginPage

@allure.epic("Тестирование UI")
@allure.feature("Тестирование Создания Отзыва Администратором")
@pytest.mark.ui
class TestAdminReview:
    @allure.title("Оставление отзыва под админом")
    def test_admin_create_review(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=False)
            page = browser.new_page()

            try:
                # Логинимся
                login_page = CinescopLoginPage(page)
                login_page.open()

                admin_email = 'api1@gmail.com'
                admin_password = 'asdqwe123Q'

                login_page.login(admin_email, admin_password)

                login_page.assert_was_redirect_to_home_page()
                time.sleep(2)

                # Переход к фильму
                details_buttons = page.locator("text=Подробнее")

                if details_buttons.count() == 0:
                    pytest.skip("Не найдены кнопки 'Подробнее' на странице")

                details_buttons.first.click()
                page.wait_for_load_state("networkidle")
                time.sleep(2)

                # Оставляем отзыв
                review_textarea = page.locator("textarea")
                review_textarea.fill("Отличный фильм! Тестовый отзыв от администратора.")

                rating_select = page.locator("select").first
                if rating_select.count() > 0:
                    rating_select.select_option(value="4")
                else:
                    rating_buttons = page.get_by_role('option', name='4')
                    if rating_buttons.count() > 0:
                        rating_buttons.first.click()

                submit_button = page.locator("button:has-text('Отправить')").first
                submit_button.click()

                # Проверяем успешное создание отзыва
                try:
                    page.wait_for_selector("text=Отзыв успешно создан", timeout=5000)
                    success_message = page.locator("text=Отзыв успешно создан")
                    assert success_message.is_visible(), "Сообщение об успехе не появилось"

                except:
                    raise AssertionError('Не появилось сообщение об успешном создании отзыва')

                time.sleep(5)

                login_page.make_screenshot_and_attach_to_allure()

                page.locator('.lucide-more-vertical').first.click()
                page.get_by_role('menuitem', name='Удалить').click()
                page.wait_for_selector("text=Отзыв успешно удален", timeout=5000)
                time.sleep(2)

            finally:
                browser.close()