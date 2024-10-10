import re
from requests import get
from bs4 import BeautifulSoup
from json import dump


if __name__ == "__main__":
    response = list(
        map(
            lambda element: element["properties"]["id"],
            get(
                "https://gis.kbv.de/webgis/data/getGeojsonData.php?type=praxisnetz"
            ).json()["features"],
        )
    )

    all = get(
        "https://www.kbv.de/tools/praxisnetzatlas/praxisnetzatlas.json.php?id=null&cluster="
        + ",".join(response)
    ).json()["cluster"]

    results = []

    for element in all:
        id = int(element["id"])
        accreditation = int(element["accreditation_id"])
        name = element["name"]
        identification = int(element["identification"])
        practice_count = int(element["description1"])
        doctor_count = int(element["description2"])
        url = (
            BeautifulSoup(element["description3"], "html.parser")
            .find("a")
            .attrs["href"]
        )
        head = (
            BeautifulSoup(element["description4"], "html.parser")
            .find("a")
            .attrs["href"]
        )

        results.append(
            {
                "id": id,
                "name": name,
                "accreditation": accreditation,
                "identification": identification,
                "practices": practice_count,
                "doctors": doctor_count,
                "url": url,
                "head": head,
            }
        )

    results = sorted(results, key=lambda element: element["accreditation"])

    with open("data.json", "w", encoding="utf-8") as f:
        dump(results, f, ensure_ascii=False, indent=4)
