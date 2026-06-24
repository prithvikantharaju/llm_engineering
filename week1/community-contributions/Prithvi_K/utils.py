import requests
from bs4 import BeautifulSoup
from playwright.async_api import Page

# Standard headers to fetch a website
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
}


def fetch_website_contents(url):
    """
    Return the title and contents of the website at the given url;
    truncate to 2,000 characters as a sensible limit
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    title = soup.title.string if soup.title else "No title found"
    if soup.body:
        for irrelevant in soup.body(["script", "style", "img", "input"]):
            irrelevant.decompose()
        text = soup.body.get_text(separator="\n", strip=True)
    else:
        text = ""
    return (title + "\n\n" + text)[:2_000]


def fetch_website_links(url):
    """
    Return the links on the webiste at the given url
    I realize this is inefficient as we're parsing twice! This is to keep the code in the lab simple.
    Feel free to use a class and optimize it!
    """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [link.get("href") for link in soup.find_all("a")]
    return [link for link in links if link]

async def search_book(page: Page, name: str) -> str:
    # get the search field locator
    search_locator = page.get_by_placeholder("Title / Author / ISBN")
    await search_locator.fill(name)
    await search_locator.press("Enter")

    # Monitor signin popup and close it
    popup_container = page.locator("div").filter(has_text="Discover & read moreSign up").nth(
        2)  # Example Goodreads class
    close_button = popup_container.get_by_role("button", name="Dismiss")

    # Define an async function that tells Playwright HOW to close the popup
    async def dismiss_popup():
        print("Sign-in popup detected! Closing it...")
        await close_button.click()

    await page.add_locator_handler(popup_container, dismiss_popup)

    # Get table of search results
    table = page.get_by_role("table")

    # Get first row second column which contains hyperlink of the book
    await table.get_by_role('row').first.get_by_role('link').first.click()
    book_url = page.url
    return book_url


async def get_reviews_from_page(page: Page, book_url: str):
    # Get reviews from the book page
    content = await page.get_by_test_id("contentContainer").all_inner_texts()
    return content


async def go_to_author_page(page: Page, author_name: str):
    # Get reviews from the book page

    author_page_link = page.get_by_test_id("name").filter(has_text=author_name.strip()).first
    await author_page_link.click()
    return page.url


