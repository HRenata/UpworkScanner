from dotenv import dotenv_values
from playwright.sync_api import sync_playwright, Page

from bs4 import BeautifulSoup


class WebDriver:
    def __init__(self) -> None:
        self.logged_in = False

        credentials = dotenv_values(".env")
        self.username = credentials["USERNAME"]
        self.password = credentials["PASSWORD"]
        self.secret = credentials["SECRET"]

        self.login_url = "https://www.upwork.com/ab/account-security/login"

        self.work_with_browser()

    def work_with_browser(self) -> None:
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=False, slow_mo=100)
            page = browser.new_page()

            self.login(page)

            #self.set_work_soup(page)
            self.set_profile_soup(page)

            browser.close()

    def login(self, page: Page) -> None:
        page.goto(self.login_url, timeout=1000000)

        page.locator('#login_username').fill(self.username)
        page.locator('#login_password_continue').click()

        page.locator('#login_password').fill(self.password)
        page.locator('#login_control_continue').click()

        #page.locator('#login_answer').fill(self.secret)
        #page.locator('#login_control_continue').click()

        page.click("text=Close")

        self.logged_in = True

    def set_work_soup(self, page: Page) -> None:
        if self.logged_in:
            page.click("text=Best Matches")
            html_profile = page.inner_html('#main')
            self.work_soup = BeautifulSoup(html_profile, 'html.parser')

    def get_work_soup(self):
        if self.logged_in:
            return self.work_soup

    def set_profile_soup(self, page: Page) -> None:
        if self.logged_in:
            page.click("text=Best Matches")
            html_profile = page.inner_html('#main')
            self.profile_soup = BeautifulSoup(html_profile, 'html.parser')

    def get_profile_soup(self):
        if self.logged_in:
            return self.profile_soup


wb = WebDriver()
