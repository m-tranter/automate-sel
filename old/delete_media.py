from dotenv import load_dotenv
import os
import time
import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

cut_off = datetime.datetime(2022, 1, 1)


# open the file and get the page titles into an array
with open("media.csv", "r") as file:
    lines = [line.strip() for line in file.readlines()]


# Get login info
load_dotenv()
user = os.getenv("USERNAME")
pwd = os.getenv("PASSWORD")

# Set up Firefox driver
options = webdriver.FirefoxOptions()
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(2)
wait = WebDriverWait(driver, timeout=2)

# Open contensis
driver.get("https://cms-chesheast.cloud.contensis.com/Default.aspx")
root_handle = driver.current_window_handle

# Log in
user_input = driver.find_element(by=By.NAME, value="_Textbox_Username")
pwd_input = driver.find_element(by=By.NAME, value="_Textbox_Password")
login_btn = driver.find_element(by=By.NAME, value="ctl39")
user_input.send_keys(user)
pwd_input.send_keys(pwd)
login_btn.click()
time.sleep(1)
root_title = driver.title
print(f"Window title: {root_title}")

# Switch to iframe
# iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
# driver.switch_to.frame(iframe)

# Navigate to folder

el = driver.find_element(By.ID, "EF332")
el.click()
time.sleep(1)
el = driver.find_element(By.ID, "EF333")
el.click()
time.sleep(1)
el = driver.find_element(By.ID, "EF334")
el.click()
time.sleep(1)
el = driver.find_element(By.ID, "EF411")
el.click()
time.sleep(1)


for line in lines:
    links = driver.find_elements(By.CSS_SELECTOR, ".rtIn")
    tar = [x for x in links if line in x.text]
    if len(tar) > 0:
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView(true);", tar[0])
        tar[0].click()
        mydel = driver.find_elements(By.CSS_SELECTOR, "#contextmenu_delete_link")
        if len(mydel) > 0:
            mydel[0].click()
            wait.until(EC.number_of_windows_to_be(2))
            for window_handle in driver.window_handles:
                if window_handle != root_handle:
                    driver.switch_to.window(window_handle)
                    break
            wait.until(EC.title_is("Delete Content to Recycle Bin"))
            buttons = driver.find_elements(By.CSS_SELECTOR, ".sys_button-danger")
            if len(buttons) > 0:
                buttons[0].click()
                time.sleep(1)
                driver.switch_to.window(root_handle)
                wait.until(EC.title_is(root_title))
