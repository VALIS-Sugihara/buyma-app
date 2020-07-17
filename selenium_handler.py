from selenium import webdriver
from ec import lyst

class Chrome:
    def headless_lambda(self):
        options = webdriver.ChromeOptions()
        # options.binary_location = "/opt/python/bin/headless-chromium"
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--single-process")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1280x1696")
        options.add_argument("--disable-application-cache")
        options.add_argument("--disable-infobars")
        options.add_argument("--hide-scrollbars")
        options.add_argument("--enable-logging")
        options.add_argument("--log-level=0")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--homedir=/tmp")
    
        driver = webdriver.Chrome(
            # executable_path="/opt/python/bin/chromedriver",
            chrome_options=options
        )
        return driver

def selenium_test(event, context):
    chrome=Chrome()
    driver = chrome.headless_lambda()

    Lyst = lyst.Lyst()
    Activator = lyst.Activator(Lyst)
    Client = lyst.Client(Activator, driver)
    Client.search(keywords=["Margiela"])

    print(Client.soup)

    return True
    # driver.get('https://www.google.com')
    # screenshot(driver, "/tmp/shot1.png")
    # print(driver.page_source)
    # return driver.title
    # driver.quit()


def screenshot(driver, filename):
    # get width and height of the page
    w = driver.execute_script("return document.body.scrollWidth;")
    h = driver.execute_script("return document.body.scrollHeight;")

    # set window size
    driver.set_window_size(w,h)

    # Get Screen Shot
    driver.save_screenshot(filename)


selenium_test(1,1)