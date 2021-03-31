#!/usr/local/bin python3

import requests
import json
import datetime

URL = "https://www.afbostader.se/redimo/rest/vacantproducts"
CACHE_FILE = "apartments.json"


def load_cache():
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
            return [a for a in data]
    except FileNotFoundError:
        return []


def update_cache(apartments):
    old_cache = load_cache()

    for apartment in old_cache:
        reserve_until_date = datetime.datetime.strptime(
            apartment["reserveUntilDate"], "%Y-%m-%d"
        ).date()

        if datetime.date.today() > reserve_until_date:
            old_cache.remove(apartment)

    all_apartments = old_cache
    new_apartments = []
    apartment_ids = [a["productId"] for a in old_cache]

    for apartment in apartments:
        apartment_id = apartment["productId"]

        if apartment_id not in apartment_ids:
            new_apartments.append(apartment)
            all_apartments.append(apartment)

    with open(CACHE_FILE, "w") as f:
        json.dump(all_apartments, f)

    return new_apartments


def pretty_print(apartment):
    return f"""{apartment["address"]}:
    Area: {apartment["area"]}
    Square meters: {apartment["sqrMtrs"]}
    Rooms: {apartment["shortDescription"][:1]}
    Rent: {apartment["rent"]}
    Move in date: {apartment["moveInDate"]}
    Last day to reserve: {apartment["reserveUntilDate"]}
"""


def filter_data(data):
    filtered_data = []
    for apt in data:
        if apt["type"] == "Lägenhet":
            filtered_data.append(apt)

    return filtered_data


def get_data():
    response = requests.get(URL)
    # If the response wasn't ok,
    # throw an error here so that we don't mess up the cache later
    response.raise_for_status()
    return response.json()["product"]


def print_new_apartments(apartments):
    print(f"Date: {datetime.date.today()}")
    print("These new apartments was found:\n")

    for i, apt in enumerate(apartments):
        print(f"{i + 1}. {pretty_print(apt)}")


def main():
    data = get_data()
    filtered_data = filter_data(data)
    new_aps = update_cache(filtered_data)
    print_new_apartments(new_aps)


if __name__ == "__main__":
    main()
