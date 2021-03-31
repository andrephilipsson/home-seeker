#!/usr/local/bin python3

import json
import requests
from datetime import datetime, date

URL = "https://www.afbostader.se/redimo/rest/vacantproducts"
CACHE_FILE = "apartments.json"
TODAY = date.today()


def get_data():
    response = requests.get(URL)
    # If the response wasn't ok,
    # throw an error here so that we don't mess up the cache later
    response.raise_for_status()
    return response.json()["product"]


def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return [a for a in data]
    except FileNotFoundError:
        return []


def update_cache(apts):
    cache = load_cache()

    for apt in cache:
        reserve_date = datetime.strptime(
            apt["reserveUntilDate"], "%Y-%m-%d"
        ).date()

        if TODAY > reserve_date:
            cache.remove(apt)

    apt_ids = [a["productId"] for a in cache]
    new_apts = [a for a in apts if a["productId"] not in apt_ids]
    all_apts = cache + new_apts

    with open(CACHE_FILE, "w") as f:
        json.dump(all_apts, f)

    return new_apts


def filter_apartments(apts):
    filtered_apts = []
    for apt in apts:
        if apt["type"] == "Lägenhet":
            filtered_apts.append(apt)

    return filtered_apts


def pretty_print(apt):
    reserve_date = datetime.strptime(
        apt["reserveUntilDate"], "%Y-%m-%d"
    ).date()

    return f"""{apt["address"]}:
    Area:           {apt["area"]}
    Rooms:          {apt["shortDescription"][:1]}
    Square meters:  {apt["sqrMtrs"]}
    Rent:           {apt["rent"]}
    Move in date:   {apt["moveInDate"]}
    Reserve before: {reserve_date}, {(reserve_date - TODAY).days} day(s)
"""


def print_new_apartments(apts):
    print(f"Today's date: {TODAY}")
    print("These new apartments were found:\n")

    for i, apt in enumerate(apts):
        print(f"{i + 1}. {pretty_print(apt)}")


def main():
    data = get_data()
    filtered_apts = filter_apartments(data)
    new_apts = update_cache(filtered_apts)
    print_new_apartments(new_apts)


if __name__ == "__main__":
    main()
