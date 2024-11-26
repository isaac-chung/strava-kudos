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
            raise Exception("Must set environ variables EMAIL AND PASSWORD. \
                e.g. run export STRAVA_EMAIL=YOUR_EMAIL")

        self.max_run_duration = max_run_duration
        self.start_time = time.time()
        self.num_entries = 100
        self.web_feed_entry_pattern = '[data-testid=web-feed-entry]'

        p = sync_playwright().start()
        self.browser = p.firefox.launch() # does not work in chrome
        self.page = self.browser.new_page()


    def email_login(self):
        """
        Login using email and password
        """
        self.page.goto(os.path.join(BASE_URL, 'login'))
        try:
            self.page.get_by_role("button", name="Reject").click(timeout=5000)
        except Exception as _:
            pass
        self.page.get_by_role("textbox", name='email').fill(self.EMAIL)
        self.page.get_by_role("textbox", name="password").fill(self.PASSWORD)
        self.page.get_by_role("button", name="Log In").click()
        print("---Logged in!!---")
        self._run_with_retries(func=self._get_page_and_own_profile)
        
    def _run_with_retries(self, func, retries=3):
        """
        Retry logic with sleep in between tries.
        """
        for i in range(retries):
            if i == retries - 1:
                raise Exception(f"Retries {retries} times failed.")
            try:
                func()
                return
            except Exception as _:
                time.sleep(1)

    def _get_page_and_own_profile(self):
        """
        Limit activities count by GET parameter and get own profile ID.
        """
        self.page.goto(os.path.join(BASE_URL, f"dashboard?num_entries={self.num_entries}"))

        ## Scrolling for lazy loading elements.
        for _ in range(5):
            self.page.keyboard.press('PageDown')
            time.sleep(0.5)
            self.page.keyboard.press('PageUp')

        try:
            self.own_profile_id = self.page.locator(".user-menu > a").get_attribute('href').split("/athletes/")[1]
            print("id", self.own_profile_id)
        except Exception as _:
            print("can't find own profile ID")

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

            # check if feed item is a club post
            if self.is_club_post(web_feed):
                print('c', end='')
                continue

            # check if activity has multiple participants
            if p_count > 1:
                for j in range(p_count):
                    participant = web_feed.get_by_test_id("entry-header").nth(j)
                    # ignore own activities
                    if not self.is_participant_me(participant):
                        kudos_container = web_feed.get_by_test_id("kudos_comments_container").nth(j)
                        button = self.find_unfilled_kudos_button(kudos_container)
                        given_count += self.click_kudos_button(unfilled_kudos_container=button)
            else:
                # ignore own activities
                if not self.is_participant_me(web_feed):
                    button = self.find_unfilled_kudos_button(web_feed)
                    given_count += self.click_kudos_button(unfilled_kudos_container=button)
        print(f"\nKudos given: {given_count}")
        return given_count
    
    def is_club_post(self, container) -> bool:
        """
        Returns true if the container is a club post
        """
        if(container.get_by_test_id("group-header").count() > 0):
            return True
        
        if(container.locator(".clubMemberPostHeaderLinks").count() > 0):
            return True

        return False
    
    def is_participant_me(self, container) -> bool:
        """
        Returns true is the container's owner is logged-in user.
        """
        owner = self.own_profile_id
        try:
            h = container.get_by_test_id("owners-name").get_attribute('href')
            hl = h.split("/athletes/")
            owner = hl[1]
        except Exception as _:
            print("Some issue with getting owners-name container.")
        return owner == self.own_profile_id
    
    def find_unfilled_kudos_button(self, container):
        """
        Returns button as a playwright.locator class
        """
        button = None
        try:
            button = container.get_by_test_id("unfilled_kudos")
        except Exception as _:
            print("Some issue with finding the unfilled_kudos container.")
        return button

    def click_kudos_button(self, unfilled_kudos_container) -> int:
        """
        input: playwright.locator class
        Returns 1 if kudos button was clicked else 0
        """
        if unfilled_kudos_container.count() == 1:
            unfilled_kudos_container.click(timeout=0, no_wait_after=True)
            print('=', end='')
            time.sleep(1)
            return 1
        return 0

    def give_kudos(self):
        """
        Interate over web feed entries
        """
        ## Give Kudos on loaded page ##
        try:
            self.page.get_by_role("button", name="Accept").click(timeout=5000)
            print("Accepting updated terms.")
        except Exception as _:
            pass
        web_feed_entry_locator = self.page.locator(self.web_feed_entry_pattern)
        self.locate_kudos_buttons_and_maybe_give_kudos(web_feed_entry_locator=web_feed_entry_locator)
        self.browser.close()


def main():
    kg = KudosGiver()
    kg.email_login()
    kg.give_kudos()


if __name__ == "__main__":
    main()
