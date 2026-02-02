import allure
from playwright.sync_api import Page
from pages.page_object_main import PageAction





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

