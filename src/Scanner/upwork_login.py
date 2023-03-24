import time

from dotenv import dotenv_values
from playwright.sync_api import Playwright, Browser, Page, sync_playwright


class UpworkLogin:
    def __init__(self, pw: Playwright):
        self.browser: Browser = pw.chromium.launch(headless=False, slow_mo=200)
        self.page: Page = self.browser.new_page()

    def login(self, username: str, password: str, answer: str):
        # Navigate to Upwork login page
        try:
            login_page = 'https://www.upwork.com/ab/account-security/login'
            self.page.goto(login_page)
        except Exception:
            raise ValueError("Can't connect to the page " + login_page)

        if self.page.title() != "Log In to Your Account | Upwork":
            raise ValueError("Login failed. Can't load the page " + login_page)

        if self.page.locator('span:has-text("Log in to Upwork")').count() == 0:
            raise ValueError("Login failed. It's not login page")

        # Enter username and continue
        self.page.fill('input[placeholder="Username or Email"]', username)
        self.page.click('text=Continue with Email')
        time.sleep(1)

        # If username isn't correct, throw exception
        if self.page.locator('span:has-text("Oops! Username is incorrect.")').count() > 0:
            raise ValueError("Login failed. Wrong username or email")

        # Enter password and login
        self.page.fill('input[placeholder="Password"]', password)
        self.page.click('text=Log in')
        # TODO waiting
        time.sleep(1)

        # TODO recaptcha

        # If password isn't correct, throw exception
        if self.page.locator('span:has-text("Oops! Password is incorrect.")').count() > 0:
            raise ValueError("Login failed. Wrong password")

        # Check if answer on secret question is needed
        if self.page.locator('span:has-text(“Let’s make sure it’s you")').count() > 0:
            # Answer security question
            self.page.fill('input[placeholder="Your answer"]', answer)
            self.page.click('text=Continue')

            # If answer isn't correct, throw exception
            time.sleep(1)
            if self.page.locator('span:has-text("Oops. Answer is incorrect.")').count() > 0:
                raise ValueError("Login failed. Wrong answer")

        # Click "I'll do it later" on protect account page
        if self.page.locator('span:has-text(“Protect your account")').count() > 0:
            self.page.click("text=I'll do it later")

        # Close "Complete Your Profile" window if present
        if self.page.locator('span:has-text(“Complete Your Profile")').count() > 0:
            self.page.click('text=Close')

    def get_best_matches(self):
        # Navigate to "Best Matches" page and save as object
        self.page.goto('https://www.upwork.com/search/profiles/')
        return self.page

    def get_contact_info(self):
        # Navigate to contact info page and save as object
        self.page.goto('https://www.upwork.com/ab/settings/contact')
        return self.page

    def close(self):
        # Close browser
        self.browser.close()


with sync_playwright() as pw:
    login = UpworkLogin(pw)
    try:
        credentials = dotenv_values(".env")
        login.login(credentials["USERNAME"], credentials["PASSWORD"], credentials["SECRET"])
    except ValueError as e:
        print(e)
        # Handle login error
    finally:
        login.close()
