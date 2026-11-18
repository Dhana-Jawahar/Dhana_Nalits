
from playwright.sync_api import sync_playwright

url = "https://www.jobs.service.gov.uk/jobs/search?keywords=Software+Engineer"

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    page.goto(url, wait_until="domcontentloaded")
    page.locator("body").wait_for()

    print("\n--- JOB HEADINGS ---")

    headings = page.locator("h2, h3").evaluate_all("""
        elements => elements.map(el => ({
            tag: el.tagName,
            title: el.innerText.trim(),
            html: el.parentElement.outerHTML.substring(0, 1200)
        }))
    """)

    for heading in headings:
        print("\nTitle:", heading["title"])
        print("HTML:", heading["html"])

    print("\n--- JOB LINKS ---")

    links = page.locator("a").evaluate_all("""
        elements => elements.map(a => ({
            text: a.innerText.trim(),
            url: a.href
        })).filter(a => a.text.length > 0)
    """)

    for link in links:
        print(link)

    browser.close()
