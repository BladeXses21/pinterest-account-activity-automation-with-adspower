import requests
from playwright.sync_api import sync_playwright
from actions_on_pinklink import perform_actions_on_pinlink
from auth import pinterest_login
from parser_app.models import Account, PinLink, AccountLog
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, Error as PlaywrightError
from logger import log_account_action
import traceback
from proxy_rotator import rotate_ip


# ads_profiles_id = ['kvvx92c', 'kvvx91g', 'kw1pmvs']
# ads_profiles_id = ['kwofqtq', 'kwohf6w']

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


def close_adspower_browser(profile_id):
    try:
        url = f"http://127.0.0.1:50325/api/v1/browser/stop?user_id={profile_id}"
        response = requests.get(url)
        if response.status_code == 200 and response.json().get("code") == 0:
            print(f"✅ AdsPower browser for profile {profile_id} successfully stopped.")
        else:
            print(f"⚠️ Failed to stop AdsPower browser for profile {profile_id}: {response.text}")
    except Exception as e:
        print(f"⚠️ Error while trying to stop AdsPower browser for profile {profile_id}: {e}")


if __name__ == "__main__":

    links = list(PinLink.objects.filter(status='Active').values('url'))
    links_map = [link['url'] for link in links]

    ads_profiles = Account.objects.filter(status='Active')

    with sync_playwright() as p:
        for profile in ads_profiles:
            profile_id = profile.profile_id
            print(f"\nWorking with (Profile: {profile_id})")

            print(f"🔄 Rotating proxy before working with profile {profile_id}...")
            success = rotate_ip()
            if not success:
                print(f"Failed to rotate proxy before working with {profile_id}. Skipping this profile.")
                continue

            try:
                page, context, browser = start_adspower_browser(profile_id, p)

                pinterest_pages = [pg for pg in context.pages if "pinterest.com" in pg.url]
                page = pinterest_pages[0] if pinterest_pages else context.new_page()
                page.bring_to_front()

                page, email, status = pinterest_login(page=page, profile=profile_id)

                if status is False:
                    print(f"Pinterest login failed for profile {profile_id}. Skipping this profile.")
                    raise Exception(f"Pinterest login failed for profile {profile_id}")

                for url in links_map:
                    print(f"Opening link: {url}")
                    log_account_action(status="Action", message=f"Opening link: {url}", profile=profile_id, email=email)
                    try:
                        perform_actions_on_pinlink(email=email, page=page, url=url, profile=profile_id)
                    except (PlaywrightTimeoutError, PlaywrightError) as e:
                        log_account_action(status="Error", message=f"Error on {url}: {e}", profile=profile_id, email=email)
                        print(f"Error on {url}: {e}")
                        continue

            except Exception as e:
                print(f"❌ Error occurred: {type(e).__name__} - {e}")
                print(traceback.format_exc())
                log_account_action(status="Error", message=str(e), profile=profile_id)

            finally:
                if browser:
                    try:
                        close_adspower_browser(profile_id)
                        for tab in context.pages:
                            try:
                                tab.close()
                            except Exception:
                                pass
                        browser.close()
                        print(f"✅ Closed AdsPower browser for profile {profile_id}")
                        log_account_action(status="Success", message=f"Closed AdsPower browser for profile {profile_id}", profile=profile_id)
                    except Exception as close_err:
                        log_account_action(status="Error", message=f"Failed to properly close browser: {close_err}", profile=profile_id)
                        print(f"⚠️ Failed to properly close browser: {close_err}")