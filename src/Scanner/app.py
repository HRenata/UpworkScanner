from dotenv import dotenv_values
from upwork_scrapper import UpworkScraper


if __name__ == "__main__":
    credentials = dotenv_values(".env")
    scrapper = UpworkScraper(
        credentials["USERNAME"],
        credentials["PASSWORD"],
        credentials["SECRET"])

    scrapper.scrape_jobs()
    scrapper.save_jobs('jobs.json')

    scrapper.scrape_profile_info()
    scrapper.save_profile_info('profile.json')
