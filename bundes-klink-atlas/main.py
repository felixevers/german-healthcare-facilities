from requests import get
from bs4 import BeautifulSoup
from json import dump
import re

BASE_URL = "https://bundes-klinik-atlas.de"

SEARCH_ENDPOINT = BASE_URL + "/searchresults/"


def fetch_hospitals(page: int = 0, page_size: int = 20):
    payload = {
        "tx_solr[start]": page * page_size,
        "tx_solr[rows]": page_size,
        "searchtype": "free-search",
    }

    response = get(SEARCH_ENDPOINT, params=payload)

    print("CRAWLED", page * page_size, "TO", (page + 1) * page_size)

    json = response.json()

    meta = json["metaInfos"]

    continue_crawl = meta["loadMore"]

    if not continue_crawl:
        return []

    results = []

    for element in json["results"]:
        id = element["id"]
        name = element["header"]
        link = element["detailLink"]

        final_element = {
            "id": id,
            "name": name,
            "link": BASE_URL + link,
        }

        results.append(final_element)

    return results


def fetch_detailed_hospital(link: str, id: int | None = None):
    response = get(link).text

    print(link)

    soup = BeautifulSoup(response, "html.parser")

    name = soup.find("h1").get_text().strip()
    lat, lng = map(
        float,
        soup.find(id="js_hospital-map")
        .attrs["data-location-latlng"]
        .split(","),
    )
    address = soup.find("address").get_text().strip()

    url_element = soup.find("a", {"class": "u-icon--icon-link-extern"})
    url = None
    if url_element:
        url = url_element.get_text().strip()

    phone_element = soup.find("a", {"class": "u-icon--icon-telefon"})
    phone = None
    if phone_element:
        phone = phone_element.get_text().strip()

    email_element = soup.select_one(".col-1.row-3")
    email = None
    if email_element:
        email = email_element.get_text().strip()

    company = soup.select_one(".col-2.row-1").contents[2].get_text().strip()

    beds = re.findall(
        r"\d+",
        soup.find("li", {"class": "location-size"}).find("small").get_text(),
    )

    if len(beds) != 2:
        beds += [0]

    stationary_beds, temporary_beds = map(int, beds)

    cases = int(
        soup.find_all("div", {"class": "c-tacho-text__text"})[0]
        .find("strong")
        .get_text()
        .strip()
        .split(" ")[-1]
        .replace(".", "")
    )
    nursing_quota = float(
        re.search(
            r"\d+,\d+",
            soup.find_all("div", {"class": "c-tacho-text__text"})[1]
            .find("strong")
            .get_text()
            .strip(),
        )
        .group()
        .replace(",", ".")
    )
    nurses = int(
        soup.select_one("div.ce-accordion__header__components p strong")
        .get_text()
        .strip()
        .replace(".", "")
    )

    return {
        "id": id,
        "name": name,
        "address": address,
        "location": {
            "lat": lat,
            "long": lng,
        },
        "url": url,
        "phone": phone,
        "email": email,
        "company": company,
        "beds": {
            "stationary": stationary_beds,
            "temporary": temporary_beds,
        },
        "cases": cases,
        "nursing": {
            "quota": nursing_quota,
            "total": nurses,
        },
    }


def index_hospitals():
    current_page = 0

    results = []

    while elements := fetch_hospitals(current_page):
        for element in elements:
            results.append(
                fetch_detailed_hospital(element["link"], id=element["id"])
            )

        current_page += 1

    with open("data.json", "w", encoding="utf-8") as f:
        dump(results, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    index_hospitals()
