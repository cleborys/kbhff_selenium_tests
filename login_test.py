import pytest
from fixtures import *

from navigation import *
from check_email import *

import time


## Test specification number 1
#def test_unverifiedUserFirstLogin(driver, unverified_user_via_medlemshjaelp):
#    user = unverified_user_via_medlemshjaelp
#
#    try_login(driver, user["email"], user["password"])
#    assert_current_page_is("bekraeft_konto", driver)
#
#    mail = get_latest_mail_to(user["email"], expect_title="Aktiver din konto hos KBHFF", retry=5)
#    token = get_activation_code_from_email(mail.body)
#    fill_form_field(token, driver, form_id="input_verification_code")
#    submit_form(driver)
#    assert_current_page_is("opret_password", driver)
#
#    fill_form_field(user["password"], driver, form_id="input_new_password")
#    fill_form_field(user["password"], driver, form_id="input_confirm_password")
#    submit_form(driver)
#    assert_current_page_is("kvittering", driver)
#
#    navigate_to_page("login", driver)
#    assert_current_page_is("login", driver)
#    assert get_form_field_value(driver, form_id="input_username") == user["email"]


# Test specification number 2
def test_unverifiedUserFirstLoginDuplicateTab(driver, unverified_user_via_medlemshjaelp):
    user = unverified_user_via_medlemshjaelp

    navigate_to_page("login", driver)
    first_tab = driver.current_window_handle

    navigate_to_page("login", driver, new_tab=True)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    second_tab = [x for x in driver.window_handles if x != first_tab][0]

    driver.switch_to.window(first_tab)
    try_login(driver, user["email"], user["password"])
    assert_current_page_is("bekraeft_konto", driver)
    mail = get_latest_mail_to(user["email"], expect_title="Aktiver din konto hos KBHFF", retry=5)
    token = get_activation_code_from_email(mail.body)

    driver.switch_to.window(second_tab)
    navigate_to_page("bekraeft_konto", driver)
    assert_current_page_is("bekraeft_konto", driver)
    fill_form_field(token, driver, form_id="input_verification_code")
    submit_form(driver)
    assert_current_page_is("opret_password", driver)
    fill_form_field(user["password"], driver, form_id="input_new_password")
    fill_form_field(user["password"], driver, form_id="input_confirm_password")
    submit_form(driver)
    assert_current_page_is("kvittering", driver)
    navigate_to_page("login", driver)
    assert_current_page_is("login", driver)
    assert get_form_field_value(driver, form_id="input_username") == user["email"]

    driver.switch_to.window(first_tab)
    fill_form_field(token, driver, form_id="input_verification_code")
    submit_form(driver)
    assert_current_page_is("login", driver)
    assert get_form_field_value(driver, form_id="input_username") == user["email"]
    assert_text_on_page("Din konto er allerede aktiveret!", driver)
