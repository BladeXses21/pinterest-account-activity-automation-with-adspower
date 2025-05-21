import os.path

import requests
from playwright.sync_api import sync_playwright, Playwright
from actions_on_pinklink import perform_actions_on_pinlink
from auth import pinterest_login
from load_django import *
from parser_app.models import Account, PinLink
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError


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


def get_storage_path(email):
    safe_email = email.replace('@', '_at_').replace('.', '_')
    return f"storage/{safe_email}_storage.json"


if __name__ == "__main__":
    accounts = list(Account.objects.filter(status='Active'))

    if not accounts:
        print("⚠️ No Pinterest accounts found in admin.")
        exit()

    links = list(PinLink.objects.filter(status='Active').values('url', 'status'))
    links_map = {link['url']: link['status'] for link in links}

    with sync_playwright() as p:
        for account in accounts:
            print(f"Working with account: {account.email}")

            ads_profiles_id = ['kw1pmvs', 'kvvx92c', 'kvvx91g']

            for profile in ads_profiles_id:
                debugger_address = start_adspower_browser(profile)

                if not debugger_address:
                    print(f"Failed to connect to AdsPower browser for profile {profile}. Skipping.")
                    continue

                try:
                    browser = p.chromium.connect_over_cdp(debugger_address)

                except Exception as e:
                    print(f"❌ Failed to connect or open page: {e}")
                    continue


                storage_path = get_storage_path(account.email)

                if os.path.exists(storage_path):
                    context = browser.new_context(storage_state=storage_path)
                    print(f"Loaded session from {storage_path}")

                else:
                    context = browser.new_context()
                    print("No session found, creating new one...")

                page = context.new_page()

                if not os.path.exists(storage_path):

                    try:
                        page = pinterest_login(page, account.email, account.password)
                        context.storage_state(path=storage_path)
                        print(f"Session saved to {storage_path}")

                    except Exception as e:
                        print(f"Login failed: {e}")
                        continue

                # try:
                #     page = pinterest_login(page, account.email, account.password)
                #
                # except (PlaywrightTimeoutError, PlaywrightError) as e:
                #     print(f"Failed to open login page: {e}")
                #     continue

                for url, status in links_map.items():
                    print(f"Opening link: {url}")

                    try:
                        perform_actions_on_pinlink(page=page, url=url)

                    except (PlaywrightTimeoutError, PlaywrightError) as e:
                        print(f"Error while performing actions on {url}: {e}")
                        continue

                context.close()
                browser.close()
