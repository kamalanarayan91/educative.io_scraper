import os

from selenium.webdriver.common.by import By

from src.Utility.OSUtility import OSUtility
from src.Logging.Logger import Logger
from src.ScraperType.CourseTopicScraper.ScraperModules.SeleniumBasicUtility import SeleniumBasicUtility
from src.Utility.FileUtility import FileUtility


class ScreenshotUtility:
    def __init__(self, configJson):
        self.browser = None
        self.fileUtils = FileUtility()
        self.osUtils = OSUtility(configJson)
        self.seleniumBasicUtils = SeleniumBasicUtility(configJson)
        selectorPath = os.path.join(os.path.dirname(__file__), "Selectors.json")
        self.selectors = self.fileUtils.loadJsonFile(selectorPath)["ScreenshotHtmlUtility"]
        self.logger = Logger(configJson, "ScreenshotHtmlUtility").logger


    def getFullPageScreenshot(self, topicName):
        self.logger.info(f"getFullPageScreenshot: Getting full page screenshot for {topicName}")
        rootContentSelector = self.selectors["rootContent"]
        self.seleniumBasicUtils.browser = self.browser
        try:
            canvas = self.browser.find_elements(By.XPATH, rootContentSelector)[-1]
            base64Png = self.screenshotAsCdp(canvas, 1)
            self.osUtils.sleep(2)
            self.logger.info("getFullPageScreenshot: Successfully Received Full Page Screenshot...")
            return base64Png
        except Exception as e:
            lineNumber = e.__traceback__.tb_lineno
            raise Exception(f"ScreenshotHtmlUtility:getFullPageScreenshot: {lineNumber}: {e}")


    def screenshotAsCdp(self, canvas, scale=1):
        try:
            self.logger.info("Taking screenshot as CDP")
            size, location = canvas.size, canvas.location
            width, height = size['width'], size['height']
            x, y = location['x'], location['y']

            params = {
                "format": "png",
                "captureBeyondViewport": True,
                "clip": {
                    "width": width,
                    "height": height,
                    "x": x,
                    "y": y,
                    "scale": scale
                }
            }
            screenshot = self.seleniumBasicUtils.sendCommand("Page.captureScreenshot", params)
            return screenshot['data']
        except Exception as e:
            lineNumber = e.__traceback__.tb_lineno
            raise Exception(f"ScreenshotUtility:screenshotAsCdp: {lineNumber}: {e}")