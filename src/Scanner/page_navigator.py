from typing import Optional
import time
import json

from bs4 import BeautifulSoup
from playwright.sync_api import Browser, Page


class PageNavigator:
    def __init__(self, browser: Browser, username: str, password: str, answer: str):
        self.page: Page = browser.new_page()

        self.user_id: str = ""
        self.user_profile: str = ""

        self.username: str = username
        self.password: str = password
        self.answer: str = answer

        self.login_url: str = 'https://www.upwork.com/ab/account-security/login'
        self.best_matches_url: str = 'https://www.upwork.com/nx/find-work/best-matches'

        self.profile_id_url: str = 'https://www.upwork.com/freelancers/api/v1/profile/me/fwh'
        self.profile_extra_info_url: str = 'https://www.upwork.com/freelancers/api/v1/freelancer/profile/'
        self.profile_info_url: str = 'https://www.upwork.com/freelancers/settings/contactInfo'

        self.is_next_step_available: bool = True
        self.logged_in: bool = False

    def _goto_page(self, page_url: str) -> None:
        self.is_next_step_available = True
        try:
            self.page.goto(page_url)
            self.page.wait_for_timeout(3)
        except BaseException:
            self.is_next_step_available = False
            raise ValueError("Can't connect to the page " + page_url)

    def _check_page_correctness(
            self, selector: str, error_message: str) -> None:
        selector_element = self.page.query_selector(selector)
        if selector_element is None:
            self.is_next_step_available = False
            raise ValueError(error_message)

    def goto_login_page(self) -> None:
        self._goto_page(self.login_url)
        self._check_page_correctness(
            'span:has-text("Log in to Upwork")',
            "Login failed. It's not login page")

    def goto_best_matches_page(self) -> None:
        if not self.logged_in:
            return

        time.sleep(3)
        self._goto_page(self.best_matches_url)
        self._check_page_correctness(
            'h2:has-text("Jobs you might like")',
            "It's not Best matches jobs page")

    def goto_profile_info_page(self) -> None:
        if not self.logged_in:
            return

        self._goto_page(self.profile_info_url)

    def goto_profile_extra_info_page(self) -> None:
        if not self.logged_in:
            return

        self._goto_page(self.profile_id_url)

        soup = BeautifulSoup(self.page.content(), 'html.parser')
        profile_info = json.loads(soup.text)
        cipher_id = profile_info['identity']['ciphertext']
        self.user_id = profile_info['identity']['userId']

        self._goto_page(self.profile_extra_info_url + cipher_id
                        + '/details')

        soup = BeautifulSoup(self.page.content(), 'html.parser')
        self.user_profile = json.loads(soup.text)

    def enter_username(self) -> None:
        if not self.is_next_step_available:
            return

        self.page.locator('#login_username').fill(self.username)
        self.page.locator('#login_password_continue').click()

        selector_element = self.page.query_selector(
            'span:has-text("Oops! Username is incorrect.")')
        if selector_element:
            self.is_next_step_available = False
            raise ValueError("Login failed. Wrong username or email")

    def enter_password(self) -> None:
        if not self.is_next_step_available:
            return

        self.page.locator('#login_password').fill(self.password)
        self.page.locator('#login_control_continue').click()

        selector_element = self.page.query_selector(
            'span:has-text("Oops! Password is incorrect.")')
        if selector_element:
            self.is_next_step_available = False
            raise ValueError("Login failed. Wrong password")
        else:
            self.logged_in = True

    def reenter_password(self) -> None:
        if not self.is_next_step_available:
            return

        selector_element = self.page.query_selector(
            'h1:has-text("Re-enter password")')
        if selector_element:
            self.logged_in = False
            self.page.locator(
                '#sensitiveZone_password').fill(self.password)
            self.page.locator('#control_continue').click()

            selector_element = self.page.query_selector(
                'span:has-text("Oops! Password is incorrect.")')
            if selector_element:
                self.is_next_step_available = False
                raise ValueError("Login failed. Wrong password")
            else:
                self.logged_in = True

    def enter_answer(self) -> None:
        if not self.is_next_step_available:
            return

        selector_element = self.page.query_selector(
            'span:has-text("Let\'s make sure it\'s you")')
        if selector_element:
            self.logged_in = False
            self.page.locator('#login_answer').fill(self.answer)
            self.page.locator('#login_control_continue').click()

            selector_element = self.page.query_selector(
                'span:has-text("Oops. Answer is incorrect.")')
            if selector_element:
                self.is_next_step_available = False
                raise ValueError("Login failed. Wrong answer")
            else:
                self.logged_in = True

    def reenter_answer(self) -> None:
        if not self.is_next_step_available:
            return

        selector_element = self.page.query_selector(
            'h2:has-text("Confirm that it\'s you")')
        if selector_element:
            self.logged_in = False
            self.page.locator('#deviceAuth_answer').fill(self.answer)
            self.page.locator('#control_save').click()

            selector_element = self.page.query_selector(
                'span:has-text("Oops! Answer is incorrect.")')
            if selector_element:
                self.is_next_step_available = False
                raise ValueError("Login failed. Wrong password")
            else:
                self.logged_in = True

    def ignore_protection_of_account(self) -> None:
        if not self.is_next_step_available:
            return
        selector_element = self.page.query_selector(
            'span:has-text("Protect your account")')
        if selector_element:
            self.page.click("text=I'll do it later")

    def close_complete_profile(self) -> None:
        if not self.is_next_step_available:
            return
        selector_element = self.page.query_selector(
            'span:has-text("Complete Your Profile")')
        if selector_element:
            self.page.click('text=Close')

    def get_page_content(self) -> Optional[str]:
        self.page.wait_for_timeout(3)
        return self.page.content() if self.logged_in else None

    def get_user_id(self) -> Optional[str]:
        return self.user_id if self.logged_in else None

    def get_user_profile(self) -> Optional[str]:
        return self.user_profile if self.logged_in else None
