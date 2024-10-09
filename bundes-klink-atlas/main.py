from os import curdir
from requests import get
from json import dump

BASE_URL = "https://bundes-klinik-atlas.de/searchresults/"

results = []


def fetch_hospitals(page: int = 0, page_size: int = 20):
    payload = {
        "tx_solr[start]": page * page_size,
        "tx_solr[rows]": page_size,
        "searchtype": "free-search",
    }

    response = get(BASE_URL, params=payload)

    print("CRAWLED", page * page_size, "TO", (page +1 ) * page_size)

    json = response.json()

    meta = json["metaInfos"] 
    continue_crawl = meta["loadMore"]




    for element in json["results"]:
        id = element["id"]
        name = element["header"]
        link = element["detailLink"]

        final_element = {
                    "id": id,
                    "name": name,
                    "link": link,
                }

        results.append(final_element)


    return continue_crawl



if __name__ == "__main__":
    current_page = 0
    while fetch_hospitals(current_page):
        current_page += 1

    with open("data.json", "w", encoding="utf-8") as f:
        dump(results, f, ensure_ascii=False, indent=4)
