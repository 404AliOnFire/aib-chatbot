import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import csv
import time

class TitleNotFoundError(Exception):
    pass

DEBUG = False
URL = "https://aib.ps/"
DOMAIN = "aib.ps"
OUTPUT_FILE = ""

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
        logging.info("HTMl Content Successfully Fetched!")
        return response.text
    except requests.exceptions.RequestException as e:
        logging.error(f"Error Fetching {url} page: {e}")
        return None


def aboutus_content(url: str) -> tuple:
    html = fetch_page(url)
    soup = BeautifulSoup(html, "lxml")

    try:

        if url.endswith("/about-bank"):
            print(get_title(soup))
        elif url.endswith("/chairmans-speech"):
            print(get_title(soup))
        elif url.endswith("/board-of-directors"):
             print(get_title(soup))
        elif url.endswith("/executive-management"):
             print(get_title(soup))
        elif url.endswith("/sharia-supervisory-board"):
             print(get_title(soup))
        elif url.endswith("/prizes"):
             print(get_title(soup))


    except TitleNotFoundError as e:
        print(e)


def get_title(soup: BeautifulSoup) -> str:
    title_tag = soup.select_one("h1.inner-header-title")

    if title_tag:
        title = title_tag.get_text(strip=True)
        logging.info(f"Title feteched: {title}")
        return title

    else:
        logging.error("Title tag 'h1.inner-header-title' not found.")
        raise TitleNotFoundError("Title tag not found in HTML")


def extract_content(url: str, html: str):
    soup = BeautifulSoup(html, "lxml")
    text_content = []
    title = []
    urls = []

    if url.endswith("/about-us"):
        links = soup.select("div.item-list-w a.item-list")
        for link in links:
            aboutus_content(link['href'])


def main():
    html = fetch_page("https://aib.ps/content/about-us")
    extract_content("https://aib.ps/content/about-us", html)


if __name__ == "__main__":
    main()
