"""
Instagram Reel Chat Sender — Selenium Automation
=================================================
Sends a Reel link to one or more Instagram users via DM.

⚠️  DISCLAIMER:
    This script is for personal/educational use ONLY.
    Automating Instagram actions violates their Terms of Service.
    Use responsibly — add delays, don't spam, don't use on accounts
    you can't afford to lose. You have been warned.

Requirements:
    pip install selenium webdriver-manager

Usage:
    1. Fill in your credentials and targets below (or use .env).
    2. Run: python instagram_reel_sender.py
"""

import time
import random
import logging
from dataclasses import dataclass, field
from typing import List

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

# ─── Logging Setup ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("IGReelSender")


# ─── Config ───────────────────────────────────────────────────────────────────
@dataclass
class Config:
    username: str = "your_instagram_username"
    password: str = "your_instagram_password"

    # Reel URL to send
    reel_url: str = "https://www.instagram.com/reel/XXXXXXXXXXX/"

    # Optional message to accompany the Reel link
    message: str = "Check this out! 🔥"

    # List of Instagram usernames to send to
    targets: List[str] = field(default_factory=lambda: [
        "target_username_1",
        "target_username_2",
    ])

    # Delays (seconds) — keep these realistic to avoid detection
    delay_between_actions: tuple = (2, 4)   # random range
    delay_between_users:   tuple = (8, 15)  # random range between DMs

    headless: bool = False  # Set True to run without browser window


# ─── Helper ───────────────────────────────────────────────────────────────────
def human_delay(range_: tuple):
    """Sleep for a random duration to mimic human timing."""
    t = random.uniform(*range_)
    time.sleep(t)


# ─── Bot Class ────────────────────────────────────────────────────────────────
class InstagramReelSender:
    BASE_URL = "https://www.instagram.com"
    TIMEOUT  = 15  # seconds for WebDriverWait

    def __init__(self, config: Config):
        self.cfg     = config
        self.driver  = None
        self.wait    = None
        self.results = {}  # username -> "sent" | "failed" | "not found"

    # ── Driver Setup ──────────────────────────────────────────────────────────
    def _init_driver(self):
        options = webdriver.ChromeOptions()
        if self.cfg.headless:
            options.add_argument("--headless=new")

        # Anti-detection flags
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1280,900")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.wait = WebDriverWait(self.driver, self.TIMEOUT)
        log.info("Browser launched.")

    # ── Login ─────────────────────────────────────────────────────────────────
    def login(self):
        log.info("Navigating to Instagram login…")
        self.driver.get(f"{self.BASE_URL}/accounts/login/")
        human_delay(self.cfg.delay_between_actions)

        # Accept cookies if prompted
        try:
            cookie_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Allow')]"))
            )
            cookie_btn.click()
            human_delay((1, 2))
        except TimeoutException:
            pass  # No cookie dialog

        # Enter credentials
        username_field = self.wait.until(EC.presence_of_element_located((By.NAME, "username")))
        password_field = self.driver.find_element(By.NAME, "password")

        username_field.clear()
        for char in self.cfg.username:
            username_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        password_field.clear()
        for char in self.cfg.password:
            password_field.send_keys(char)
            time.sleep(random.uniform(0.05, 0.12))

        password_field.send_keys(Keys.RETURN)
        log.info("Credentials submitted. Waiting for home feed…")
        human_delay((4, 6))

        # Dismiss "Save Login Info" / "Turn on Notifications" popups
        for _ in range(2):
            try:
                not_now = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
                )
                not_now.click()
                human_delay((1, 2))
            except TimeoutException:
                break

        log.info("Login successful ✓")

    # ── Open DM with a user ───────────────────────────────────────────────────
    def _open_dm(self, target_username: str) -> bool:
        """Navigate to the DM thread for target_username. Returns True on success."""
        dm_url = f"{self.BASE_URL}/direct/new/"
        self.driver.get(dm_url)
        human_delay(self.cfg.delay_between_actions)

        try:
            # Search box inside new-message dialog
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search…']"))
            )
            search_box.send_keys(target_username)
            human_delay((1.5, 2.5))

            # Click the matching result
            result = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//span[contains(text(),'{target_username}')]")
                )
            )
            result.click()
            human_delay((1, 2))

            # Confirm with the "Next" / "Chat" button
            next_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[text()='Next' or text()='Chat']")
                )
            )
            next_btn.click()
            human_delay(self.cfg.delay_between_actions)
            return True

        except (TimeoutException, NoSuchElementException) as e:
            log.warning(f"Could not open DM with @{target_username}: {e}")
            return False

    # ── Send message in open DM thread ───────────────────────────────────────
    def _send_message(self, text: str) -> bool:
        """Type and send a message in the currently open DM thread."""
        try:
            msg_box = self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@aria-label='Message' and @contenteditable='true'] | "
                               "//textarea[@placeholder]")
                )
            )
            msg_box.click()
            human_delay((0.5, 1))

            for char in text:
                msg_box.send_keys(char)
                time.sleep(random.uniform(0.03, 0.09))

            human_delay((0.5, 1))
            msg_box.send_keys(Keys.RETURN)
            human_delay(self.cfg.delay_between_actions)
            return True

        except (TimeoutException, NoSuchElementException) as e:
            log.warning(f"Could not send message: {e}")
            return False

    # ── Main Send Loop ────────────────────────────────────────────────────────
    def send_reel_to_all(self):
        full_message = f"{self.cfg.message}\n{self.cfg.reel_url}"

        for i, target in enumerate(self.cfg.targets, 1):
            log.info(f"[{i}/{len(self.cfg.targets)}] Sending to @{target}…")

            opened = self._open_dm(target)
            if not opened:
                self.results[target] = "not found / DM failed"
                continue

            sent = self._send_message(full_message)
            self.results[target] = "✅ sent" if sent else "❌ failed"
            log.info(f"  → @{target}: {self.results[target]}")

            if i < len(self.cfg.targets):
                wait_time = random.uniform(*self.cfg.delay_between_users)
                log.info(f"  Waiting {wait_time:.1f}s before next user…")
                time.sleep(wait_time)

    # ── Run ───────────────────────────────────────────────────────────────────
    def run(self):
        try:
            self._init_driver()
            self.login()
            self.send_reel_to_all()
        except Exception as e:
            log.error(f"Unexpected error: {e}", exc_info=True)
        finally:
            self._print_summary()
            if self.driver:
                self.driver.quit()
                log.info("Browser closed.")

    def _print_summary(self):
        log.info("\n" + "═" * 40)
        log.info("  SUMMARY")
        log.info("═" * 40)
        for user, status in self.results.items():
            log.info(f"  @{user:30s}  {status}")
        log.info("═" * 40)


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    cfg = Config(
        username  = "your_instagram_username",   # ← change
        password  = "your_instagram_password",   # ← change
        reel_url  = "https://www.instagram.com/reel/XXXXXXXXXXX/",  # ← change
        message   = "Bro check this out! 🔥",   # ← change
        targets   = [                             # ← change
            "target_username_1",
            "target_username_2",
        ],
        headless  = False,   # True = no visible browser
    )

    bot = InstagramReelSender(cfg)
    bot.run()