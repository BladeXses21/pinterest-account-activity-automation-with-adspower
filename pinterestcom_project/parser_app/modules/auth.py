import traceback

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

import random
import time
from datetime import datetime, timedelta

from logger import log_account_action

from load_django import *
from parser_app.models import AccountLog, Account

def pinterest_login(page, profile):

    account = Account.objects.filter(profile_id=profile, status='Active').first()

    if not account:
        print("No active Pinterest accounts found.")
        log_account_action(profile=profile, status="Error", message="No Pinterest account for this profile.")
        return page, None, False

    try:
        page.goto("https://www.pinterest.com/", timeout=50000, wait_until="domcontentloaded")
        print("Get https://www.pinterest.com/")

        try:
            profile_element = page.wait_for_selector('//div[@data-test-id="header-profile"]//a', timeout=50000)

            if profile_element:
                log_account_action(profile=profile, status="Action", message="Account already — already logged in")
                return page, account.email, True

        except PlaywrightTimeoutError as e:
            print(f"Maybe the account was not logged in.")
            log_account_action(profile=profile, status="Info", message=f"Maybe the account was not logged in.")

            try:
                login = page.wait_for_selector('//button[div/div[contains(text(), "Войти") or contains(text(), "Log in") or contains(text(), "Увійти")]]', timeout=70000)

                login.click()
                print("Click button 'Log in'")

                page.wait_for_selector('//input[@id="email"]', timeout=50000)
                page.fill('//input[@id="email"]', account.email)
                print("fill email")

                page.fill('//input[@id="password"]', account.password)
                print("fill password")

                login_button = page.wait_for_selector('//button[@type="submit"]', timeout=50000)
                page.click('//button[@type="submit"]', force=True)
                print("Click button 'Log In #2'")

                time.sleep(random.uniform(2, 4))

                page.wait_for_selector('//button[@type="submit"]', state="detached", timeout=70000)

                try:
                    page.wait_for_selector('//div[@data-test-id="header-profile"]//a', timeout=60000)
                    print("Login successful.")
                    log_account_action(email=account.email, profile=profile, status="Login", message="Logged in.")
                    return page, account.email, True

                except PlaywrightTimeoutError:
                    print("Login failed - profile not found after login.")
                    log_account_action(profile=profile, status="Error", message="Login failed - profile not found after login.")
                    return page, account.email, False

            except PlaywrightTimeoutError:
                print("No Log in button found.")
                log_account_action(profile=profile, status="Action", message="Log in button not found.")
                return page, account.email, False


    except PlaywrightTimeoutError as e:
        print(f"Error: {type(e).__name__} - {e}")
        print(traceback.format_exc())
        log_account_action(profile=profile, status="Error", message=f"{type(e).__name__} - {e}")

        return page, account.email, False



