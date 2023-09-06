import os

from src.Logging.Logger import Logger
from src.Main.LoginAccount import LoginAccount
from src.ScraperMethod.ExtensionMethod.ScraperModules.ApiUtility import ApiUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.RemoveUtility import RemoveUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.ScreenshotHtmlUtility import ScreenshotHtmlUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.SeleniumBasicUtility import SeleniumBasicUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.ShowUtility import ShowUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.SingleFileUtility import SingleFileUtility
from src.ScraperMethod.ExtensionMethod.ScraperModules.UrlUtility import UrlUtility
from src.Utility.BrowserUtility import BrowserUtility
from src.Utility.FileUtility import FileUtility


class ExtensionScraper:
    def __init__(self, configJson):
        self.browser = None
        self.configJson = configJson
        self.logger = Logger(configJson, "ExtensionScraper").logger
        self.fileUtils = FileUtility()
        self.apiUtils = ApiUtility()
        self.urlUtils = UrlUtility()
        self.browserUtils = BrowserUtility(self.configJson)
        self.outputFolderPath = self.configJson["saveDirectory"]
        self.loginUtils = LoginAccount()
        self.seleniumBasicUtils = SeleniumBasicUtility()
        self.removeUtils = RemoveUtility()
        self.showUtils = ShowUtility()
        self.singleFileUtils = SingleFileUtility(configJson)
        self.screenshotHtmlUtils = ScreenshotHtmlUtility(configJson)


    def start(self):
        self.logger.info("ExtensionScraper initiated...")
        urlsTextFile = self.fileUtils.loadTextFile(self.configJson["courseUrlsFilePath"])
        for textFileUrl in urlsTextFile:
            try:
                self.logger.info(f"Started Scraping from Text File URL: {textFileUrl}")
                self.browser = self.browserUtils.loadBrowser()
                self.apiUtils.browser = self.browser
                self.loginUtils.browser = self.browser
                self.scrapeCourse(textFileUrl)
                print("Complete")
                while True:
                    pass
            except Exception as e:
                lineNumber = e.__traceback__.tb_lineno
                raise Exception(f"ExtensionScraper:start: {lineNumber}: {e}")
            finally:
                if self.browser is not None:
                    self.browser.quit()
        self.logger.info("ExtensionScraper completed.")


    def scrapeCourse(self, textFileUrl):
        try:
            courseTopicUrlsList = self.apiUtils.getCourseTopicUrlsList(textFileUrl)
            startIndex = courseTopicUrlsList.index(textFileUrl) if textFileUrl in courseTopicUrlsList else 0
            self.loginUtils.checkIfLoggedIn()
            courseCollectionsJson = self.apiUtils.getCourseCollectionsJson(textFileUrl)
            courseTitle = self.fileUtils.filenameSlugify(courseCollectionsJson["courseTitle"])
            coursePath = os.path.join(self.outputFolderPath, courseTitle)
            self.fileUtils.createFolderIfNotExists(coursePath)
            # with open("courseTopicUrls.txt", "w") as f:
            #     f.write(str(courseTopicUrlsList))
            # with open("courseCollectionsData.json", "w") as f:
            #     f.write(json.dumps(courseCollectionsJson))
            for topicIndex in range(startIndex, len(courseTopicUrlsList)):
                courseTopicUrl = courseTopicUrlsList[topicIndex]
                courseApiUrl = courseCollectionsJson["topicApiUrlList"][topicIndex]
                topicName = str(topicIndex) + "-" + self.fileUtils.filenameSlugify(
                    courseCollectionsJson["topicNameList"][topicIndex])
                self.logger.info(f"Scraping {topicName}: {courseTopicUrl}")
                self.loginUtils.checkIfLoggedIn()
                courseApiContentJson = self.apiUtils.getCourseApiContentJson(courseApiUrl)
                self.scrapeTopic(coursePath, topicName, courseApiContentJson, courseTopicUrl)
                # with open(f"courseApiContentJson{topicIndex}.json", "w") as f:
                #     f.write(json.dumps(courseApiContentJson))
        except Exception as e:
            lineNumber = e.__traceback__.tb_lineno
            raise Exception(f"ExtensionScraper:scrapeCourse: {lineNumber}: {e}")


    def scrapeTopic(self, coursePath, topicName, courseApiContentJson, courseTopicUrl):
        try:
            self.seleniumBasicUtils.browser = self.browser
            self.removeUtils.browser = self.browser
            self.showUtils.browser = self.browser
            self.singleFileUtils.browser = self.browser
            self.screenshotHtmlUtils.browser = self.browser
            self.browser.get(courseTopicUrl)
            self.seleniumBasicUtils.waitWebdriverToLoadTopicPage()
            self.browserUtils.scrollPage()
            self.seleniumBasicUtils.checkSomethingWentWrong()
            self.browserUtils.setWindowSize()
            self.removeUtils.removeBlurWithCSS()
            self.removeUtils.removeMarkAsCompleted()
            self.showUtils.showSingleMarkDownQuizSolution()
            self.showUtils.showCodeSolutions()
            self.showUtils.showHints()
            self.showUtils.showSlides()
            self.seleniumBasicUtils.addNameAttributeInNextBackButton()
            self.removeUtils.removeUnwantedElements()
            self.singleFileUtils.fixAllObjectTags()
            self.singleFileUtils.injectImportantScripts()
            self.singleFileUtils.makeCodeSelectable()
            courseTopicPath = os.path.join(coursePath, topicName)
            self.fileUtils.createFolderIfNotExists(courseTopicPath)
            if self.configJson["singleFileHTML"]:
                htmlPageData = self.singleFileUtils.getSingleFileHtml(topicName)
            else:
                htmlPageData = self.screenshotHtmlUtils.getFullPageScreenshotHtml(topicName)
            htmlFilePath = os.path.join(courseTopicPath, f"{topicName}.html")
            self.fileUtils.createTopicHtml(htmlFilePath, htmlPageData)
        except Exception as e:
            lineNumber = e.__traceback__.tb_lineno
            raise Exception(f"ExtensionScraper:scrapeTopic: {lineNumber}: {e}")