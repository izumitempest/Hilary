import logging
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

logger = logging.getLogger(__name__)


def run_login_flow():
    logger.info("Starting Playwright session")
    with sync_playwright() as p:
        browser = None
        try:
            browser = p.chromium.launch(headless=True)
            logger.info("Browser launched")

            page = browser.new_page()
            logger.info("New page created")

            logger.info("Navigating to login page")
            page.goto("https://example.com/login", timeout=30000)
            logger.info("Page loaded: %s", page.url)

            logger.info("Filling username field")
            page.fill("#username", "myuser")
            logger.info("Filling password field")
            page.fill("#password", "mypass")

            logger.info("Submitting the login form")
            page.click("#submit")
            page.wait_for_load_state("networkidle", timeout=10000)
            logger.info("Submit clicked and page is idle")

            # Confirm that navigation happened or expected element exists
            if page.url != "https://the-internet.herokuapp.com/login":
                logger.info("Navigation appears successful to %s", page.url)
            else:
                logger.warning("Still on login page after submit; verify selectors and credentials")

            logger.info("Login flow completed successfully")
            return True
        except PlaywrightTimeoutError as err:
            logger.exception("Playwright timeout error during execution: %s", err)
            return False
        except Exception as err:
            logger.exception("Unexpected error during Playwright execution: %s", err)
            return False
        finally:
            if browser:
                browser.close()
                logger.info("Browser closed")


if __name__ == "__main__":
    success = run_login_flow()
    if success:
        logger.info("Script executed successfully")
    else:
        logger.error("Script execution failed")
        raise SystemExit(1)