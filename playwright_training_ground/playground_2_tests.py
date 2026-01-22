from playwright.sync_api import Page,expect
from random import randint
import time
'''
from playwright.sync_api import sync_playwright, Page
from random import randint
import time

def test_some_entities(page):
    page.goto('https://google.com')
    time.sleep(10)
'''
'''
# Локальный таймаут для заполнения поля
# page.fill('input#search', 'Playwright', timeout=5000)

#@pytest.mark.timeout(60000)  # Устанавливаем таймаут для теста 60 секунд (1 минута)
#def test_long_running_task(page):
# ... код теста

#page.click('button#submit', timeout=10000)  # Кликаем по кнопке, ожидая не более 10 секунд
#page.fill('input[name="q"]', 'Playwright', timeout=5000)  # Заполняем поле ввода, ожидая не более 5 секунд
#page.goto('https://www.example.com', timeout=60000)  # Переходим по URL, ожидая не более 1 минуты
'''
'''
def test_registration(page: Page):
    page.goto('https://dev-cinescope.coconutqa.ru/register')

    # вариант №1
    username_locator = '[data-qa-id="register_full_name_input"]'
    email_locacor = '[data-qa-id="register_email_input"]'
    password_locator = '[data-qa-id="register_password_input"]'
    repeat_password_locator = '[data-qa-id="register_password_repeat_input"]'

    user_email = f'test_{randint(1, 9999)}@email.qa'

    page.fill(username_locator, 'Жмышенко Валерий Альбертович')
    page.fill(email_locacor, user_email)
    page.fill(password_locator, 'qwerty123Q')
    page.fill(repeat_password_locator, 'qwerty123Q')

    page.click('[data-qa-id="register_submit_button"]')

    time.sleep(10)
'''

def test_text_box_2(page: Page):
    page.goto('https://demoqa.com/text-box')

    page.fill('#userName', 'testQa')
    page.fill('#userEmail', 'test@qa.com')
    page.fill('#currentAddress', 'Phuket, Thalang 99')
    page.fill('#permanentAddress', 'Mockow, Mashkova 1')

    page.click('button#submit')

    expect(page.locator('#output #name')).to_have_text('Name:testQa')
    expect(page.locator('#output #email')).to_have_text('Email:test@qa.com')
    expect(page.locator('#output #currentAddress')).to_have_text('Current Address :Phuket, Thalang 99')
    expect(page.locator('#output #permanentAddress')).to_have_text('Permananet Address :Moscow, Mashkova 1')

    time.sleep(10)
