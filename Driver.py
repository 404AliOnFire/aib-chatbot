from types import NoneType
import requests
from bs4 import BeautifulSoup, Tag
import logging
from urllib.parse import urljoin
import re
import pandas as pd
from tabulate import tabulate
from io import StringIO


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


def get_green_titles(url: str, soup: BeautifulSoup) -> list:

    data_list = []

    titles_tag = soup.find_all("span", style=re.compile(r"color:\s*(?:#799E91|#4A4A4A)", re.IGNORECASE))

    for title_span in titles_tag:
        try:
            title = title_span.get_text(strip=True)

            parent = title_span.parent
            list_elements = None
            if parent:
                list_elements = parent.find_next_sibling(["ul", "ol"])

            full_text = ""
            if list_elements:
                points = [
                    li.get_text(strip=True) for li in list_elements.find_all("li")
                ]  # type:ignore
                full_text = "\n".join(points)

            row = {"url": url, "title": title, "text": full_text}

            data_list.append(row)

        except Exception as e:
            print(f"Error occurred while processing a title: {e}")
            continue

    return data_list


def get_rewards(url: str, soup: BeautifulSoup) -> list:
    data_list = []

    all_prizes = soup.select("div.prizes-list div.prize-item")

    if not all_prizes:
        logging.error("Unavailable rewards")
        raise TitleNotFoundError("Unavailable rewards")

    for prize_item in all_prizes:
        title_tag = prize_item.select_one(
            "div.prize-item-content div.prize-item--title"
        )
        title = title_tag.get_text(strip=True) if title_tag else "Empty"

        source_tag = prize_item.select_one(
            "div.prize-item-content div.prize-item--desc"
        )
        source = source_tag.get_text(strip=True) if source_tag else "Empty"

        year_tag = prize_item.select_one(
            'div.prize-item-icon svg text[font-size = "15"]'
        )
        year = year_tag.get_text(strip=True) if year_tag else "Empty"

        month_tag = prize_item.select_one(
            'div.prize-item-icon svg text[font-size = "14"]'
        )
        month = month_tag.get_text(strip=True) if month_tag else "c"

        full_title = f"{title} - {source}"
        full_text = f"{year} - {month}"

        row = {"url": url, "title": full_title, "text": full_text}

        data_list.append(row)

    return data_list


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


# --- Remember to change the return hint --- # changed but re see
def about_us_content(url: str) -> list[dict]:
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
            # pages_tags = soup.select('a.page-link')
            # titles.extend(get_titles(url,soup))
            # texts.extend(get_names(url,soup))

            # if pages_tags:
            #     for link in pages_tags:
            #         if link.has_attr('href'):
            #             new_url = urljoin(url, str(link['href']))
            #             html = fetch_page(new_url)
            #             if html:
            #                 new_soup = BeautifulSoup(html, 'lxml')
            #                 titles.extend(get_titles(new_url, new_soup))
            #                 texts.extend(get_names(new_url, new_soup))
            # for title,name in zip(titles,texts):
            #     print(f"{title}: {name}")
            pass

        elif url.endswith("/sharia-supervisory-board"):
            # df = pd.DataFrame(get_green_titles(url,soup))
            # df.to_csv('output.csv', index=False, encoding='utf-8-sig')
            pass
        #     print(get_paragraph(soup))
        # elif url.endswith("/prizes"):
        #     print(get_title(soup))
        elif url.endswith("/content/prizes"):
            get_rewards(url, soup)
            print("test")

    except TitleNotFoundError as e:
        print(e)
        return {}

    return {"url": url, "title": titles, "text": texts}


def individual_services_content(url: str) -> list[dict]:

    html = fetch_page(url)
    scriped_data = []

    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return {}
    soup = BeautifulSoup(html, "lxml")

    try:
     
            # E-SADAD
        if url.endswith("/733.html"):
            # iBURAQ
            scriped_data.extend(get_esdad_content(url, soup))
            # df.to_csv("test.csv")
            pass
        elif url.endswith('/771.html'):
            scriped_data.extend(get_iburag_content(url, soup))
        else:
            scriped_data.extend(get_individual_service_sections(url, soup))
            
    except TitleNotFoundError as e:
        print(e)
        return {}

    return scriped_data

def get_service_sections(url: str, soup: BeautifulSoup) -> list[dict]:
    """
    Extracts the main title, intro text, and green sections for an individual service page.
    Returns a list of dicts with url, title, and text.
    """
    scriped_data = []
    main_title = get_title(url, soup)
    first_text = get_intro_text(soup)
    row = {
        "url": url,
        "title": main_title,
        "text": first_text if first_text else "N/A",
    }
    scriped_data.append(row)

    green_selections = get_green_titles(url, soup)
    for section in green_selections:
        combined_title = f"{main_title} - {section['title']}"
        row = {
            "url": url,
            "title": combined_title,
            "text": section["text"] if section["text"] else "N/A",
        }
        scriped_data.append(row)
    return scriped_data


def is_green_title_element(tag: Tag) -> bool:
    if tag.find("strong"):
        return True

    green_span = tag.find("span", style=re.compile(r"color:\s*#799E91"))
    if green_span:
        return True

    return False


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
            if '،' in t:
                
                cleaned_parts = [part.strip() for part in t.split('،')]
                processed_text = '\n'.join(cleaned_parts)
                intro_paragraphs.append(processed_text)
                
            else:
                intro_paragraphs.append(t)
                
    return "".join(intro_paragraphs)


def get_esdad_content(url: str, soup: BeautifulSoup) -> list[dict]:
    data = []
    faq_tags = soup.select("div.faq-item")
    title_page = get_title(url, soup)

    if faq_tags:
        for tag in faq_tags:

            tilte_tag = tag.find("div", class_="faq-title")
            title = tilte_tag.get_text(strip=True) if tilte_tag else "N/A"

            full_title = f"{title_page} - {title}"

            content_points = []
            content_tags = tag.find("div", class_="faq-content")

            if content_tags:
                content_points = [
                    li.get_text(strip=True) for li in content_tags.find_all("li")
                ]

            full_content = "\n".join(content_points)

            row = {"url": url, "title": full_title, "text": full_content}
            data.append(row)

        return data

def get_iburag_content(url: str, soup: BeautifulSoup) -> list[dict]:
    """
    Extracts content from the IBURAQ service page, separating the
    introductory paragraphs from the bulleted list.
    
    """
    results = []
    
    container = soup.select_one('div.inner-body-desc.list-design')
    if not container:
        return []

    intro_paragraphs = container.find_all('p', recursive=False)
    if intro_paragraphs:
        intro_text = "\n".join([p.get_text(strip=True) for p in intro_paragraphs])
        
   
        results.append({
            'url': url,
            'title': 'نظام الدفع الإلكتروني IBURAQ', 
            'text': intro_text
        })

    ul_tag = container.find('ul')
    if ul_tag:
        list_items = ul_tag.find_all('li')
            
        if(list_items):
            for list in list_items:
                title_tag = list.find('strong')
                if(title_tag):
                    list_title = title_tag.get_text(strip=True)
        
                list_text = list.get_text(strip=True)
        
                results.append({
                    'url': url,
                    'title': list_title,
                    'text': list_text
                })

    table_data = parse_iburag_table(soup)
    
    for row in table_data:
        title_prefix = "حدود الحركة"
        movement_type = row.get('الحركة', '') 
        
        text_content = ", ".join([f"{key}: {value}" for key, value in row.items()])
        
        results.append({
            'url': url,
            'title': f"{title_prefix} - {movement_type}",
            'text': text_content
        })

    
    return results    

def parse_iburag_table(soup: BeautifulSoup) -> list[dict]:
    """
    Finds the table, parses it using pandas, cleans it up, 
    and returns it as a list of dictionaries.
    This version is more robust and handles different header types.
    """
    table_tag = soup.find('figure', class_='table')
    if not table_tag:
        table_tag = soup.find('table')
        
    if not table_tag:
        return []

    try:
        df = pd.read_html(StringIO(str(table_tag)))[0]
    except ValueError:
        return []

    new_columns = []
    for col in df.columns:
        if isinstance(col, tuple):
            cleaned_col = '_'.join(str(c) for c in col if 'Unnamed' not in str(c))
            new_columns.append(cleaned_col)
        else:
            new_columns.append(str(col))
    
    df.columns = new_columns

    df.dropna(how='all', inplace=True)

    return df.to_dict('records')    
def get_data(url: str, soup: BeautifulSoup):
    title = get_title(url, soup)
    text = get_paragraph(soup)
    return [text], [title]


def extract_content(url: str):

    scrapied_data = []

    # link = "https://aib.ps/content/business-e-services"
    individual_services_urls = [
        'https://aib.ps/content/accounts',
        'https://aib.ps/content/fund',
        'https://aib.ps/content/cards',
        'https://aib.ps/content/e-services',
        'https://aib.ps/content/transfers',
        'https://aib.ps/content/treasury-services',
        'https://aib.ps/content/others'
    ]

    business_services_urls = [
        'https://aib.ps/content/accounts-b',
        'https://aib.ps/content/fund-b',
        'https://aib.ps/content/international-trade',
        'https://aib.ps/content/treasury-services-b',
        'https://aib.ps/content/business-e-services',
        'https://aib.ps/content/transfers-b',
    ]
    
    html = fetch_page(url)

    if html is None:
        logging.error(f"No HTML content to extract for URL: {url}")
        return

    if url.endswith("/about-us"):
        soup = BeautifulSoup(html, "lxml")
        links = soup.select("div.item-list-w a.item-list")

        for link in links:
            href = link.get("href")
            if href:
                full_url = urljoin(BASE_URL, str(href))
                dic = about_us_content(full_url)

    elif url.endswith("/individual-services"):

        for url in individual_services_urls:

            html = fetch_page(url)
            soup = BeautifulSoup(html, "lxml")

            if url.endswith("/e-services"):
                links = soup.select("div.col-md-4 a.cat-list")
            else:
                links = soup.select("div.item-list-w a.item-list")

            for link in links:
                href = link.get("href")
                print(href)
                if href:
                    full_url = urljoin(BASE_URL, str(href))
                    scrapied_data.extend(individual_services_content(full_url))
                else:
                    print("error")
                    
            # Edit this dont forget ----------------------------------- Important
            # df = pd.DataFrame(scrapied_data)
            # df.to_csv("outputs.csv", index=False, encoding="utf-8-sig")
            
    elif url.endswith("/business-services"):
        for url in business_services_urls:
            html = fetch_page(url)
            soup = BeautifulSoup(html, "lxml")
            links = soup.select("div.item-list-w a.item-list")

            for link in links:
                href = link.get("href")
                print(href)
                if href:
                    full_url = urljoin(BASE_URL, str(href))
                    scrapied_data.extend(business_services_content(full_url))
                else:
                    print("error")
            df = pd.DataFrame(scrapied_data)
            df.to_csv("outputs.csv", index=False, encoding="utf-8-sig")

def business_services_content(url: str) -> list[dict]:
    # Placeholder implementation; adjust as needed for your business services scraping logic.
    html = fetch_page(url)
    scriped_data = []

    if html is None:
        logging.error(f"No HTML content for URL: {url}")
        return {}
    soup = BeautifulSoup(html, "lxml")

    try:
        scriped_data.extend(get_service_sections(url, soup))
    except TitleNotFoundError as e:
        print(e)
        return {}

    return scriped_data

def main():
    extract_content(urljoin(BASE_URL, "/content/business-services"))


if __name__ == "__main__":
    main()

