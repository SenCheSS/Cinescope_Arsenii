from playwright.sync_api import Page, expect
from random import randint
import time

def test_codegen(page: Page):
    page.goto("https://demoqa.com/")
    page.locator("path").first.click()
    page.get_by_text("Text Box").click()
    page.get_by_role("textbox", name="Full Name").click()
    page.get_by_role("textbox", name="Full Name").fill("Name_example")
    page.get_by_role("textbox", name="name@example.com").click()
    page.get_by_role("textbox", name="name@example.com").fill("main@example.ru")
    page.get_by_role("textbox", name="Current Address").click()
    page.get_by_role("textbox", name="Current Address").fill("Address")
    page.locator("#permanentAddress").click()
    page.locator("#permanentAddress").fill("address")
    page.get_by_role("button", name="Submit").click()
    expect(page.locator("#name")).to_contain_text("Name:Name_example")
    page.get_by_text("Email:main@example.ru").click()
    expect(page.locator("#email")).to_contain_text("Email:main@example.ru")
    expect(page.locator("#output")).to_contain_text("Current Address :Address")
    expect(page.locator("#output")).to_contain_text("Permananet Address :address")

    time.sleep(10)