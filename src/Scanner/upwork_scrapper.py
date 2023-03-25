import json
import time

from bs4 import BeautifulSoup
from typing import List
from dotenv import dotenv_values
from playwright.sync_api import sync_playwright

from upwork_login import UpworkLogin
from model import Job


class UpworkScraper:
    def __init__(self, username: str, password: str, answer: str):
        self.jobs: List = []
        self.best_matches_content: BeautifulSoup = None

        with sync_playwright() as pw:
            login = UpworkLogin(pw, username, password, answer)
            try:
                login.login()
            except ValueError as e:
                print(e)
            else:
                time.sleep(3)
                self.best_matches_content = login.get_best_matches_content()
                self.contact_info_content = login.get_contact_info_content()
            finally:
                login.close()

    def scrape_jobs(self):
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

    def save_jobs(self, file_path):
        with open(file_path, 'w') as f:
            json.dump(self.jobs, f, indent=4)


credentials = dotenv_values(".env")
scrapper = UpworkScraper(credentials["USERNAME"], credentials["PASSWORD"], credentials["SECRET"])
scrapper.scrape_jobs()
scrapper.save_jobs('jobs.json')
