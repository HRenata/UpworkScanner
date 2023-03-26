import json
import time

from bs4 import BeautifulSoup
from typing import List
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

from upwork_manager import UpworkManager
from model import Job, Profile, Address


class UpworkScraper:
    def __init__(self, username: str, password: str, answer: str):
        self.username: str = None

        self.jobs: List = []
        self.profile_info: List = []

        self.best_matches_content: BeautifulSoup = None
        self.profile_info_content: BeautifulSoup = None
        self.extra_profile_info: str = None


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

    def scrape_jobs(self):
        if self.best_matches_content is None:
            return

        soup = BeautifulSoup(self.best_matches_content, 'html.parser')
        best_matches_jobs = soup.select('div[data-test="job-tile-list"]')

        for job in best_matches_jobs:
            title = job.select_one('h3.job-tile-title').text.strip()
            url = 'https://www.upwork.com/' + job.select_one('h3.job-tile-title a')['href']
            description = soup.select_one('span[data-test="job-description-text"]').text.strip()
            job_type = soup.select_one('strong[data-test="job-type"]').text.strip()
            time_posted = soup.select_one('span[data-test="posted-on"]').text.strip()

            tier_span = soup.select_one('span[data-test="contractor-tier"]')
            tier = tier_span.text.strip() if tier_span else None

            est_time_span = soup.select_one('span[data-test="duration"]')
            est_time = est_time_span.text.strip() if est_time_span else None

            budget_span = soup.select_one('span[data-test="budget"]')
            budget = budget_span.text.strip() if budget_span else None

            skills = []
            skills_wrapper = soup.select_one('div[class="up-skill-wrapper"]').select('a')
            for skill in skills_wrapper:
                skills.append(skill.text.strip())

            client_country_span = soup.select_one('small[data-test="client-country"]')
            client_country = client_country_span.text.strip() if client_country_span else None

            client_rating = float(soup.select_one('div[class="up-rating-background"]')
                                  .select_one('span[class="sr-only"]').text.strip().split(' ')[2])

            payment_verified = soup.select_one('small[data-test="payment-verification-status"]')\
                                   .select_one('strong[class="text-muted"]').text.strip() == 'Payment verified'

            client_spending = soup.select_one('small[data-test="client-spendings"]').text.strip()
            proposals = soup.select_one('strong[data-test = "proposals"]').text.strip()

            job_obj = Job(title=title, url=url, description=description, job_type=job_type, time_posted=time_posted,
                          tier=tier, est_time=est_time, budget=budget, skills=skills, client_country=client_country,
                          client_rating=client_rating, payment_verified=payment_verified,
                          client_spending=client_spending, proposals=proposals)
            self.jobs.append(job_obj.dict())

    def scrape_profile_info(self):
        if self.profile_info_content is None or self.extra_profile_info is None:
            return

        soup = BeautifulSoup(self.profile_info_content, 'html.parser')

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

        account = self.extra_profile_info['profile']['identity']['uid']
        created_at = self.extra_profile_info['person']['creationDate']
        updated_at = self.extra_profile_info['person']['updatedOn']

        full_name_div = soup.select_one('div[data-test="userName"]')
        full_name = full_name_div.text.strip() if full_name_div else ""
        full_name = " ".join(full_name.split())

        first_name = self.extra_profile_info['person']['personName']['firstName']
        last_name = full_name.replace(first_name, '').strip()

        phone_number_div = soup.select_one('div[data-test="phone"]')
        phone_number = phone_number_div.text.strip() if phone_number_div else ""
        phone_number = phone_number.split()

        if not self.username.find('@'):
            hidden_email_div = soup.select_one('div[data-test="userEmail"]')
            hidden_email = hidden_email_div.text.strip() if hidden_email_div else None
            email = self.username + hidden_email.split('@')[1]
        else:
            email = self.username

        picture_url = self.extra_profile_info['person']['photoUrl']

        profile_info = Profile(id=user_id, account=account, created_at=created_at, updated_at=updated_at,
                               first_name=first_name, last_name=last_name, full_name=full_name, email=email,
                               phone_number=phone_number, picture_url=picture_url, address=address)

        self.profile_info.append(profile_info.dict())

    def save_profile_info(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.profile_info, f, indent=4)

    def save_jobs(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.jobs, f, indent=4)


credentials = dotenv_values(".env")
scrapper = UpworkScraper(credentials["USERNAME"], credentials["PASSWORD"], credentials["SECRET"])
scrapper.scrape_jobs()
scrapper.save_jobs('jobs.json')

scrapper.scrape_profile_info()
scrapper.save_profile_info('profile.json')
