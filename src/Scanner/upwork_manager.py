from typing import Any

from playwright.sync_api import Playwright, Browser

from Scanner.page_navigator import PageNavigator


class UpworkManager:
    def __init__(self, pw: Playwright, username: str,
                 password: str, answer: str):
        self.__pw: Playwright = pw
        self.__browser: Browser = self.__pw.chromium.launch(
            headless=False, slow_mo=100)
        self.__navigator: PageNavigator = PageNavigator(
            self.__browser, username, password, answer)

    @property
    def navigator(self) -> PageNavigator:
        return self.__navigator

    def login(self) -> None:
        self.__navigator.goto_login_page()
        self.__navigator.enter_username()
        self.__navigator.enter_password()
        self.__navigator.enter_answer()
        self.__navigator.ignore_protection_of_account()
        self.__navigator.close_complete_profile()

    def get_best_matches_content(self) -> Any:
        self.__navigator.goto_best_matches_page()
        self.__navigator.close_complete_profile()

        return self.__navigator.get_page_content()

    def get_profile_info_content(self) -> Any:
        self.__navigator.goto_profile_info_page()
        self.__navigator.reenter_password()
        self.__navigator.reenter_answer()

        return self.__navigator.get_page_content()

    def get_profile_extra_info(self) -> Any:
        self.__navigator.goto_profile_extra_info_page()
        return self.__navigator.user_profile

    def close(self) -> None:
        self.__browser.close()
