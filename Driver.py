from types import NoneType
import requests
from bs4 import BeautifulSoup
import logging
from urllib.parse import urljoin
import re
import pandas as pd


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
    
    titles_tag = soup.find_all('span', style=re.compile(r'color:\s*#799E91'))
    
    for title_span in titles_tag:
        try:
            title = title_span.get_text(strip=True)
            
    
            parent = title_span.parent
            list_elements = None
            if parent:
                list_elements = parent.find_next_sibling(['ul', 'ol'])
            
            full_text = ""
            if list_elements:
                points = [li.get_text(strip=True) for li in list_elements.find_all('li')]#type:ignore
                full_text = '\n'.join(points)

            row = {
                'url' : url,
                'title' : title,
                'text' : full_text
            }
            
            data_list.append(row)
            
        except Exception as e:
            print(f"Error occurred while processing a title: {e}")
            continue
            
    return data_list
        
def get_rewards(url:str, soup:BeautifulSoup) :
            data_list = []
            
            all_prizes = soup.select('div.prizes-list div.prize-item')
            
            if not all_prizes:
                logging.error('Unavailable rewards')
                raise TitleNotFoundError("Unavailable rewards")
        
            for prize_item in all_prizes:
                title_tag = prize_item.select_one('div.prize-item-content div.prize-item--title')
                title = title_tag.get_text(strip=True) if title_tag else 'Empty'
                
                source_tag = prize_item.select_one('div.prize-item-content div.prize-item--desc')
                source = source_tag.get_text(strip=True) if source_tag else 'Empty'
                
                year_tag = prize_item.select_one('div.prize-item-icon svg text[font-size = "15"]')
                year = year_tag.get_text(strip=True) if year_tag else 'Empty'
                
                month_tag = prize_item.select_one('div.prize-item-icon svg text[font-size = "14"]')
                month = month_tag.get_text(strip=True) if month_tag else 'c'
                
                full_title = f"{title} - {source}"
                full_text = f"{year} - {month}"

                row = {
                    'url' : url,
                    'title' : full_title,
                    'text'  : full_text
                }
                
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
            get_rewards(url,soup)
            print('test')
            
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
