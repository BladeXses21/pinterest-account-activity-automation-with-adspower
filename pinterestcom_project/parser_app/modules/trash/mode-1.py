import requests
from playwright.sync_api import sync_playwright

from action import perform_actions
from auth import pinterest_login
import os
import django
from load_django import *
from parser_app.models import Account


def start_adspower_browser(profile_id):
    api_port = 50325
    url = f"http://localhost:{api_port}/api/v1/browser/start?user_id={profile_id}"
    print(f"➡️ request: {url}")

    response = requests.get(url)

    print(f"⬅️ response: {response.status_code} | {response.text}")

    if response.status_code == 200:
        data = response.json()
        try:
            debugger_address = data['data']['ws']['puppeteer']
            return debugger_address
        except KeyError:
            print("⚠️ The response does not contain the required key (data → ws → puppeteer)")
            return None
    else:
        print(f"❌ Unable to start AdsPower browser for profile {profile_id}")
        return None


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pinterestcom_project.settings")
django.setup()


if __name__ == "__main__":
    accounts = Account.objects.filter(status='Active')

    if not accounts:
        print("⚠️ No Pinterest accounts found in admin.")
        exit()

    with sync_playwright() as p:
        for account in accounts:

            ads_profiles_id = ['kwofqtq', 'kwohf6w']

            for profile in ads_profiles_id:
                debugger_address = start_adspower_browser(profile)

                if debugger_address:

                    try:
                        browser = p.chromium.connect_over_cdp(debugger_address)
                        page = browser.new_page()
                    except Exception as e:
                        print(f"❌ Failed to connect or open page: {e}")
                        continue

                    page  = pinterest_login(page, profile)

                    if page is not None:
                        perform_actions(page)
                        browser.close()

                    else:
                        print("Failed to log in. Exiting.")

                    if browser:
                        browser.close()

                else:
                    print(f"Failed to connect to AdsPower browser for profile {profile}. Skipping.")