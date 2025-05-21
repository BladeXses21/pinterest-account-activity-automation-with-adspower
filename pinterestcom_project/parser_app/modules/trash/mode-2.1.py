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


if __name__ == "__main__":
    accounts = list(Account.objects.filter(status='Active'))
    if not accounts:
        print("No active Pinterest accounts found.")
        exit()

    links = list(PinLink.objects.filter(status='Active').values('url'))
    links_map = [link['url'] for link in links]

    ads_profiles_id = ['kw1pmvs', 'kvvx92c', 'kvvx91g']

    with sync_playwright() as p:
        for account, profile_id in zip(accounts, ads_profiles_id):
            print(f"\nWorking with account: {account.email} (Profile: {profile_id})")

            debugger_address = start_adspower_browser(profile_id)
            if not debugger_address:
                continue

            try:
                browser = p.chromium.connect_over_cdp(debugger_address)
            except Exception as e:
                print(f"Failed to connect to browser: {e}")
                continue

            if not browser.contexts:
                print("⚠No context found in browser.")
                continue

            context = browser.contexts[0]

            pinterest_pages = [pg for pg in context.pages if "pinterest.com" in pg.url]
            page = pinterest_pages[0] if pinterest_pages else context.new_page()

            try:
                page = pinterest_login(page, account.email, account.password)
            except Exception as e:
                print(f"Login check failed: {e}")
                continue

            for url in links_map:
                print(f"Opening link: {url}")
                try:
                    perform_actions_on_pinlink(email=account.email, page=page, url=url)
                except (PlaywrightTimeoutError, PlaywrightError) as e:
                    print(f"Error on {url}: {e}")
                    continue

            for p in context.pages:
                try:
                    p.close()
                except Exception:
                    pass