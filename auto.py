from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import datetime
import os
import time


def waitClick(wait, el):
    wait.until(lambda _: el.is_displayed())
    el.click()


def waitClickId(driver, wait, id):
    el = wait.until(EC.element_to_be_clickable((By.ID, id)))
    el.click()


def delete_files(wait, driver, root_title, files):
    root_handle = driver.current_window_handle
    els = ["EF332", "EF333", "EF334", "EF411"]
    for id in els:
        waitClickId(driver, wait, id)
    for fname in files:
        links = driver.find_elements(By.CSS_SELECTOR, ".rtIn")
        target_files = [x for x in links if fname == x.text]
        if len(target_files) > 0:
            my_target = target_files[0]
            driver.execute_script("arguments[0].scrollIntoView(true);", my_target)
            waitClick(wait, my_target)
            mydel = driver.find_elements(By.CSS_SELECTOR, "#contextmenu_delete_link")
            if len(mydel) > 0:
                waitClick(wait, mydel[0])
                wait.until(EC.number_of_windows_to_be(2))
                for window_handle in driver.window_handles:
                    if window_handle != root_handle:
                        driver.switch_to.window(window_handle)
                        break
                wait.until(EC.title_is("Delete Content to Recycle Bin"))
                buttons = driver.find_elements(By.CSS_SELECTOR, ".sys_button-danger")
                if len(buttons) > 0:
                    waitClick(wait, buttons[0])
                    driver.switch_to.window(root_handle)
                    wait.until(EC.title_is(root_title))


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


def unarchive(wait, driver, n, cut_off):
    target_files = []
    root_title = driver.title
    root_handle = driver.current_window_handle
    # Get into the archive
    waitClickId(driver, wait, "management-toggle")
    waitClickId(driver, wait, "ArchivedContent")

    # Loop n times and unarchive releases created before cutoff
    i = 0
    while i < n:
        i += 1
        iframe = driver.find_element(By.ID, "ContensisUI_Viewer")
        wait.until(lambda _: iframe.is_displayed())
        driver.switch_to.frame(iframe)
        # Set folder path
        path_input = driver.find_element(
            By.ID, "ctl19_ctl00_ctl02_ctl02_FilterTextBox_ItemPath"
        )
        wait.until(lambda _: path_input.is_displayed())
        path_input.send_keys(Keys.TAB)
        path_input.send_keys(
            "/council_and_democracy/council_information/media_hub/media_releases"
        )
        path_input.send_keys(Keys.ENTER)
        # Sort by date
        main_table = driver.find_element(By.ID, "ctl19_ctl00_Header")
        wait.until(lambda _: main_table.is_displayed())
        head = main_table.find_elements(By.TAG_NAME, "thead")
        wait.until(lambda _: head[0].is_displayed())
        a_tags = head[0].find_elements(By.TAG_NAME, "a")
        date_fields = [x for x in a_tags if x.text.strip().lower() == "date created"]
        wait.until(lambda _: date_fields[0].is_displayed())
        print(date_fields[0].text)
        date_fields[0].click()
        time.sleep(2)
        
        # Find oldest page & date
        rows = driver.find_elements(By.CSS_SELECTOR, ".GridRow_StandardGrid")
        tds = rows[0].find_elements(By.TAG_NAME, "td")
        unarchive = rows[0].find_elements(By.CSS_SELECTOR, ".sys_function_unarchive")
        inner_text = driver.execute_script("return arguments[0].innerHTML;", tds[4])
        print(inner_text)
        my_split = inner_text.split(" ")
        (d, m, y) = my_split[0].split("/")
        item_date = datetime.datetime(int(y), int(m), int(d))
        # Un-archive
        if item_date < cut_off:
            if "media_release" in tds[3].text:
                waitClick(wait, unarchive[0])
                # Find the pop-up window & switch to it
                wait.until(EC.number_of_windows_to_be(2))
                for window_handle in driver.window_handles:
                    if window_handle != root_handle:
                        driver.switch_to.window(window_handle)
                        break
                wait.until(EC.title_is("Confirmation"))
                waitClickId(driver, wait, "ctl43")
                # Switch back to main window
                driver.switch_to.window(root_handle)
                wait.until(EC.title_is(root_title))
                target_files.append(tds[1].text)
        else:
            
    return target_files


def main():
    load_dotenv()
    driver = init_driver()
    wait = WebDriverWait(driver, timeout=20)
    my_login(wait, driver, os.getenv("USERNAME"), os.getenv("PASSWORD"))
    cut_off = datetime.datetime(2022, 1, 1)
    files = unarchive(wait, driver, 2, cut_off)
    # delete_files(wait, driver, driver.title, files)
    driver.quit()


if __name__ == "__main__":
    main()
