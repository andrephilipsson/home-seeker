#!/usr/bin/python3

import json
import requests
import smtplib
import ssl
from datetime import datetime, date
from pathlib import Path

# Should be absolute path or path relative to current directory
CACHE_FILE = Path(__file__).parent / "apartments.json"
CONFIG_FILE = Path(__file__).parent / "config.json"
URL = "https://api.afbostader.se:442/redimo/rest/vacantproducts"
TODAY = date.today()
config = None


def load_config():
    global config
    try:
        with open(CONFIG_FILE, "r") as config_file:
            config = json.load(config_file)
    except FileNotFoundError:
        print("No config file found. Will send results to stdout.\n")


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
        # This is where you would add your own filters

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


def create_email_message(apts):
    msg = f"""Subject: New apartments on AF Bostäder ({TODAY})
These new apartments were found:\n\n"""

    for i, apt in enumerate(apts):
        msg += f"{i + 1}. {pretty_print(apt)}\n"
    return msg


def send_email(message):
    try:
        port = config["port"]
        smtp_server = config["smtpServer"]
        email = config["email"]
        password = config["password"]
    except KeyError:
        print("Some required configurations is missing, no email will be sent.")
        return

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls(context=context)
        server.login(email, password)
        server.sendmail(email, email, message.encode("utf8"))


def main():
    load_config()
    data = get_data()
    filtered_apts = filter_apartments(data)
    new_apts = update_cache(filtered_apts)
    if config["sendEmail"]:
        msg = create_email_message(new_apts)
        send_email(msg)
    else:
        print_new_apartments(new_apts)


if __name__ == "__main__":
    main()
