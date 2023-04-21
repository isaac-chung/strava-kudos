import os
import time

from playwright.sync_api import sync_playwright

BASE_URL = "https://www.strava.com/"

class KudosGiver:
    """
    Logins into Strava and gives kudos to all activities under
    Following.
    """
    def __init__(self, max_run_duration=540) -> None:
        self.EMAIL = os.environ.get('STRAVA_EMAIL')
        self.PASSWORD = os.environ.get('STRAVA_PASSWORD')

        if self.EMAIL is None or self.PASSWORD is None:
            raise Exception(f"Must set environ variables EMAIL AND PASSWORD. \
                e.g. run export STRAVA_EMAIL=YOUR_EMAIL")

        self.max_run_duration = max_run_duration
        self.start_time = time.time()
        self.num_entries = 200
        self.web_feed_entry_pattern = '[data-testid=web-feed-entry]'

        p = sync_playwright().start()
        self.browser = p.firefox.launch() # does not work in chrome
        self.page = self.browser.new_page()


    def email_login(self):
        """
        Login using email and password
        """
        self.page.goto(os.path.join(BASE_URL, 'login'))
        self.page.fill('#email', self.EMAIL)
        self.page.fill("#password", self.PASSWORD)
        self.page.click("button[type='submit']")
        print("---Logged in!!---")
        # limit activities count by GET parameter
        self.page.goto(os.path.join(BASE_URL, f"dashboard?num_entries={self.num_entries}"), wait_until="networkidle")
        self.own_profile_id = self.page.locator("#athlete-profile .card-body > a").get_attribute('href').split("/athletes/")[1]
        print(f"own_profile_id: {self.own_profile_id}")


    def locate_kudos_buttons_and_maybe_give_kudos(self, web_feed_entry_locator) -> int:
        """
        input: playwright.locator class
        Returns count of kudos given.
        """
        w_count = web_feed_entry_locator.count()
        given_count = 0
        print(f"web feeds found: {w_count}")
        for i in range(w_count):
            # run condition check
            curr_duration = time.time() - self.start_time
            if curr_duration > self.max_run_duration:
                print("Max run duration reached.")
                break

            web_feed = web_feed_entry_locator.nth(i)
            p_count = web_feed.get_by_test_id("entry-header").count()

            # check if activity has multiple participants
            if p_count > 1:
                print(f"Found multiple list entries: {p_count}")
                for j in range(p_count):
                    participant = web_feed.get_by_test_id("entry-header").nth(j)
                    # ignore own activities
                    if participant.get_by_test_id("owners-name").get_attribute('href').split("/athletes/")[1] != self.own_profile_id:
                        kudos_container = web_feed.get_by_test_id("kudos_comments_container").nth(j)
                        button = kudos_container.get_by_test_id("unfilled_kudos")
                        given_count += self.click_kudos_button(unfilled_kudos_container=button)
            else:
                # ignore own activities
                if web_feed.get_by_test_id("owners-name").get_attribute('href').split("/athletes/")[1] != self.own_profile_id:
                    button = web_feed.get_by_test_id("unfilled_kudos")
                    given_count += self.click_kudos_button(unfilled_kudos_container=button)
        print(f"Kudos given: {given_count}")
        return given_count

    def click_kudos_button(self, unfilled_kudos_container) -> int:
        """
        input: playwright.locator class
        Returns 1 if kudos button was clicked else 0
        """
        if unfilled_kudos_container.count() == 1:
            unfilled_kudos_container.click(timeout=0, no_wait_after=True)
            print("Kudos button clicked")
            time.sleep(1)
            return 1
        return 0

    def give_kudos(self):
        """
        Interate over web feed entries
        """
        ## Give Kudos on loaded page ##
        web_feed_entry_locator = self.page.locator(self.web_feed_entry_pattern)
        self.locate_kudos_buttons_and_maybe_give_kudos(web_feed_entry_locator=web_feed_entry_locator)
        self.browser.close()


def main():
    kg = KudosGiver()
    kg.email_login()
    kg.give_kudos()


if __name__ == "__main__":
    main()
