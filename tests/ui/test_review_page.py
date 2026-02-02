import allure
import pytest
from pages.page_object_reviewpage import ReviewPage


@allure.epic("Тестирование UI")
@allure.feature("Создание отзывов администратором")
@pytest.mark.ui
class TestAdminReview:

    @allure.title("Админ создает и удаляет отзыв")
    def test_admin_review_flow_full(self, review_page_for_admin: ReviewPage):
        """Полный тест с использованием всех методов ReviewPage"""
        review_page = review_page_for_admin

        # Проверяем начальное состояние
        review_page.assert_review_form_visible()
        initial_count = review_page.get_reviews_count()

        # Создаем уникальный отзыв
        review_text = review_page.create_unique_review(
            base_text="Отличный фильм! Тестовый отзыв от администратора",
            rating=4
        )
        review_page.assert_review_created_successfully()
        review_page.wait_for_page_load()
        # Проверяем, что отзыв добавился
        assert review_page.has_review_with_text(review_text), \
            f"Созданный отзыв не найден: {review_text}"
        new_count = review_page.get_reviews_count()
        assert new_count == initial_count + 1, \
            f"Количество отзывов не изменилось: было {initial_count}, стало {new_count}"
        # Проверяем ограничение "один отзыв"
        # После создания форма должна исчезнуть
        try:
            review_page.assert_review_form_visible()
            assert False, "Форма отзыва все еще видна после создания отзыва"
        except AssertionError:
            # Это ожидаемое поведение - форма не видна
            pass
        # Удаляем отзыв
        review_page.delete_review(0)
        review_page.assert_review_deleted_successfully()
        review_page.wait_for_page_load()
        # Проверяем удаление
        assert not review_page.has_review_with_text(review_text), \
            f"Отзыв все еще присутствует после удаления: {review_text}"
        final_count = review_page.get_reviews_count()
        assert final_count == initial_count, \
            f"Количество отзывов не вернулось к исходному: было {initial_count}, стало {final_count}"
        # Проверяем, что форма снова доступна
        review_page.assert_review_form_visible()
        # Финальный скриншот
        review_page.make_screenshot_and_attach_to_allure("Тест завершен")
