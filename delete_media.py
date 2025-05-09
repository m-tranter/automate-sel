from dotenv import load_dotenv
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver

from selenium.webdriver.common.keys import Keys


def waitClick(wait, el):
    wait.until(lambda _: el.is_displayed())
    el.click()


def waitClickId(wait, id):
    el = wait.until(EC.element_to_be_clickable((By.ID, id)))
    el.click()


def init_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-remote-allow-system-access")
    options.add_argument("-headless")
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


def main():
    # open the file and get the page titles into an array
    with open("media.csv", "r") as file:
        lines = [line.strip() for line in file.readlines()]

    load_dotenv()
    driver = init_driver()
    root_title = driver.title
    root_handle = driver.current_window_handle
    wait = WebDriverWait(driver, timeout=20)
    my_login(wait, driver, os.getenv("USERNAME"), os.getenv("PASSWORD"))
    time.sleep(1)
    els = ["EF332", "EF333", "EF334", "EF411"]
    for id in els:
        waitClickId(wait, id)
    time.sleep(1)

    driver.set_context("chrome")
    win = driver.find_element(By.TAG_NAME, "html")
    for x in range(0, 10):
        win.send_keys(Keys.CONTROL + "-")
    driver.set_context("content")
    print("Deleting")
    for line in lines:
        time.sleep(1)
        links = driver.find_elements(By.CSS_SELECTOR, ".rtIn")
        targets = [x for x in links if line == x.text]
        for my_target in targets:
            time.sleep(2)
            wait.until(lambda _: my_target.is_displayed())
            nav = driver.find_element(By.ID, "ContensisUI_NavigatorPanel")
            nav2 = driver.find_element(By.ID, "ContensisUI_navigatorPanelContainer")
            nav3 = driver.find_element(By.ID, "ContensisUI_navigatorpanel-pull")
            driver.execute_script("arguments[0].style.width = '1000px';", nav)
            driver.execute_script("arguments[0].style.width = '5px';", nav2)
            driver.execute_script("arguments[0].style.width = '5px';", nav3)
            driver.execute_script("arguments[0].style.zIndex = '100';", my_target)
            driver.execute_script("arguments[0].style.zIndex = '-1';", nav2)
            driver.execute_script("arguments[0].style.zIndex = '-1';", nav3)
            driver.execute_script("arguments[0].scrollIntoView(true);", my_target)
            name = my_target.text
            waitClick(wait, my_target)
            time.sleep(1)
            mydel = driver.find_element(By.CSS_SELECTOR, "#contextmenu_delete_link")
            waitClick(wait, mydel)
            time.sleep(1)
            wait.until(EC.number_of_windows_to_be(2))
            for window_handle in driver.window_handles:
                if window_handle != root_handle:
                    driver.switch_to.window(window_handle)
                    break
            time.sleep(1)
            wait.until(EC.title_is("Delete Content to Recycle Bin"))
            buttons = driver.find_elements(By.CSS_SELECTOR, ".sys_button-danger")
            waitClick(wait, buttons[0])
            print(name)
            driver.switch_to.window(root_handle)
            time.sleep(1)
    driver.quit()


if __name__ == "__main__":
    main()
