import os.path
import os
import django
import requests
from playwright.sync_api import sync_playwright, Playwright
from actions_on_pinklink import perform_actions_on_pinlink
from auth import pinterest_login
from load_django import *
from parser_app.models import Account, PinLink, AccountLog
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from logger import log_account_action
import traceback



def start_adspower_browser(profile_id, playwright):
    api_port = 50325
    url = f"http://localhost:{api_port}/api/v1/browser/start?user_id={profile_id}"
    print(f"➡️ request: {url}")

    response = requests.get(url)
    print(f"⬅️ response: {response.status_code} | {response.text}")

    if response.status_code == 200:
        data = response.json()

        if data["code"] != 0:
            raise Exception(f"Failed to start AdsPower profile: {data['msg']}")

        try:
            ws_url = data['data']['ws']['puppeteer']
            browser = playwright.chromium.connect_over_cdp(ws_url)
            context = browser.contexts[0] if browser.contexts else browser.new_context()
            page = context.new_page()

            return page, context, browser
        except KeyError:
            print("⚠️ The response does not contain the required key (data → ws → puppeteer)")
            return None
    else:
        print(f"❌ Unable to start AdsPower browser for profile {profile_id}")
        return None


if __name__ == "__main__":

    links = list(PinLink.objects.filter(status='Active').values('url'))
    links_map = [link['url'] for link in links]
    ads_profiles_id = ['kvvx92c', 'kvvx91g', 'kw1pmvs']

    with sync_playwright() as p:
        for profile_id in ads_profiles_id:
            print(f"\nWorking with (Profile: {profile_id})")

            try:
                page, context, browser = start_adspower_browser(profile_id, p)

            except Exception as e:
                print(f"Error: {type(e).__name__} - {e}")
                print(traceback.format_exc())
                print(f"Failed to unpack AdsPower browser instance: {e}")
                continue

            pinterest_pages = [pg for pg in context.pages if "pinterest.com" in pg.url]
            page = pinterest_pages[0] if pinterest_pages else context.new_page()
            page.bring_to_front()

            try:
                page, email = pinterest_login(page=page, profile=profile_id)
            except Exception as e:
                print(f"Login check failed: {e}")
                log_account_action(status="Action", message="Login check failed.", profile=profile_id)
                continue

            for url in links_map:
                print(f"Opening link: {url}")
                log_account_action(status="Action", message=f"Opening link: {url}", profile=profile_id, email=email)
                try:
                    perform_actions_on_pinlink(email=email, page=page, url=url, profile=profile_id)
                except (PlaywrightTimeoutError, PlaywrightError) as e:
                    log_account_action(status="Error", message=f"Error on {url}: {e}", profile=profile_id, email=email)
                    print(f"Error on {url}: {e}")
                    continue

            for tab in context.pages:
                try:
                    tab.close()
                except Exception:
                    pass

        if browser:
            browser.close()