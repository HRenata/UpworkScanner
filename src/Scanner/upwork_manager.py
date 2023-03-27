from typing import Any

from playwright.sync_api import Playwright, Browser

from Scanner.page_navigator import PageNavigator


class UpworkManager:
    def __init__(self, pw: Playwright, username: str, password: str, answer: str):
        self.pw: Playwright = pw
        self.browser: Browser = self.pw.chromium.launch(
            headless=False, slow_mo=100)
        self.navigator: PageNavigator = PageNavigator(
            self.browser, username, password, answer)

    def login(self) -> None:
        self.navigator.goto_login_page()
        self.navigator.enter_username()
        self.navigator.enter_password()
        self.navigator.enter_answer()
        self.navigator.ignore_protection_of_account()
        self.navigator.close_complete_profile()

    def get_best_matches_content(self) -> Any:
        self.navigator.goto_best_matches_page()
        self.navigator.close_complete_profile()

        return self.navigator.get_page_content()

    def get_profile_info_content(self) -> Any:
        self.navigator.goto_profile_info_page()
        self.navigator.reenter_password()
        self.navigator.reenter_answer()

        return self.navigator.get_page_content()

    def get_profile_extra_info(self) -> Any:
        self.navigator.goto_profile_extra_info_page()
        return self.navigator.user_profile

    def close(self) -> None:
        self.browser.close()
