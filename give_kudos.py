import os
import time
import send_telegram

from playwright.sync_api import sync_playwright, TimeoutError

BASE_URL = "https://www.strava.com/"

class KudosGiver:
    """
    Logins into Strava and gives kudos to all activities under
    Following. Additionally, scrolls down to check for more activities
    until no more kudos can be given at this time.
    """
    def __init__(self, max_retry_scroll=3, max_run_duration=540) -> None:
        self.EMAIL = os.environ.get('STRAVA_EMAIL')
        self.PASSWORD = os.environ.get('STRAVA_PASSWORD')

        if self.EMAIL is None or self.PASSWORD is None:
            raise Exception(f"Must set environ variables EMAIL AND PASSWORD. \
                e.g. run export STRAVA_EMAIL=YOUR_EMAIL")

        self.max_retry_scroll = max_retry_scroll
        self.max_run_duration = max_run_duration
        self.kudos_button_pattern = '[data-testid="kudos_button"]'
        p = sync_playwright().start()
        self.browser = p.firefox.launch() # does not work in chrome
        self.page = self.browser.new_page()
        
        self.start_time = time.time()


    def email_login(self):
        """
        Login using email and password
        """
        self.page.goto(os.path.join(BASE_URL, 'login'))
        self.page.fill('#email', self.EMAIL)
        self.page.fill("#password", self.PASSWORD)
        self.page.click("button[type='submit']")
        print("---Logged in!!---")
        self.page.goto(os.path.join(BASE_URL, "dashboard"), wait_until="domcontentloaded")
        

    def locate_kudos_buttons_and_maybe_give_kudos(self, button_locator) -> int:
        """
        input: playwright.locator class
        Returns count of kudos given.
        """
        b_count= button_locator.count()
        given_count = 0
        for i in range(b_count):
            button = button_locator.nth(i)
            if button.get_by_test_id("unfilled_kudos").count():
                try:
                    button.click(timeout=1000)
                    given_count += 1
                    time.sleep(1)
                except TimeoutError:
                    print("Click timed out.")
        print(f"Kudos given: {given_count}")
        return given_count

    def give_kudos(self):
        """
        Scroll through pages to give kudos that are giveable.
        """
        ## Give Kudos on loaded page ##
        button_locator = self.page.locator(self.kudos_button_pattern)
        kudos_given = self.locate_kudos_buttons_and_maybe_give_kudos(button_locator=button_locator)
        curr_retry = self.max_retry_scroll

        ## Scroll down and repeat ##
        while kudos_given or curr_retry > 0:
            curr_duration = time.time() - self.start_time
            if curr_duration > self.max_run_duration:
                print("Max run duration reached.")
                break
            self.page.mouse.wheel(0, 12000)
            time.sleep(5)
            kudos_given = self.locate_kudos_buttons_and_maybe_give_kudos(button_locator=button_locator)
            if not kudos_given:
                curr_retry -= 1
        send_telegram.send_to_telegram('send_telegram.send_to_telegram')
        print("That's all, folks! Terminating... ")

        self.browser.close()
        

def main():
    send_telegram.send_to_telegram('Trying to give kudos')
    kg = KudosGiver()
    kg.email_login()
    kg.give_kudos()


if __name__ == "__main__":
    main()
