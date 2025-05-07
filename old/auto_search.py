from dotenv import load_dotenv
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.common import NoSuchElementException, ElementNotInteractableException

# Get login info
load_dotenv()
user = os.getenv("USERNAME")
pwd = os.getenv("PASSWORD")

# Set up Firefox driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(0.5)
wait = WebDriverWait(driver, timeout=2)

# Open contensis
driver.get("https://cms-chesheast.cloud.contensis.com/Default.aspx")

# Log in
user_input = driver.find_element(by=By.NAME, value="_Textbox_Username")
pwd_input = driver.find_element(by=By.NAME, value="_Textbox_Password")
login_btn = driver.find_element(by=By.NAME, value="ctl39")
user_input.send_keys(user)
pwd_input.send_keys(pwd)
login_btn.click()

# Search for old media releases
search_btn = driver.find_element(by=By.ID, value="search-toggle")
wait.until(lambda _: search_btn.is_displayed)
search_btn.click()

# Property select
iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
driver.switch_to.frame(iframe)
time.sleep(2)
prop_div = driver.find_element(By.ID, "zenql-ss-type")
elements = prop_div.find_elements(By.TAG_NAME, "a")
elements[0].click()
elem = driver.switch_to.active_element
elem.send_keys("Folder Path")
elem.send_keys(Keys.ENTER)

# Set folder path

# Set date

# Un-archive

# Other pages of results?
