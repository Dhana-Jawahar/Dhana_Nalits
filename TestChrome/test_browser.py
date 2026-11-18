
from playwright.sync_api import sync_playwright

url = "https://www.jobs.service.gov.uk/jobs/search?keywords=Software+Engineer"

with sync_playwright() as p:

    print("Hello")
    browser = p.chromium.launch(headless=False)

    page = browser.new_page()

    response = page.goto(url, wait_until="domcontentloaded")

    print("Page title:", page.title())
    print("Page URL:", page.url)
    print("HTTP status:", response.status if response else "Unknown")

    print("\nPage content:")
    print(page.locator("body").inner_text()[:3000])

    browser.close()