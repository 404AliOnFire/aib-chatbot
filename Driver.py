"""
Web scraper for collecting data from the Arab Islamic Bank (AIB) website.

This script is the final integrated version. It combines the clean architecture
of the refactored code with the detailed, page-specific parsing logic from
the original script to ensure maximum data extraction.

"""

from typing import List, Dict, Optional
from urllib.parse import urljoin
from io import StringIO
import logging
import re

import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag

# ----------------------
# Config
# ----------------------
DEBUG = True
BASE_URL = "https://aib.ps"
DOMAIN = "aib.ps"

LOG_LEVEL = logging.INFO if DEBUG else logging.CRITICAL
logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")


# ----------------------
# Custom Exception
# ----------------------
class TitleNotFoundError(Exception):
    pass


# ----------------------
# Fetch
# ----------------------
def fetch_page(url: str, timeout: int = 8) -> Optional[str]:
    try:
        r = requests.get(url, timeout=timeout)
        r.raise_for_status()
        return r.text
    except requests.RequestException as e:
        logging.error(f"Error fetching {url}: {e}")
        return None


# ----------------------
# Generic extractors
# ----------------------
def get_title(url: str, soup: BeautifulSoup) -> str:
    title_tag = soup.select_one("h1.inner-header-title")
    if title_tag:
        return title_tag.get_text(strip=True)
    raise TitleNotFoundError("Title tag not found in HTML")


def get_titles(url: str, soup: BeautifulSoup) -> List[str]:
    titles_tag = soup.select("div.staff-item--desc")
    if titles_tag:
        return [t.get_text(strip=True) for t in titles_tag]
    raise TitleNotFoundError("Title tag not found in HTML")


def get_names(url: str, soup: BeautifulSoup) -> List[str]:
    names_tag = soup.select("div.staff-item--title")
    if names_tag:
        return [n.get_text(strip=True) for n in names_tag]
    raise TitleNotFoundError("Name tag not found in HTML")


def get_paragraph(soup: BeautifulSoup) -> str:
    ps = soup.select("div.inner-body-desc p")
    return "\n".join([p.get_text(strip=True) for p in ps])


def get_green_titles(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    data_list = []
    titles_tag = soup.find_all(
        "span", style=re.compile(r"color:\s*(?:#799E91|#4A4A4A)", re.IGNORECASE)
    )
    for title_span in titles_tag:
        title = title_span.get_text(strip=True)
        parent = title_span.parent
        list_elements = parent.find_next_sibling(["ul", "ol"]) if parent else None
        full_text = ""
        if list_elements:
            points = [li.get_text(strip=True) for li in list_elements.find_all("li")]
            full_text = "\n".join(points)
        data_list.append({"url": url, "title": title, "text": full_text})
    return data_list


def get_rewards(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    data_list = []
    all_prizes = soup.select("div.prizes-list div.prize-item")
    if not all_prizes:
        raise TitleNotFoundError("Unavailable rewards")
    for prize_item in all_prizes:
        title_tag = prize_item.select_one("div.prize-item-content div.prize-item--title")
        title = title_tag.get_text(strip=True) if title_tag else "Empty"

        source_tag = prize_item.select_one("div.prize-item-content div.prize-item--desc")
        source = source_tag.get_text(strip=True) if source_tag else "Empty"

        year_tag = prize_item.select_one('div.prize-item-icon svg text[font-size = "15"]')
        year = year_tag.get_text(strip=True) if year_tag else "Empty"

        month_tag = prize_item.select_one('div.prize-item-icon svg text[font-size = "14"]')
        month = month_tag.get_text(strip=True) if month_tag else "Empty"

        full_title = f"{title} - {source}"
        full_text = f"{year} - {month}"
        data_list.append({"url": url, "title": full_title, "text": full_text})
    return data_list


def get_data(url: str, soup: BeautifulSoup):
    title = get_title(url, soup)
    text = get_paragraph(soup)
    return [text], [title]


# ----------------------
# Specific page parsers
# ----------------------
def about_us_content(url: str) -> List[Dict[str, str]]:
    html = fetch_page(url)
    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return []

    soup = BeautifulSoup(html, "lxml")
    rows: List[Dict[str, str]] = []

    try:
        if url.endswith("/about-bank") or url.endswith("/chairmans-speech"):
            texts, titles = get_data(url, soup)
            for t, ti in zip(texts, titles):
                rows.append({"url": url, "title": ti, "text": t})

        elif url.endswith("/board-of-directors"):
            titles = get_titles(url, soup)
            names = get_names(url, soup)
            for ti, name in zip(titles, names):
                rows.append({"url": url, "title": ti, "text": name})

        elif url.endswith("/executive-management"):
            pages_tags = soup.select("a.page-link")
            titles = get_titles(url, soup)
            names = get_names(url, soup)
            if pages_tags:
                for link in pages_tags:
                    if link.has_attr("href"):
                        new_url = urljoin(url, str(link["href"]))
                        html_page = fetch_page(new_url)
                        if html_page:
                            new_soup = BeautifulSoup(html_page, "lxml")
                            titles.extend(get_titles(new_url, new_soup))
                            names.extend(get_names(new_url, new_soup))
            for ti, name in zip(titles, names):
                rows.append({"url": url, "title": ti, "text": name})

        elif url.endswith("/sharia-supervisory-board"):
            rows.extend(get_green_titles(url, soup))
            paragraph_text = get_paragraph(soup)
            if paragraph_text:
                rows.append({"url": url, "title": "General Paragraph", "text": paragraph_text})

        elif url.endswith("/prizes") or url.endswith("/content/prizes"):
            rows.extend(get_rewards(url, soup))

    except TitleNotFoundError as e:
        logging.error(f"Title not found while parsing about-us subpage {url}: {e}")
        return []

    return rows


def individual_services_content(url: str) -> List[Dict[str, str]]:
    html = fetch_page(url)
    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return []

    soup = BeautifulSoup(html, "lxml")
    if url.endswith("/733.html"):
        return get_esdad_content(url, soup)
    elif url.endswith("/771.html"):
        return get_iburag_content(url, soup)
    else:
        return get_service_sections(url, soup)


def business_services_content(url: str) -> List[Dict[str, str]]:
    html = fetch_page(url)
    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return []
    soup = BeautifulSoup(html, "lxml")
    return get_service_sections(url, soup)


# ----------------------
# Service helpers
# ----------------------
def get_service_sections(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    scriped_data = []
    main_title = get_title(url, soup)
    first_text = get_intro_text(soup) or "N/A"
    scriped_data.append({"url": url, "title": main_title, "text": first_text})
    green_selections = get_green_titles(url, soup)
    for section in green_selections:
        combined_title = f"{main_title} - {section['title']}"
        scriped_data.append({"url": url, "title": combined_title, "text": section.get("text", "N/A")})
    return scriped_data


def get_intro_text(soup: BeautifulSoup) -> str:
    intro_paragraphs = []
    container = soup.find("div", class_="inner-body-desc")
    if not container:
        return ""
    for element in container.find_all(True, recursive=False):
        if is_green_title_element(element):
            break
        if element.name == "p" and not element.find("img"):
            t = element.get_text(strip=True)
            intro_paragraphs.append(t)
    return "\n".join(intro_paragraphs)


def is_green_title_element(tag: Tag) -> bool:
    if tag.find("strong"):
        return True
    green_span = tag.find("span", style=re.compile(r"color:\s*#799E91"))
    return bool(green_span)


def get_esdad_content(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    data = []
    faq_tags = soup.select("div.faq-item")
    title_page = get_title(url, soup)
    for tag in faq_tags:
        tilte_tag = tag.find("div", class_="faq-title")
        title = tilte_tag.get_text(strip=True) if tilte_tag else "N/A"
        full_title = f"{title_page} - {title}"
        content_points = []
        content_tags = tag.find("div", class_="faq-content")
        if content_tags:
            content_points = [li.get_text(strip=True) for li in content_tags.find_all("li")]
        full_content = "\n".join(content_points)
        data.append({"url": url, "title": full_title, "text": full_content})
    return data


def get_iburag_content(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    results = []
    container = soup.select_one("div.inner-body-desc.list-design")
    if not container:
        return results
    intro_paragraphs = container.find_all("p", recursive=False)
    if intro_paragraphs:
        intro_text = "\n".join([p.get_text(strip=True) for p in intro_paragraphs])
        results.append({"url": url, "title": "نظام الدفع الإلكتروني IBURAQ", "text": intro_text})
    ul_tag = container.find("ul")
    if ul_tag:
        list_items = ul_tag.find_all("li")
        for li in list_items:
            title_tag = li.find("strong")
            list_title = title_tag.get_text(strip=True) if title_tag else "N/A"
            list_text = li.get_text(strip=True)
            results.append({"url": url, "title": list_title, "text": list_text})
    table_data = parse_iburag_table(soup)
    for row in table_data:
        movement_type = row.get("الحركة", "") or ""
        text_content = ", ".join([f"{k}: {v}" for k, v in row.items()])
        results.append({"url": url, "title": f"حدود الحركة - {movement_type}", "text": text_content})
    return results


def parse_iburag_table(soup: BeautifulSoup) -> List[Dict]:
    table_tag = soup.find("figure", class_="table") or soup.find("table")
    if not table_tag:
        return []
    try:
        df = pd.read_html(StringIO(str(table_tag)))[0]
    except ValueError:
        return []
    df.dropna(how="all", inplace=True)
    return df.to_dict("records")


def atms_places_data(url: str, soup: BeautifulSoup) -> List[Dict[str, str]]:
    all_locations = soup.select("div.location-map-item")
    structured_locations = []
    for location_item in all_locations:
        title = location_item.get("data-title", "العنوان غير متوفر")
        details_div = location_item.find("div", class_="location-details")
        full_text = ""
        if details_div:
            p_tags = details_div.find_all("p")
            full_text = "\n".join([p.get_text(strip=True) for p in p_tags])
        structured_locations.append({"url": url, "title": title, "text": full_text})
    return structured_locations


# ----------------------
# CSV helper
# ----------------------
def save_to_csv(rows: List[Dict], filename: str):
    df = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["url", "title", "text"])
    df.to_csv(filename, index=False, encoding="utf-8-sig")
    logging.info(f"Saved {len(df)} rows to {filename}")


# ----------------------
# Extract content main
# ----------------------
def extract_content(url: str):
    html = fetch_page(url)
    if html is None:
        logging.error(f"No HTML content to extract for URL: {url}")
        return

    if url.endswith("/about-us"):
        soup = BeautifulSoup(html, "lxml")
        links = soup.select("div.item-list-w a.item-list")
        aggregated = []
        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(BASE_URL, str(href))
                aggregated.extend(about_us_content(full_url))
        save_to_csv(aggregated, "about_us.csv")

    elif url.endswith("/individual-services"):
        individual_services_urls = [
            "https://aib.ps/content/accounts",
            "https://aib.ps/content/fund",
            "https://aib.ps/content/cards",
            "https://aib.ps/content/e-services",
            "https://aib.ps/content/transfers",
            "https://aib.ps/content/treasury-services",
            "https://aib.ps/content/others",
        ]
        aggregated = []
        for svc_url in individual_services_urls:
            html2 = fetch_page(svc_url)
            if html2 is None:
                continue
            soup2 = BeautifulSoup(html2, "lxml")
            if svc_url.endswith("/e-services"):
                links = soup2.select("div.col-md-4 a.cat-list")
            else:
                links = soup2.select("div.item-list-w a.item-list")
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(BASE_URL, str(href))
                    aggregated.extend(individual_services_content(full_url))
        save_to_csv(aggregated, "individual_services.csv")

    elif url.endswith("/business-services"):
        business_services_urls = [
            "https://aib.ps/content/accounts-b",
            "https://aib.ps/content/fund-b",
            "https://aib.ps/content/international-trade",
            "https://aib.ps/content/treasury-services-b",
            "https://aib.ps/content/business-e-services",
            "https://aib.ps/content/transfers-b",
        ]
        aggregated = []
        for svc_url in business_services_urls:
            html2 = fetch_page(svc_url)
            if html2 is None:
                continue
            soup2 = BeautifulSoup(html2, "lxml")
            links = soup2.select("div.item-list-w a.item-list")
            for link in links:
                href = link.get("href")
                if href:
                    full_url = urljoin(BASE_URL, str(href))
                    aggregated.extend(business_services_content(full_url))
        save_to_csv(aggregated, "business_services.csv")

    elif url.endswith("/branches-and-atms#branch-110"):
        soup = BeautifulSoup(html, "lxml")
        structured_locations = atms_places_data(url, soup)
        save_to_csv(structured_locations, "atm_branches_locations.csv")


# ----------------------
# Main
# ----------------------
def main():
    main_links = [
        urljoin(BASE_URL, "/content/business-services"),
        urljoin(BASE_URL, "/content/individual-services"),
        urljoin(BASE_URL, "/content/about-us"),
        urljoin(BASE_URL, "/content/branches-and-atms#branch-110"),
    ]
    for link in main_links:
        extract_content(link)


if __name__ == "__main__":
    main()