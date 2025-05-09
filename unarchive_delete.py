from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import os
import time

unarchived = []
deleted = []


def waitClick(wait, el):
    wait.until(lambda _: el.is_displayed())
    el.click()


def waitClickId(wait, id):
    el = wait.until(EC.element_to_be_clickable((By.ID, id)))
    el.click()


def delete_files(wait, driver, root_title, files):
    print("Deleting")
    root_handle = driver.current_window_handle
    els = ["EF332", "EF333", "EF334", "EF411"]
    for id in els:
        waitClickId(wait, id)
    time.sleep(1)
    files = list(dict.fromkeys(files))
    files.sort()
    for fname in files:
        time.sleep(1)
        links = driver.find_elements(By.CSS_SELECTOR, ".rtIn")
        target_files = [x for x in links if fname.replace("'", "") == x.text]
        for my_target in target_files:
            time.sleep(1)
            wait.until(lambda _: my_target.is_displayed())
            name = my_target.text
            nav = driver.find_element(By.ID, "ContensisUI_NavigatorPanel")
            nav2 = driver.find_element(By.ID, "ContensisUI_navigatorPanelContainer")
            nav3 = driver.find_element(By.ID, "ContensisUI_navigatorpanel-pull")
            driver.execute_script("arguments[0].style.width = '1000px';", nav)
            driver.execute_script("arguments[0].style.width = '5px';", nav2)
            driver.execute_script("arguments[0].style.width = '5px';", nav3)
            driver.execute_script("arguments[0].style.zIndex = '-1';", nav2)
            driver.execute_script("arguments[0].style.zIndex = '-1';", nav3)
            driver.execute_script("arguments[0].style.zIndex = '100';", my_target)
            driver.execute_script("arguments[0].scrollIntoView(true);", my_target)
            waitClick(wait, my_target)
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
            time.sleep(1)
            driver.switch_to.window(root_handle)
            wait.until(EC.title_is(root_title))


def init_driver():
    options = webdriver.FirefoxOptions()
    options.add_argument("-remote-allow-system-access")
    options.add_argument("-headless")
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(20)
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


def setPath(wait, driver):
    path_input = driver.find_element(
        By.ID, "ctl19_ctl00_ctl02_ctl02_FilterTextBox_ItemPath"
    )
    wait.until(lambda _: path_input.is_displayed())
    path_input.send_keys(Keys.TAB)
    path_input.send_keys(
        "/council_and_democracy/council_information/media_hub/media_releases"
    )
    path_input.send_keys(Keys.ENTER)


def sortDate(wait, driver):
    main_table = driver.find_element(By.ID, "ctl19_ctl00_Header")
    wait.until(lambda _: main_table.is_displayed())
    head = main_table.find_elements(By.TAG_NAME, "thead")
    wait.until(lambda _: head[0].is_displayed())
    a_tags = head[0].find_elements(By.TAG_NAME, "a")
    date_fields = [x for x in a_tags if x.text.strip().lower() == "date created"]
    wait.until(lambda _: date_fields[0].is_displayed())
    date_fields[0].click()
    time.sleep(2)


def unarchive(wait, driver, n, cut_off):
    target_files = []
    root_title = driver.title
    root_handle = driver.current_window_handle
    # Get into the archive
    waitClickId(wait, "management-toggle")
    waitClickId(wait, "ArchivedContent")
    iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
    wait.until(lambda _: iframe.is_displayed())
    driver.switch_to.frame(iframe)
    print("Unarchiving")
    # Loop n times and unarchive releases created before cutoff
    for i in range(n):
        time.sleep(2)
        # Set folder path
        date = None
        while True:
            setPath(wait, driver)
            time.sleep(2)
            # Sort by date
            sortDate(wait, driver)
            # Find oldest page & date
            rows = driver.find_elements(By.CSS_SELECTOR, ".GridRow_StandardGrid")
            tds = rows[0].find_elements(By.TAG_NAME, "td")
            if len(tds) > 3:
                date = tds[4]
                break
        unarchive = rows[0].find_elements(By.CSS_SELECTOR, ".sys_function_unarchive")
        inner_text = driver.execute_script("return arguments[0].innerHTML;", date)
        my_split = inner_text.split(" ")
        (d, m, y) = my_split[0].split("/")
        item_date = datetime.datetime(int(y), int(m), int(d))
        # Un-archive
        if item_date < cut_off:
            if "media_release" in tds[3].text:
                fname = tds[1].text
                waitClick(wait, unarchive[0])
                time.sleep(1)
                # Find the pop-up window & switch to it
                wait.until(EC.number_of_windows_to_be(2))
                for window_handle in driver.window_handles:
                    if window_handle != root_handle:
                        driver.switch_to.window(window_handle)
                        break
                wait.until(EC.title_is("Confirmation"))
                waitClickId(wait, "ctl34")
                print(fname)
                # Switch back to main window
                driver.switch_to.window(root_handle)
                wait.until(EC.title_is(root_title))
                target_files.append(fname)
                iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
                wait.until(lambda _: iframe.is_displayed())
                driver.switch_to.frame(iframe)

    return target_files


def main():
    load_dotenv()
    driver = init_driver()
    wait = WebDriverWait(driver, timeout=10)
    my_login(wait, driver, os.getenv("USERNAME"), os.getenv("PASSWORD"))
    driver.set_context("chrome")
    win = driver.find_element(By.TAG_NAME, "html")
    for x in range(0, 10):
        win.send_keys(Keys.CONTROL + "-")
    driver.set_context("content")
    cut_off = datetime.datetime(2022, 1, 1)
    files = unarchive(wait, driver, 100, cut_off)
    driver.switch_to.default_content()
    waitClickId(wait, "navigator-toggle")
    delete_files(wait, driver, driver.title, files)
    driver.quit()


if __name__ == "__main__":
    main()
