from playwright.sync_api import Playwright, sync_playwright, Page, Browser
from core.logger import logger
from utils import Singleton

class PlaywrightRuntime(metaclass=Singleton):
    playwright: Playwright
    browser: Browser
    browser_page: Page

    def __init__(self):
        logger.warning("initialising playwright ...")
        self.playwright: Playwright = None
        self.browser: Browser = None
        self.browser_page: Page = None


    def initialize(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=True)
        self.browser_page = self.browser.new_context().new_page()

    def free(self):
        self.browser_page.close()
        self.browser.close()
        self.playwright.stop()
