import json
import time

from bs4 import BeautifulSoup
from typing import List
from playwright.sync_api import sync_playwright

from upwork_manager import UpworkManager
from model import Job, Profile, Address


class UpworkScraper:
    def __init__(self, username: str, password: str, answer: str):
        self.__username: str

        self.__jobs: List = []
        self.__profile_info: dict = {}

        self.__best_matches_content: BeautifulSoup
        self.__profile_info_content: BeautifulSoup
        self.__extra_profile_info: str

        with sync_playwright() as pw:
            manager = UpworkManager(pw, username, password, answer)
            self.__username = manager.navigator.username
            try:
                manager.login()
            except ValueError as e:
                print(e)
            else:
                time.sleep(3)
                self.__best_matches_content = manager.get_best_matches_content()
                self.__extra_profile_info = manager.get_profile_extra_info()
                self.__profile_info_content = manager.get_profile_info_content()
            finally:
                manager.close()

    def scrape_jobs(self) -> None:
        if self.__best_matches_content is None:
            return

        soup = BeautifulSoup(self.__best_matches_content, 'html.parser')
        best_matches_jobs = soup.select('div[data-test="job-tile-list"]')

        for job in best_matches_jobs:
            title_h = job.select_one('h3.job-tile-title')
            title = title_h.text.strip() if title_h else ""

            url_h = job.select_one('h3.job-tile-title a')
            url = ('https://www.upwork.com/' + url_h['href']) if url_h else ""

            description_span = soup.select_one('span[data-test="job-description-text"]')
            description = description_span.text.strip() if description_span else ""

            job_type_strong = soup.select_one('strong[data-test="job-type"]')
            job_type = job_type_strong.text.strip() if job_type_strong else ""

            time_posted_span = soup.select_one('span[data-test="posted-on"]')
            time_posted = time_posted_span.text.strip() if time_posted_span else ""

            tier_span = soup.select_one('span[data-test="contractor-tier"]')
            tier = tier_span.text.strip() if tier_span else ""

            est_time_span = soup.select_one('span[data-test="duration"]')
            est_time = est_time_span.text.strip() if est_time_span else None

            budget_span = soup.select_one('span[data-test="budget"]')
            budget = budget_span.text.strip() if budget_span else None

            skills = []
            skills_wrapper_div = soup.select_one('div[class="up-skill-wrapper"]')
            skills_wrapper = skills_wrapper_div.select('a') if skills_wrapper_div else []
            for skill in skills_wrapper:
                skills.append(skill.text.strip())

            client_country_span = soup.select_one('small[data-test="client-country"]')
            client_country = client_country_span.text.strip() if client_country_span else ""

            rating_div = soup.select_one('div[class="up-rating-background"]')
            rating_span = rating_div.select_one('span[class="sr-only"]') if rating_div else ""
            client_rating = float(rating_span.text.strip().split(' ')[2]) if rating_span else 0

            verification_small = soup.select_one('small[data-test="payment-verification-status"]')
            verification_strong = verification_small.select_one('strong[class="text-muted"]') \
                if verification_small else ""
            verification = verification_strong.text.strip() if verification_strong else ""
            payment_verified = verification == 'Payment verified'

            client_spending_small = soup.select_one('small[data-test="client-spendings"]')
            client_spending = client_spending_small.text.strip() if client_spending_small else ""

            proposals_strong = soup.select_one('strong[data-test="proposals"]')
            proposals = proposals_strong.text.strip() if proposals_strong else ""

            job_obj = Job(title=title, url=url, description=description, job_type=job_type, time_posted=time_posted,
                          tier=tier, est_time=est_time, budget=budget, skills=skills, client_country=client_country,
                          client_rating=client_rating, payment_verified=payment_verified,
                          client_spending=client_spending, proposals=proposals)
            self.__jobs.append(job_obj.dict())

    def scrape_profile_info(self) -> None:
        if self.__profile_info_content is None or self.__extra_profile_info is None:
            return

        soup = BeautifulSoup(self.__profile_info_content, 'html.parser')

        address_street_span = soup.select_one('span[data-test="addressStreet"]')
        address_street = address_street_span.text.strip() if address_street_span else ""

        address_street2_span = soup.select_one('span[data-test="addressStreet2"]')
        address_street2 = address_street2_span.text.strip() if address_street2_span else None

        city_span = soup.select_one('span[data-test="addressCity"]')
        city = city_span.text.strip() if city_span else ""

        state_span = soup.select_one('span[data-test="addressState"]')
        state = state_span.text.strip() if state_span else None

        postal_code_span = soup.select_one('span[data-test="addressZip"]')
        postal_code = postal_code_span.text.strip() if postal_code_span else None

        country_span = soup.select_one('span[data-test="addressCountry"]')
        country = country_span.text.strip() if country_span else ""

        address = Address(line1=address_street, line2=address_street2, city=city, state=state,
                          postal_code=postal_code, country=country)

        user_id_div = soup.select_one('div[data-test="userId"]')
        user_id = user_id_div.text.strip() if user_id_div else ""

        account = self.__extra_profile_info['profile']['identity']['uid']
        created_at = self.__extra_profile_info['person']['creationDate']
        updated_at = self.__extra_profile_info['person']['updatedOn']

        full_name_div = soup.select_one('div[data-test="userName"]')
        full_name = full_name_div.text.strip() if full_name_div else ""
        full_name = " ".join(full_name.split())

        first_name = self.__extra_profile_info['person']['personName']['firstName']
        last_name = full_name.replace(first_name, '').strip()

        phone_number_div = soup.select_one('div[data-test="phone"]')
        phone_number = phone_number_div.text.strip() if phone_number_div else ""
        phone_number = "".join(phone_number.split())

        if not self.__username.find('@'):
            hidden_email_div = soup.select_one('div[data-test="userEmail"]')
            hidden_email = hidden_email_div.text.strip() if hidden_email_div else None
            email = self.__username + hidden_email.split('@')[1]
        else:
            email = self.__username

        picture_url = self.__extra_profile_info['person']['photoUrl']

        self.__profile_info = Profile(id=user_id, account=account, created_at=created_at,
                                      updated_at=updated_at, first_name=first_name, last_name=last_name,
                                      full_name=full_name, email=email, phone_number=phone_number,
                                      picture_url=picture_url, address=address).dict()

    def save_profile_info(self, file_path) -> None:
        with open(file_path, 'w') as f:
            json.dump(self.__profile_info, f, indent=4)

    def save_jobs(self, file_path) -> None:
        with open(file_path, 'w') as f:
            json.dump(self.__jobs, f, indent=4)
