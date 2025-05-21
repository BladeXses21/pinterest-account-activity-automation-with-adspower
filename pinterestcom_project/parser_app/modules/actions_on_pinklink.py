import random
import time
from logger import log_account_action
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


BASE_TIMEOUT = 40000


def random_mouse_move(page, profile, email=None):
    try:
        viewport = page.viewport_size
        if viewport is None:
            viewport = page.evaluate("() => ({ width: window.innerWidth, height: window.innerHeight })")

        width = viewport['width']
        height = viewport['height']

        for _ in range(random.randint(3, 7)):
            x = random.randint(0, width)
            y = random.randint(0, height)
            page.mouse.move(x, y, steps=random.randint(5, 20))
            time.sleep(random.uniform(0.1, 0.5))

        print(f"Random mouse movements performed.")
        log_account_action(email=email, profile=profile, status="Action", message="Random mouse movements performed.")
    except Exception as e:
        log_account_action(email=email, profile=profile, status="Error", message=f"Error in random_mouse_move: {e}")
        print(f"Error in random_mouse_move: {e}")


def random_scroll(page, profile, email=None):
    """Random scroll"""

    scroll_distance = random.randint(100, 500)
    page.mouse.wheel(0, scroll_distance)
    print(f"Scrolled {scroll_distance} pixels")
    log_account_action(email=email, profile=profile, status="Action", message="Scrolled {scroll_distance} pixels")
    time.sleep(random.uniform(1, 3))


def like_photo(page, profile, email=None):
    """Like the image"""

    try:
        like_button = page.wait_for_selector("//div[@aria-label='reaction']", timeout=BASE_TIMEOUT)

        if like_button:
            like_button.click()
            print("Liked the photo.")
            log_account_action(email=email, profile=profile, status="Action", message="Liked the photo.")
            time.sleep(random.uniform(2, 3))
        else:
            log_account_action(email=email, profile=profile, status="Failed", message="Like button not found.")
            print("Like button not found.")

    except PlaywrightTimeoutError:
        log_account_action(email=email, profile=profile, status="Failed", message="Timeout: Like button not found.")
        print("Timeout: Like button not found.")


def write_comment(page, profile, email=None):
    """Write a comment under the pin"""

    comments = [
        "Amazing post!", "So inspiring", "Love This", "Cool","✨", "This is perfect", "🔥", "Saved this, thanks!",
        "❤", "😍", "🔥🔥🔥", "🤍", "💛", "💙", "Turned out great!", "Thank you.", "🧐", "😊", "🤩", "Wow!", "Awesome", "🤯", "💛",
        "Beautiful work 👏", "Just wow 🤯", "👀", "👏", "⚡️", "Absolutely stunning 🔥", "Such a vibe! ✨", "Incredible 😍",
        "Well done! 👌", "looks amazing"
    ]

    chosen_comment = random.choice(comments)

    try:
        comment_box = page.wait_for_selector('//div[@contenteditable="true" and (contains(@aria-label, "Додати коментар") or contains(@aria-label, "Add a comment"))]',
                                        timeout=BASE_TIMEOUT)
        if comment_box:
            comment_box.click()
            page.keyboard.press("Enter")

            time.sleep(random.uniform(2, 3))
            comment_box.type(chosen_comment, delay=100)

            time.sleep(random.uniform(2, 3))
            page.keyboard.press("Enter")

            post_button = page.wait_for_selector("//button[@aria-label='Post']", timeout=BASE_TIMEOUT)

            if post_button:
                post_button.click()
                page.wait_for_selector(f"//div[contains(text(), '{chosen_comment}')]", timeout=BASE_TIMEOUT)
                print(f"Successfully posted comment: {chosen_comment}")
                log_account_action(email=email, profile=profile, status="Action", message=f"Commented: {chosen_comment}")

            else:
                print("Post button not found after writing comment.")
                log_account_action(email=email, profile=profile, status="Failed", message="Post button not found after writing comment.")

            time.sleep(random.uniform(2, 3))

        else:
            log_account_action(email=email, profile=profile, status="Failed", message="Comment box not found")
            print("Comment box not found")

    except Exception as e:
        print(f"Failed to write comment: {e}")
        log_account_action(email=email, profile=profile, status="Error", message=f"Failed to write comment: {e}")



def save_pin(page, profile, email=None):
    """Save the pin"""

    try:
        save_button = page.wait_for_selector('//button[@aria-label="Save" or @aria-label="Зберегти" or @aria-label="Сохранить"]', timeout=BASE_TIMEOUT)

        if save_button:
            save_button.click()
            print("Pin Saves")
            log_account_action(email=email, profile=profile, status="Action", message="Pin Saves")
            time.sleep(random.uniform(1, 2))
        else:
            log_account_action(email=email, profile=profile, status="Failed", message="Save button not found")
            print("Save button not found")

    except PlaywrightTimeoutError as e:
        log_account_action(email=email, profile=profile, status="Error", message=f"Failed to save pin: {e}")
        print(f"Failed to save pin: {e}")


def visit_external_website(page, profile, email=None):
    """Go to an external site from a post link"""

    page.wait_for_selector("//div[@class='Jea KS5 mQ8 zI7 iyn Hsu']", timeout=50000)
    website_link = page.query_selector('div[data-test-id="visit-site-button"]')

    if website_link:
        with page.context.expect_page() as new_page_info:
            website_link.click()

        new_page = new_page_info.value
        new_page.wait_for_load_state("domcontentloaded")

        if not new_page.url or "error" in new_page.url:
            print("The external website did not load properly. Closing the tab.")
            log_account_action(email=email, profile=profile, status="Failed", message="The external website did not load properly. Closing the tab.")
            new_page.close()

            page.bring_to_front()
            page.goto("https://www.pinterest.com/homefeed/")
            new_page.wait_for_load_state("domcontentloaded")
            log_account_action(email=email, profile=profile, status="Action", message="Returned to homefeed page.")
            print("Returned to homefeed.")

        print("Successfully visited an external website.")
        log_account_action(email=email, profile=profile, status="Action", message="Successfully visited an external website.")
        time.sleep(random.uniform(3, 5))

        random_mouse_move(page=new_page, profile=profile, email=email)
        random_scroll(page=new_page, profile=profile, email=email)

        new_page.close()
        page.bring_to_front()

        print("Returning to homefeed and repeating actions.")
        log_account_action(email=email, profile=profile, status="Success", message="Returning to homefeed and repeating actions.")
    else:
        log_account_action(email=email, profile=profile, status="Failed", message="Failed to retrieve page from post, returning to page /homefeed/")
        print(f"Failed to retrieve page from post, returning to page /homefeed/")
        page.goto("https://www.pinterest.com/homefeed/")
        page.wait_for_load_state("domcontentloaded")


def perform_random_actions(page, profile, email=None):
    """Run random actions on a pin"""

    action = [like_photo, write_comment, save_pin, visit_external_website]
    random.shuffle(action)

    for action in action[:random.randint(1, 3)]:

        try:
            action(page=page, profile=profile, email=email)

        except Exception as e:
            log_account_action(email=email, profile=profile, status="Failed", message=f"Failed action {action.__name__}: {e}")
            print(f"Failed action {action.__name__}: {e}")


def perform_actions_on_pinlink(page, url, profile, email=None):
    """Link actions with PinLink"""

    page.goto(url, timeout=90000, wait_until="domcontentloaded")
    page.wait_for_load_state("domcontentloaded")
    log_account_action(email=email, profile=profile, status="Success", message="Pinlink successfully loaded")

    print(f"Visiting pin link: {url}")
    time.sleep(random.uniform(2, 4))

    random_mouse_move(page=page, profile=profile, email=email)
    random_scroll(page=page, profile=profile, email=email)

    perform_random_actions(page=page, profile=profile, email=email)
