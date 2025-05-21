import traceback

from playwright.sync_api import TimeoutError

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
        return page, account.email

    try:
        page.goto("https://www.pinterest.com/", timeout=40000, wait_until="domcontentloaded")
        print("Get https://www.pinterest.com/")

        try:
            sign_up = page.wait_for_selector('//button[.//div[contains(text(), "Зареєструватися") or contains(text(), "Регистрация") or contains(text(), "Sign up")]]', timeout=10000)

            if not sign_up:
                print(f"Registration button not found. Continuing")
                log_account_action(profile=profile, status="Action", message="Registration button not found. Continuing")

                return page, account.email

            page.click('//button[.//div[contains(text(), "Зареєструватися") or contains(text(), "Регистрация") or contains(text(), "Sign up")]]')
            print("Click button 'Sign Up'")

            page.wait_for_selector('//input[@id="email"]', timeout=50000)
            page.fill('//input[@id="email"]', account.email)
            print("fill email")

            page.fill('//input[@id="password"]', account.password)
            print("fill password")

            start_date = datetime.strptime('1970-01-01', '%Y-%m-%d')
            end_date = datetime.strptime('2002-12-31', '%Y-%m-%d')

            random_days = random.randint(0, (end_date - start_date).days)
            random_birthdate = start_date + timedelta(days=random_days)
            birthdate_str = random_birthdate.strftime('%Y-%m-%d')

            page.wait_for_selector('//input[@id="birthdate"]', timeout=50000)
            page.fill('//input[@id="birthdate"]', birthdate_str)
            print(f"birthdate fill: {birthdate_str}")

            button_xpath = '//button[div/div[contains(text(), "Продолжить") or contains(text(), "Continue") or contains(text(), "Продовжити")]]'
            page.wait_for_selector(button_xpath, timeout=10000)
            page.click(button_xpath)
            print("Click button 'Continue'")

            time.sleep(random.uniform(2, 4))

            page.wait_for_selector(button_xpath, state="detached", timeout=30000)

            log_account_action(email=account.email, profile=profile,  status="Login",  message="Logged in.")

            return page, account.email

        except TimeoutError:
            print("No Sign Up button found — already logged in?")
            log_account_action(profile=profile, status="Action", message="Already logged in.")
            return page, account.email


    except TimeoutError as e:
        print(f"Error: {type(e).__name__} - {e}")
        print(traceback.format_exc())
        log_account_action(profile=profile, status="Error", message=f"{type(e).__name__} - {e}")

        return page, account.email



