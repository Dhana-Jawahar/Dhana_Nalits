
from playwright.sync_api import sync_playwright
from urllib.parse import urljoin
import json

BASE_URL = "https://www.jobs.service.gov.uk"
BASE_URL = "https://www.cv-library.co.uk/software-developer-jobs"

def get_text(card, selector):
    """Get text from an element inside a job card."""
    element = card.locator(selector)

    if element.count() > 0:
        return element.first.inner_text().strip()

    return ""


def extract_jobs(page):

    job_cards = page.locator(
        'div[data-testid^="searchResultCard-"]'
    )

    jobs = []

    for i in range(job_cards.count()):

        card = job_cards.nth(i)

        # Extract job ID
        card_id = card.get_attribute("data-testid")
        job_id = card_id.replace("searchResultCard-", "")

        # Extract job title and URL
        title_link = card.locator(
            'a[data-testid^="jobTitle-"]'
        )

        title = title_link.inner_text().strip()

        job_url = urljoin(
            BASE_URL,
            title_link.get_attribute("href")
        )

        # Extract employer and location
        employer_location = get_text(
            card,
            '[data-testid="searchResultCardEmployer"]'
        )

        if " - " in employer_location:
            employer, location = employer_location.split(" - ", 1)
        else:
            employer = employer_location
            location = ""

        # Extract salary
        salary = get_text(
            card,
            "p.govuk-body.govuk-\\!-font-weight-bold"
        )

        # Extract job tags
        tags = card.locator(
            '[data-testid="searchResultsCardTags"] span'
        ).all_inner_texts()

        # Extract description
        description = get_text(
            card,
            '[data-testid="searchResultCardJobDescription"]'
        )

        job = {
            "job_id": job_id,
            "title": title,
            "employer": employer,
            "location": location,
            "salary": salary,
            "tags": tags,
           # "description": description,
            "job_url": job_url,
        }

        jobs.append(job)

    return jobs



from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import quote_plus


def get_jobs(search_string,MAX_PAGES):
    """
    Fetch jobs from all available search-results pages.
    """

    encoded_search = quote_plus(search_string)

    BASE_URL = "https://www.jobs.service.gov.uk"
    #BASE_URL = "https://www.cv-library.co.uk/search-jobs"
    base_search_url = (
        f"{BASE_URL}/jobs/search?keywords={encoded_search}"
    )
    

    all_jobs = []
    seen_job_ids = set()

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page_number = 1

        for page_number in range(1, MAX_PAGES + 1):

            # First page uses the original URL.
            # Subsequent pages use the pageNumber parameter.
            if page_number == 1:
                search_url = base_search_url
            else:
                search_url = (
                    f"{base_search_url}&pageNumber={page_number}"
                )

            print(f"Fetching page {page_number + 1}: {search_url}")

            page.goto(
                search_url,
                wait_until="domcontentloaded"
            )

            job_cards = page.locator(
                'div[data-testid^="searchResultCard-"]'
            )

            try:
                job_cards.first.wait_for(timeout=15000)
            except PlaywrightTimeoutError:
                print("No more job results found.")
                break

            page_jobs = extract_jobs(page)

            if not page_jobs:
                break

            new_jobs = 0

            for job in page_jobs:

                job_id = job["job_id"]

                if job_id not in seen_job_ids:
                    seen_job_ids.add(job_id)
                    all_jobs.append(job)
                    new_jobs += 1

            print(f"Jobs found on this page: {len(page_jobs)}")
            print(f"New jobs added: {new_jobs}")
            print(f"Total unique jobs: {len(all_jobs)}")

            # Stop if this page contains only previously seen jobs.
            if new_jobs == 0:
                print("No new jobs found. Stopping pagination.")
                break

            

            # Small pause between page requests.
            page.wait_for_timeout(1000)

        browser.close()

    return all_jobs



if __name__ == "__main__":

    search_string = "Data Engineer"
    MAX_PAGES = 5
    jobs = get_jobs(search_string,MAX_PAGES)

    print(f"Search: {search_string}")
    print("Total jobs extracted:", len(jobs))

    print(
        json.dumps(
            jobs,
            indent=4,
            ensure_ascii=False
        )
    )
