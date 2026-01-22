from playwright.sync_api import Page,expect
import time

def test_web_tables_button_add(page: Page):
    page.goto('https://demoqa.com/webtables')

    page.get_by_role("button", name="Add").click()

    page.wait_for_load_state('load')

    is_visible = page.is_visible('p:has-text("Registration Form")')
    print(is_visible)

    page.fill('input[placeholder="First Name"]', 'FirstName')
    page.fill('#lastName', 'LastName')
    page.fill('#userEmail', 'exampleEmail@ex.com')
    page.fill('#age', '28')
    page.fill('#salary', '500000')
    page.fill('#department', 'it-tech')

    page.click('button#submit')

    time.sleep(10)


def test_practice_form(page: Page):
    page.goto('https://demoqa.com/automation-practice-form')

    page.fill('#firstName', 'FirstName')
    page.fill('#lastName', 'LastName')
    page.fill('#userEmail', 'exmpl@exmpl.com')

    page.get_by_text("Male", exact=True).click()
    page.check('#gender-radio-1')

    page.fill('#userNumber', '1234567890')

    page.locator("#dateOfBirthInput").click()
    dateisequel = page.get_attribute('#dateOfBirthInput', '21 Jan 2026')
    print(dateisequel)

    page.get_by_role("combobox").nth(1).select_option("1997")
    page.get_by_role("option", name="Choose Wednesday, January 1st,").click()


    page.locator(".subjects-auto-complete__value-container").click()
    page.locator('#subjectsInput').fill('Ma')
    page.get_by_text("Maths", exact=True).click()

    page.get_by_text("Music").click()
    page.check('#hobbies-checkbox-3')

    #page.get_by_role("button", name="Select picture").click()

    page.fill('#currentAddress','currentaddress')

    page.locator("#state svg").click()
    page.get_by_text("NCR", exact=True).click()

    page.locator("#city svg").click()
    page.get_by_text("Delhi", exact=True).click()

    footer = page.locator('footer').first
    footer_text = footer.text_content()
    assert '2013-2020 TOOLSQA.COM' in footer_text
    assert 'ALL RIGHTS RESERVED.' in footer_text

    page.click('button#submit')

    time.sleep(10)


def test_radiobutton(page: Page):
    page.goto('https://demoqa.com/radio-button')

    is_enabled_rad_1 = page.get_by_text('Yes').is_enabled()
    print(is_enabled_rad_1)

    is_enabled_rad_2 = page.locator('#impressiveRadio').is_enabled()
    print(is_enabled_rad_2)

    is_enabled_rad_3 = page.get_by_text('No').is_enabled()
    print(is_enabled_rad_3)

    time.sleep(10)


def test_check_box_visibility(page: Page):
    page.goto('https://demoqa.com/checkbox')

    is_visible_1 = page.get_by_text('Home').is_visible()
    print(is_visible_1)
    is_visible_2_1 = page.get_by_text('Desktop').is_visible()
    print(is_visible_2_1)

    page.get_by_role('button', name='Toggle').click()

    is_visible_2_2 = page.get_by_text('Desktop').is_visible()
    print(is_visible_2_2)
    page.wait_for_timeout(2000)


def test_dynamic_properties(page: Page):
    page.goto('https://demoqa.com/dynamic-properties')

    is_visible = page.get_by_text('Visible After 5 Seconds')
    print(is_visible)

    page.wait_for_selector('#visibleAfter', state="visible", timeout=6000)


def test_expect(page: Page):
    page.goto("https://demoqa.com/radio-button")
    yes_radio = page.get_by_role("radio", name="Yes")
    impressive_radio = page.get_by_role("radio", name="Impressive")
    no_radio = page.get_by_role("radio", name="No")

    expect(no_radio).to_be_disabled()  # проверяем, что не доступен
    expect(yes_radio).to_be_enabled()  # проверяем, что доступен
    expect(impressive_radio).to_be_enabled()  # проверяем, что доступен

    page.locator('[for="yesRadio"]').click()  # тут хитрый лейбл не позволяет кликнуть прямо на инпут, обращаемся по лейблу

    expect(yes_radio).to_be_checked()  # проверяем, что отмечен
    expect(impressive_radio).not_to_be_checked()  # проверяем, что не отмечен
