import time

from playwright.sync_api import Playwright, Browser, Page


class PageNavigator:
    def __init__(self, browser: Browser, username: str, password: str, answer: str):
        self.page: Page = browser.new_page()

        self.username: str = username
        self.password: str = password
        self.answer: str = answer

        self.login_url: str = 'https://www.upwork.com/ab/account-security/login'
        self.best_matches_url: str = 'https://www.upwork.com/nx/find-work/best-matches'
        self.contact_info_url: str = 'https://www.upwork.com/freelancers/settings/contactInfo'

        self.next_step_available: bool = True
        self.logged_in: bool = False

    def __goto_page(self, page_url: str, selector: str, error_message: str):
        self.next_step_available = True
        try:
            self.page.goto(page_url)
            time.sleep(2)
        except:
            self.next_step_available = False
            raise ValueError("Can't connect to the page " + page_url)

        selector_element = self.page.query_selector(selector)
        if selector_element is None:
            self.next_step_available = False
            raise ValueError(error_message)

    def goto_login_page(self):
        try:
            self.__goto_page(self.login_url, 'span:has-text("Log in to Upwork")', "Login failed. It's not login page")
        except Exception as e:
            raise e

    def goto_best_matches_page(self):
        if not self.logged_in:
            return

        try:
            self.__goto_page(self.best_matches_url, 'h2:has-text("Jobs you might like")',
                             "It's not Best matches jobs page")
        except Exception as e:
            raise e

    def goto_contact_info_page(self):
        if not self.logged_in:
            return

        try:
            self.__goto_page(self.contact_info_url, 'h1:has-text("Contact info")', "It's not Contact info page")
        except Exception as e:
            raise e

    def enter_username(self):
        if not self.next_step_available:
            return
        # Enter username and continue
        self.page.fill('input[placeholder="Username or Email"]', self.username)
        self.page.click('text=Continue with Email')

        selector_element = self.page.query_selector('span:has-text("Oops! Username is incorrect.")')
        if selector_element:
            self.next_step_available = False
            raise ValueError("Login failed. Wrong username or email")

    def enter_password(self):
        if not self.next_step_available:
            return
        # Enter password and login
        self.page.fill('input[placeholder="Password"]', self.password)
        self.page.click('text=Log in')

        selector_element = self.page.query_selector('span:has-text("Oops! Password is incorrect.")')
        if selector_element:
            raise ValueError("Login failed. Wrong password")
        else:
            self.logged_in = True

    def enter_answer(self):
        self.logged_in = False
        if not self.next_step_available:
            return
        # Check if answer on secret question is needed
        selector_element = self.page.query_selector('span:has-text("Let’s make sure it’s you")')
        if selector_element:
            # Answer security question
            self.page.fill('input[placeholder="Your answer"]', self.answer)
            self.page.click('text=Continue')
            time.sleep(1)

            selector_element = self.page.query_selector('span:has-text("Oops. Answer is incorrect.")')
            if selector_element:
                self.next_step_available = False
                raise ValueError("Login failed. Wrong answer")
            else:
                self.logged_in = True

    def ignore_protection_of_account(self):
        if not self.next_step_available:
            return
        selector_element = self.page.query_selector('span:has-text("Protect your account")')
        if selector_element:
            self.page.click("text=I'll do it later")

    def close_complete_profile(self):
        if not self.next_step_available:
            return
        selector_element = self.page.query_selector('span:has-text("Complete Your Profile")')
        if selector_element:
            self.page.click('text=Close')

    def get_page_content(self):
        return self.page.content() if self.logged_in else None


class UpworkManager:
    def __init__(self, pw: Playwright, username: str, password: str, answer: str):
        self.pw: Playwright = pw
        self.browser: Browser = self.pw.chromium.launch(headless=False, slow_mo=100)
        self.navigator: PageNavigator = PageNavigator(self.browser, username, password, answer)

    def login(self):
        self.navigator.goto_login_page()
        self.navigator.enter_username()
        self.navigator.enter_password()
        self.navigator.enter_answer()
        self.navigator.ignore_protection_of_account()
        self.navigator.close_complete_profile()

    def get_best_matches_content(self):
        self.navigator.goto_best_matches_page()
        self.navigator.close_complete_profile()

        return self.navigator.get_page_content()

    def get_profile_info_content(self):
        self.navigator.goto_contact_info_page()
        time.sleep(3)

        return self.navigator.get_page_content()

    def close(self):
        self.browser.close()
