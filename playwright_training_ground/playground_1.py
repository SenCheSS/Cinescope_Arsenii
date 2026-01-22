from playwright.sync_api import sync_playwright    #Строка необходимая Python для работы с браузером
import time

from pytest_playwright.pytest_playwright import browser

"""
# Создаем экземпляр Playwright и запускаем его
playwright = sync_playwright().start()

# Далее, используя объект playwright, можно запускать браузер и работать с ним
browser = playwright.chromium.launch(headless=False, slow_mo=50)
page = browser.new_page()
page.goto('https://dev-cinescope.coconutqa.ru/')
time.sleep(10)  # Сделаем sleep иначе браузер сразу закроется перейдя к следующим строкам

# После выполнения необходимых действий, следует явно закрыть браузер
browser.close()

# И остановить Playwright, чтобы освободить ресурсы
playwright.stop()
"""
# Тест мультибраузерности
'''
def test_multiple_browsers():
    with sync_playwright() as p:
        chromium_browser = p.chromium.launch(headless=False, slow_mo=50)
        firefox_browser = p.firefox.launch(headless=False, slow_mo=50)

        chromium_page = chromium_browser.new_page()
        firefox_page = firefox_browser.new_page()

        chromium_page.goto('https://dev-cinescope.coconutqa.ru/')
        firefox_page.goto("https://www.google.com")

        time.sleep(10)

        chromium_browser.close()
        firefox_browser.close()
'''
# Создание PAGE
'''
with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context()
    page1 = context.new_page() #Первая страница (вкладка)
    page2 = context.new_page() #Вторая страница

    # ...работа с page1 и page2

    context.close()
    browser.close()
'''
#Делаем несколько контекстов и пейджей

def test_some_entities():
    with sync_playwright() as p:
        browser1 = p.chromium.launch(headless=False)

        context1_1 = browser1.new_context()
        context1_2 = browser1.new_context()

        page1_1_1 = context1_1.new_page()
        page1_1_2 = context1_1.new_page()
        page1_2_1 = context1_2.new_page()
        page1_2_2 = context1_2.new_page()

        page1_1_1.goto("https://www.example.com")
        page1_1_2.goto("https://www.google.com")
        page1_2_1.goto("https://www.wikipedia.org")
        page1_2_2.goto("https://www.yandex.ru")

        time.sleep(10)

        page1_1_1.close()
        page1_1_2.close()
        page1_2_1.close()
        page1_2_2.close()
