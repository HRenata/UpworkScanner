from typing import Any, List
import time
import json

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from Scanner.model import Job, Profile, Address
from Scanner.upwork_manager import UpworkManager


class UpworkScraper:
    def __init__(self, username: str, password: str, answer: str):
        self.username: str

        self.jobs: List = []
        self.profile_info: dict = {}

        self.best_matches_content: BeautifulSoup = None
        self.profile_info_content: BeautifulSoup = None
        self.extra_profile_info: str = ""

        with sync_playwright() as pw:
            manager = UpworkManager(pw, username, password, answer)
            self.username = manager.navigator.username
            try:
                manager.login()
            except ValueError as e:
                print(e)
            else:
                time.sleep(3)
                self.best_matches_content = manager.get_best_matches_content()
                self.extra_profile_info = manager.get_profile_extra_info()
                self.profile_info_content = manager.get_profile_info_content()
            finally:
                manager.close()

    def _get_element_from_html(self, soup: BeautifulSoup,
                               selector: str, default_value: Any) -> Any:
        el_selector = soup.select_one(selector)
        return el_selector.text.strip() if el_selector else default_value

    def scrape_jobs(self) -> None:
        if self.best_matches_content is None:
            return

        soup = BeautifulSoup(self.best_matches_content, 'html.parser')
        best_matches_jobs = soup.select('div[data-test="job-tile-list"]')

        for job in best_matches_jobs:
            title = self._get_element_from_html(job, 'h3.job-tile-title', "")

            url_h = job.select_one('h3.job-tile-title a')
            url = ('https://www.upwork.com/' + url_h['href']) if url_h else ""

            description = self._get_element_from_html(job, 'span[data-test="job-description-text"]', "")
            job_type = self._get_element_from_html(job, 'strong[data-test="job-type"]', "")
            time_posted = self._get_element_from_html(job, 'span[data-test="posted-on"]', "")
            tier = self._get_element_from_html(job, 'span[data-test="contractor-tier"]', "")
            est_time = self._get_element_from_html(job, 'span[data-test="duration"]', None)
            budget = self._get_element_from_html(job, 'span[data-test="budget"]', None)

            skills = []
            skills_wrapper_div = soup.select_one('div[class="up-skill-wrapper"]')
            skills_wrapper = skills_wrapper_div.select('a') if skills_wrapper_div else []
            for skill in skills_wrapper:
                skills.append(skill.text.strip())

            client_country = self._get_element_from_html(job, 'small[data-test="client-country"]', "")

            rating_div = job.select_one('div[class="up-rating-background"]')
            rating_span = rating_div.select_one(
                'span[class="sr-only"]') if rating_div else ""
            client_rating = float(
                rating_span.text.strip().split(' ')[2]) if rating_span else 0

            verification_small = soup.select_one('small[data-test="payment-verification-status"]')
            verification = self._get_element_from_html(
                verification_small, 'strong[class="text-muted"]', "")
            payment_verified = verification == 'Payment verified'

            client_spending = self._get_element_from_html(job, 'small[data-test="client-spendings"]', "")
            proposals = self._get_element_from_html(job, 'strong[data-test="proposals"]', "")

            job_obj = Job(title=title, url=url, description=description, job_type=job_type, time_posted=time_posted,
                          tier=tier, est_time=est_time, budget=budget, skills=skills, client_country=client_country,
                          client_rating=client_rating, payment_verified=payment_verified,
                          client_spending=client_spending, proposals=proposals)
            self.jobs.append(job_obj.dict())

    def scrape_profile_info(self) -> None:
        if self.profile_info_content is None or self.extra_profile_info is None:
            return

        soup = BeautifulSoup(self.profile_info_content, 'html.parser')

        address_street = self._get_element_from_html(soup, 'span[data-test="addressStreet"]', "")
        address_street2 = self._get_element_from_html(soup, 'span[data-test="addressStreet2"]', "")
        city = self._get_element_from_html(soup, 'span[data-test="addressCity"]', "")
        state = self._get_element_from_html(soup, 'span[data-test="addressState"]', None)
        postal_code = self._get_element_from_html(soup, 'span[data-test="addressZip"]', None)
        country = self._get_element_from_html(soup, 'span[data-test="addressCountry"]', "")

        address = Address(line1=address_street, line2=address_street2, city=city, state=state,
                          postal_code=postal_code, country=country)

        user_id = self._get_element_from_html(soup, 'div[data-test="userId"]', "")

        account = self.extra_profile_info['profile']['identity']['uid']
        created_at = self.extra_profile_info['person']['creationDate']
        updated_at = self.extra_profile_info['person']['updatedOn']

        full_name = self._get_element_from_html(soup, 'div[data-test="userName"]', "")
        full_name = " ".join(full_name.split())

        first_name = self.extra_profile_info['person']['personName']['firstName']
        last_name = full_name.replace(first_name, '').strip()

        phone_number = self._get_element_from_html(soup, 'div[data-test="phone"]', "")
        phone_number = "".join(phone_number.split())

        if not self.username.find('@'):
            hidden_email = self._get_element_from_html(soup, 'div[data-test="userEmail"]', None)
            email = self.username + hidden_email.split('@')[1] if hidden_email else self.username
        else:
            email = self.username

        picture_url = self.extra_profile_info['person']['photoUrl']

        self.profile_info = Profile(id=user_id, account=account, created_at=created_at,
                                      updated_at=updated_at, first_name=first_name, last_name=last_name,
                                      full_name=full_name, email=email, phone_number=phone_number,
                                      picture_url=picture_url, address=address).dict()

    def save_profile_info(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump(self.profile_info, f, indent=4)

    def save_jobs(self, file_path: str) -> None:
        with open(file_path, 'w') as f:
            json.dump(self.jobs, f, indent=4)
