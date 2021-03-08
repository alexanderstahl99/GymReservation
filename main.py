from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
import config
import time
import helpers


def main():
    chosen_gym = helpers.choose_gym()
    if chosen_gym == "IMSB":
        url = config.IMSB_URL
    elif chosen_gym == "NCRB":
        url = config.NCRB_URL
    driver = helpers.create_driver()
    driver.get(url)
    driver.implicitly_wait(10)
    helpers.login(driver)
    time.sleep(5.5)
    openings = helpers.parse_openings(driver)
    slot_time = helpers.choose_time(driver)
    helpers.schedule_slot(slot_time, openings, driver)
    time.sleep(5)
    print("Successfully booked slot at " + chosen_gym + " for " + slot_time + "!")
    driver.close()
    driver.quit()

    # Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()
