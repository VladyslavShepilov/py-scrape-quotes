from dataclasses import dataclass
from bs4 import BeautifulSoup
import requests
import csv

BASE_URL = "https://quotes.toscrape.com/"
SELECTOR_NEXT_NAV = "li.next > a"
SELECTOR_QUOTE_BLOCK = "div.quote"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


def is_next_page(soup: BeautifulSoup) -> bool:
    next_page = soup.select_one(SELECTOR_NEXT_NAV)
    return next_page is not None


def retrieve_page_soup(page_num: int) -> BeautifulSoup:
    page_url = BASE_URL + f"page/{page_num}/"
    response = requests.get(page_url).content
    soup = BeautifulSoup(response, "html.parser")
    return soup


def parse_single_quote(quote_soup: BeautifulSoup) -> Quote:
    text = quote_soup.select_one("span.text").text
    author = quote_soup.select_one("small.author").text
    tags = [
        tag.get_text(strip=True)
        for tag in quote_soup.select("div.tags a.tag")
    ]
    return Quote(text=text, author=author, tags=tags)


def parse_page(page_soup: BeautifulSoup, result_arr: list) -> list[Quote]:
    for quote in page_soup.select(SELECTOR_QUOTE_BLOCK):
        new_quote = parse_single_quote(quote)
        result_arr.append(new_quote)
    return result_arr


def main(output_csv_path: str) -> None:
    result_arr = []
    page_num = 1

    # Retrieve and parse the first page
    page_soup = retrieve_page_soup(page_num)
    parse_page(page_soup=page_soup, result_arr=result_arr)

    # Continue scraping while there is a next page
    while is_next_page(page_soup):
        page_num += 1
        page_soup = retrieve_page_soup(page_num)
        parse_page(page_soup, result_arr)

    with open(output_csv_path, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["text", "author", "tags"])
        for quote in result_arr:
            writer.writerow([quote.text, quote.author, quote.tags])


if __name__ == "__main__":
    main("quotes.csv")
