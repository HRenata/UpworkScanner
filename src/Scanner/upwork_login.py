import time

from playwright.sync_api import Playwright, Browser, Page


class UpworkLogin:
    def __init__(self, pw: Playwright, username: str, password: str, answer: str):
        self.pw: Playwright = pw
        self.browser: Browser = self.pw.chromium.launch(headless=False, slow_mo=100)
        self.page: Page = self.browser.new_page()
        self.username: str = username
        self.password: str = password
        self.answer: str = answer

    def login(self):
        # Navigate to Upwork login page
        try:
            login_page = 'https://www.upwork.com/ab/account-security/login'
            self.page.goto(login_page)
        except:
            raise ValueError("Can't connect to the page " + login_page)

        if self.page.title() != "Log In to Your Account | Upwork":
            raise ValueError("Login failed. Can't load the page " + login_page)

        try:
            self.page.locator('span:has-text("Log in to Upwork")').count()
        except:
            raise ValueError("Login failed. It's not login page")

        # Enter username and continue
        self.page.fill('input[placeholder="Username or Email"]', self.username)
        self.page.click('text=Continue with Email')
        time.sleep(1)

        # If username isn't correct, throw exception
        try:
            self.page.locator('span:has-text("Oops! Username is incorrect.")').count()
        except:
            raise ValueError("Login failed. Wrong username or email")

        # Enter password and login
        self.page.fill('input[placeholder="Password"]', self.password)
        self.page.click('text=Log in')
        time.sleep(3)
        # TODO waiting
        # TODO recaptcha

        # If password isn't correct, throw exception
        try:
            self.page.locator('span:has-text("Oops! Password is incorrect.")').count()
        except:
            pass
        else:
            raise ValueError("Login failed. Wrong password")

        # Check if answer on secret question is needed
        try:
            self.page.locator('span:has-text(“Let’s make sure it’s you")').count()
        except:
            pass
        else:
            # Answer security question
            self.page.fill('input[placeholder="Your answer"]', self.answer)
            self.page.click('text=Continue')
            time.sleep(1)

            # If answer isn't correct, throw exception
            try:
                self.page.locator('span:has-text("Oops. Answer is incorrect.")').count()
            except:
                pass
            else:
                raise ValueError("Login failed. Wrong answer")

        # Click "I'll do it later" on protect account page
        try:
            self.page.locator('span:has-text(“Protect your account")').count()
        except:
            pass
        else:
            self.page.click("text=I'll do it later")

        # Close "Complete Your Profile" window if present
        try:
            self.page.locator('span:has-text(“Complete Your Profile")').count()
        except:
            pass
        else:
            self.page.click('text=Close')

    def get_best_matches_content(self):
        self.page.goto('https://www.upwork.com/nx/find-work/best-matches')
        time.sleep(3)

        # Close "Complete Your Profile" window if present
        try:
            self.page.locator('span:has-text(“Complete Your Profile")').count()
        except:
            pass
        else:
            self.page.click('text=Close')

        return self.page.content()

    def get_contact_info_content(self):
        self.page.goto('https://www.upwork.com/freelancers/settings/contactInfo')
        time.sleep(3)
        return self.page.content()

    def close(self):
        self.browser.close()
