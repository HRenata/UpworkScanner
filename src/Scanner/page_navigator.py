import json
import time

from playwright.sync_api import Browser, Page
from bs4 import BeautifulSoup


class PageNavigator:
    def __init__(self, browser: Browser, username: str, password: str, answer: str):
        self.__page: Page = browser.new_page()

        self.__user_id: str = None
        self.__user_profile: str = None

        self.__username: str = username
        self.__password: str = password
        self.__answer: str = answer

        self.__login_url: str = 'https://www.upwork.com/ab/account-security/login'
        self.__best_matches_url: str = 'https://www.upwork.com/nx/find-work/best-matches'

        self.__profile_id_url: str = 'https://www.upwork.com/freelancers/api/v1/profile/me/fwh'
        self.__profile_extra_info_url: str = 'https://www.upwork.com/freelancers/api/v1/freelancer/profile/'
        self.__profile_info_url: str = 'https://www.upwork.com/freelancers/settings/contactInfo'

        self.__is_next_step_available: bool = True
        self.__logged_in: bool = False

    @property
    def username(self) -> str:
        return self.__username

    @property
    def user_profile(self) -> str:
        return self.__user_profile

    def __goto_page(self, page_url: str) -> None:
        self.__is_next_step_available = True
        try:
            self.__page.goto(page_url)
            time.sleep(2)
        except:
            self.__is_next_step_available = False
            raise ValueError("Can't connect to the page " + page_url)

    def __check_page_correctness(self, selector: str, error_message: str) -> None:
        selector_element = self.__page.query_selector(selector)
        if selector_element is None:
            self.__is_next_step_available = False
            raise ValueError(error_message)

    def goto_login_page(self) -> None:
        try:
            self.__goto_page(self.__login_url)
            self.__check_page_correctness('span:has-text("Log in to Upwork")', "Login failed. It's not login page")
        except Exception as e:
            raise e

    def goto_best_matches_page(self) -> None:
        if not self.__logged_in:
            return

        try:
            self.__goto_page(self.__best_matches_url)
            self.__check_page_correctness('h2:has-text("Jobs you might like")', "It's not Best matches jobs page")
        except Exception as e:
            raise e

    def goto_profile_info_page(self) -> None:
        if not self.__logged_in:
            return

        try:
            self.__goto_page(self.__profile_info_url)
        except Exception as e:
            raise e

    def goto_profile_extra_info_page(self) -> None:
        if not self.__logged_in:
            return

        try:
            self.__goto_page(self.__profile_id_url)
        except Exception as e:
            raise e
        else:
            soup = BeautifulSoup(self.__page.content(), 'html.parser')
            profile_info = json.loads(soup.text)
            cipher_id = profile_info['identity']['ciphertext']
            self.__user_id = profile_info['identity']['userId']

            try:
                self.__goto_page(self.__profile_extra_info_url + cipher_id + '/details')
            except Exception as e:
                raise e
            else:
                soup = BeautifulSoup(self.__page.content(), 'html.parser')
                self.__user_profile = json.loads(soup.text)

    def enter_username(self) -> None:
        if not self.__is_next_step_available:
            return

        self.__page.locator('#login_username').fill(self.__username)
        self.__page.locator('#login_password_continue').click()

        selector_element = self.__page.query_selector('span:has-text("Oops! Username is incorrect.")')
        if selector_element:
            self.__is_next_step_available = False
            raise ValueError("Login failed. Wrong username or email")

    def enter_password(self) -> None:
        if not self.__is_next_step_available:
            return

        self.__page.locator('#login_password').fill(self.__password)
        self.__page.locator('#login_control_continue').click()

        selector_element = self.__page.query_selector('span:has-text("Oops! Password is incorrect.")')
        if selector_element:
            self.__is_next_step_available = False
            raise ValueError("Login failed. Wrong password")
        else:
            self.__logged_in = True

    def reenter_password(self) -> None:
        if not self.__is_next_step_available:
            return

        selector_element = self.__page.query_selector('h1:has-text("Re-enter password")')
        if selector_element:
            self.__logged_in = False
            self.__page.locator('#sensitiveZone_password').fill(self.__password)
            self.__page.locator('#control_continue').click()

            selector_element = self.__page.query_selector('span:has-text("Oops! Password is incorrect.")')
            if selector_element:
                self.__is_next_step_available = False
                raise ValueError("Login failed. Wrong password")
            else:
                self.__logged_in = True

    def enter_answer(self) -> None:
        if not self.__is_next_step_available:
            return

        selector_element = self.__page.query_selector('span:has-text("Let\'s make sure it\'s you")')
        if selector_element:
            self.__logged_in = False
            self.__page.locator('#login_answer').fill(self.__answer)
            self.__page.locator('#login_control_continue').click()

            selector_element = self.__page.query_selector('span:has-text("Oops. Answer is incorrect.")')
            if selector_element:
                self.__is_next_step_available = False
                raise ValueError("Login failed. Wrong answer")
            else:
                self.__logged_in = True

    def reenter_answer(self) -> None:
        if not self.__is_next_step_available:
            return

        selector_element = self.__page.query_selector('h2:has-text("Confirm that it\'s you")')
        if selector_element:
            self.__logged_in = False
            self.__page.locator('#deviceAuth_answer').fill(self.__answer)
            self.__page.locator('#control_save').click()

            selector_element = self.__page.query_selector('span:has-text("Oops! Answer is incorrect.")')
            if selector_element:
                self.__is_next_step_available = False
                raise ValueError("Login failed. Wrong password")
            else:
                self.__logged_in = True

    def ignore_protection_of_account(self) -> None:
        if not self.__is_next_step_available:
            return
        selector_element = self.__page.query_selector('span:has-text("Protect your account")')
        if selector_element:
            self.__page.click("text=I'll do it later")

    def close_complete_profile(self) -> None:
        if not self.__is_next_step_available:
            return
        selector_element = self.__page.query_selector('span:has-text("Complete Your Profile")')
        if selector_element:
            self.__page.click('text=Close')

    def get_page_content(self) -> str:
        return self.__page.content() if self.__logged_in else None

    def get_user_id(self) -> str:
        return self.__user_id if self.__logged_in else None

    def get_user_profile(self) -> str:
        return self.__user_profile if self.__logged_in else None
