from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import os
import time


def waitClick(wait, el):
    wait.until(lambda _: el.is_displayed())
    el.click()


def waitClickId(wait, id):
    el = wait.until(EC.element_to_be_clickable((By.ID, id)))
    el.click()


def init_driver():
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(2)
    return driver


def my_login(wait, driver, user, pwd):
    driver.get("https://cms-chesheast.cloud.contensis.com/Default.aspx")
    user_input = driver.find_element(by=By.NAME, value="_Textbox_Username")
    pwd_input = driver.find_element(by=By.NAME, value="_Textbox_Password")
    login_btn = driver.find_element(by=By.NAME, value="ctl39")
    wait.until(lambda _: user_input.is_displayed())
    user_input.send_keys(user)
    pwd_input.send_keys(pwd)
    login_btn.click()


def safe_links(wait, driver):
    root_title = driver.title
    root_handle = driver.current_window_handle
    waitClickId(wait, "management-toggle")
    waitClickId(wait, "ProjectSetup")
    waitClickId(wait, "Hyperlinks")

    iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
    wait.until(lambda _: iframe.is_displayed())
    driver.switch_to.frame(iframe)
    time.sleep(1)

    # Get all the safelinks
    path_input = driver.find_element(By.ID, "ctl19_ctl00_ctl02_ctl02_FilterTextBox_Url")
    wait.until(lambda _: path_input.is_displayed())
    path_input.send_keys(Keys.TAB)
    path_input.send_keys("safelinks")
    path_input.send_keys(Keys.ENTER)
    i = 0
    for a in range(28):
        time.sleep(2)
        rows = driver.find_elements(By.CSS_SELECTOR, ".GridRow_StandardGrid")
        tds = rows[i].find_elements(By.TAG_NAME, "td")
        waitClick(wait, tds[2])
        img = tds[4].find_element(By.TAG_NAME, "img")
        alt = driver.execute_script("return arguments[0].alt;", img)
        if tds[5].text == "Unused" or alt == "Edit":
            # input = tds[0].find_element(By.TAG_NAME, "input")
            # driver.execute_script("arguments[0].checked = true;", input)
            # waitClick(wait, tds[0])
            time.sleep(1)
            btn = driver.find_element(By.CSS_SELECTOR, ".sys_deletehyperlink")
            waitClick(wait, btn)
            wait.until(EC.number_of_windows_to_be(2))
            for window_handle in driver.window_handles:
                if window_handle != root_handle:
                    driver.switch_to.window(window_handle)
                    break
            time.sleep(1)
            wait.until(EC.title_is("Delete Content to Recycle Bin"))
            del_btn = driver.find_element(By.CSS_SELECTOR, ".sys_button-danger")
            waitClick(wait, del_btn)
            # Switch back to main window
            driver.switch_to.window(root_handle)
            wait.until(EC.title_is(root_title))
            time.sleep(1)
            iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
            wait.until(lambda _: iframe.is_displayed())
            driver.switch_to.frame(iframe)
        elif i == 0:
            i = 1
        else:
            break


def main():
    load_dotenv()
    driver = init_driver()
    wait = WebDriverWait(driver, timeout=20)
    my_login(wait, driver, os.getenv("USERNAME"), os.getenv("PASSWORD"))
    safe_links(wait, driver)
    # driver.quit()


if __name__ == "__main__":
    main()
