import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin


class TitleNotFoundError(Exception):
    pass


DEBUG = False
BASE_URL = "https://aib.ps/"
DOMAIN = "aib.ps"

if DEBUG:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
else:
    logging.basicConfig(level=logging.CRITICAL)


def fetch_page(url: str):
    logging.info(f"Fetching Page {url}.")
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        logging.info("HTML Content Successfully Fetched!")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error Fetching {url} page: {e}")
        return None


def get_title(url: str, soup: BeautifulSoup) -> str:
    title_tag = soup.select_one("h1.inner-header-title")
    if title_tag:
        title = title_tag.get_text(strip=True)
        logging.info(f"Title fetched: {title}")
        return title
    else:
        logging.error("Title tag 'h1.inner-header-title' not found.")
        raise TitleNotFoundError("Title tag not found in HTML")


def get_titles(url: str, soup: BeautifulSoup) -> list:

    titles_tag = soup.select("div.staff-item--desc")
    if titles_tag:
        titles = [title.get_text(strip=True) for title in titles_tag]
        logging.info(f"Titles fetched: {titles}")
        return titles
    else:
        logging.error("Title tag 'div.staff-item--desc' not found.")
        raise TitleNotFoundError("Title tag not found in HTML")


def get_names(url: str, soup: BeautifulSoup) -> list:
    names_tag = soup.select("div.staff-item--title")
    if names_tag:
        names = [name.get_text(strip=True) for name in names_tag]
        logging.info(f"Names fetched: {names}")
        return names
    else:
        logging.error("Title tag 'staff-item--title' not found.")
        raise TitleNotFoundError("Name tag not found in HTML")


def get_paragraph(soup: BeautifulSoup) -> str:

    ps = soup.select("div.inner-body-desc p")
    paragraphs = [p.get_text(strip=True) for p in ps]
    return "\n".join(paragraphs)


def about_us_content(url: str) -> dict:
    texts = []
    titles = []

    html = fetch_page(url)
    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return {}
    soup = BeautifulSoup(html, "lxml")
    try:
        if url.endswith("/about-bank"):
            # texts,titles = get_data(url,soup)
            pass

        elif url.endswith("/chairmans-speech"):
            # texts,titles = get_data(url,soup)
            pass
        elif url.endswith("/board-of-directors"):
            #    titles =  get_titles(url,soup)
            #    texts = get_names(url,soup)
            #    for title, name in zip(titles,texts):
            #      print(f"{title}: {name}")
            pass

        elif url.endswith("/executive-management"):
            pages_tags = soup.select('a.page-link')
            
            if pages_tags:
                for link in pages_tags:
                    if link.has_attr('href'):
                        new_url = urljoin(url, str(link['href']))
                        html = fetch_page(new_url)
                        if html:
                            new_soup = BeautifulSoup(html, 'lxml')
                            titles.extend(get_titles(new_url, soup))
                            texts.extend(get_names(new_url, soup))
        # elif url.endswith("/sharia-supervisory-board"):
        #     print(get_title(soup), end="\n\n")
        #     print(get_paragraph(soup))
        # elif url.endswith("/prizes"):
        #     print(get_title(soup))
    except TitleNotFoundError as e:
        print(e)
        return {}
    return {"url": url, "title": titles, "text": texts}


def get_data(url: str, soup: BeautifulSoup):
    title = get_title(url, soup)
    text = get_paragraph(soup)
    return [text], [title]


def extract_content(url: str, html: str):
    if html is None:
        logging.error(f"No HTML content to extract for URL: {url}")
        return
    soup = BeautifulSoup(html, "lxml")
    if url.endswith("/about-us"):
        links = soup.select("div.item-list-w a.item-list")
        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(BASE_URL, str(href))
                dic = about_us_content(full_url)


def main():
    html = fetch_page(urljoin(BASE_URL, "content/about-us"))
    extract_content(urljoin(BASE_URL, "content/about-us"), str(html))


if __name__ == "__main__":
    main()
