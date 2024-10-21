from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchFrameException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import csv
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

INPUT_FILE = "~/Downloads/license-plate.csv"
OUTPUT_FILE = "vl-validity-output.csv"

# For randomness when opening the website
MIN_SLEEP_SECONDS = 1
MAX_SLEEP_SECONDS = 3

BASE_PAGE="https://onemotoring.lta.gov.sg/content/onemotoring/home.html"
PRIME_PAGE="https://vrl.lta.gov.sg/lta/vrl/action/enquirePrivateHireCars?FUNCTION_ID=F0401023ET"


def random_sleep():
  sleep(random.randint(MIN_SLEEP_SECONDS, MAX_SLEEP_SECONDS))

def chromeSendKeys(driver, custom_element, custom_keys):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(custom_element)
    actions.click()
    actions.send_keys(custom_keys)
    actions.send_keys(Keys.RETURN)
    actions.perform()

    return

def chromeClick(driver, custom_element):
    actions = webdriver.ActionChains(driver)
    actions.move_to_element(custom_element)
    actions.click()
    actions.perform()

    return


if __name__ == "__main__":

    driver_numbers=[
        "SNL1928M",
        "SKT2902Z",
        "SGQ7772L"
    ]


    logging.info(f"{len(driver_numbers)} vehicle numbers loaded")

    # Uses Chrome now
    driver = webdriver.Chrome()
    


    logging.info("Website initialized")
    driver.get(BASE_PAGE)
    sleep(5)

    driver.get(PRIME_PAGE)

    logging.info("Get cookie. Enter veh number and captcha")
    # Send in veh no
    # driver.switch_to.frame('main')
    veh_no_field = WebDriverWait(driver, 15).until(
                  EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div[3]/div[2]/form/div[1]/div[2]/input"))
                  )
    veh_no_field.send_keys("SLL8402R")

    # Tick the checkbox
    checkbox = WebDriverWait(driver, 15).until(
               EC.presence_of_element_located((By.NAME, "tcCheckbox"))
               )
    # checkbox.click()
    chromeClick(driver, checkbox)

    # Input captcha_code
    captcha_code = raw_input("Enter the CAPTCHA: ")
    captcha_input = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "captchaResponse"))
                    )
    captcha_input.send_keys(captcha_code)
    # chromeSendKeys(driver, captcha_input, captcha_code)
    
    # Click the submit button
    submit_button = WebDriverWait(driver, 15).until(
                   EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div[3]/div[2]/form/div[5]/div/input[1]"))
                   )

    driver.switch_to.default_content()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    # driver.switch_to.frame("main")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    for i in range(10):
        try:
            chromeClick(driver, submit_button)
        except StaleElementReferenceException:
            break
    logging.info("Submitting")

    sleep(3)

    driver_count = 0
    for driver_num in driver_numbers:
            query_success = False

            # If captcha code has not been reset, go back
            # Otherwise refresh the main page
            if captcha_code != "":
                driver.back()
            else:
                driver.get(base_page)

            driver_count  += 1
            logging.info(f"#{driver_count} Checking {driver_num}")
            sleep(1)

            actions = ActionChains(driver)
            actions.send_keys(Keys.RETURN).perform
          
            success, attempts = False, 0
            while success != True and attempts < 5:
                attempts += 1
                try:
                    actions = ActionChains(driver)
                    actions.send_keys(Keys.RETURN).perform()
                    success = True
                except UnexpectedAlertPresentException:
                    driver.switch_to_alert().accept()

            if captcha_code == "":
                captcha_code = raw_input("Enter new captcha code: ")


            # Send in veh no
            veh_no_field = WebDriverWait(driver, 10).until(
                   EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div[3]/div[2]/form/div[1]/div[2]/input"))
                   )
            veh_no_field.clear()
            veh_no_field.send_keys(driver_num)
            # chromeSendKeys(driver, veh_no_field, driver_num)
            logging.info("Vehicle number entered")

            # Tick the checkbox
            checkbox = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, "tcCheckbox"))
                    )
            if checkbox.is_selected() == True:
                pass
            else:
                chromeClick(driver, checkbox)
                # checkbox.click()
                logging.info("Check checkbox")

            # Ensure captcha is filled, otherwise, ask for new captcha
            captcha_input = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.NAME, "captchaResponse"))
                            )
            captcha_input.clear()
            captcha_input.send_keys(captcha_code)
            # chromeSendKeys(driver, captcha_input, captcha_code)
            

    
            # Click the submit button
            driver.switch_to.default_content()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # driver.switch_to.frame("main")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            submit_button = WebDriverWait(driver, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div[3]/div[2]/form/div[5]/div/input[1]"))
                            )
            for i in range(1):
                try:
                    chromeClick(driver, submit_button)
                    # submit_button.click()
                except StaleElementReferenceException:
                    break
            logging.info("Submitting")

            sleep(1)

            # Check if no records found
            try:
                query_status = WebDriverWait(driver,3).until(
                              EC.presence_of_element_located((By.CLASS_NAME, "errorTxtRedBold12pt"))
                              )
                if "No record found" in query_status.text:
                    logging.info("No record found. Captcha reset")
                    captcha_code = ""

                    # Write the LTA data into the .csv file
                    with open('drivers_pdvl.csv', 'ab') as csv_file:
                        writer = csv.writer(csv_file)
                        driver_info = [driver_count, driver_num,"No record","No record","No record"] 
                        writer.writerow(driver_info)
                        query_success = True

                if query_success == True:
                    with open("driver_numbers.txt", "r") as f:
                        f_lines = f.readlines()
                    with open("driver_numbers.txt","w") as f:
                        for line in f_lines:
                            if line != driver_num + "\n":
                                f.write(line)
                            else:
                                logging.info("1 line removed")

                    logging.info(f"{driver_num} has been successfully queried")
                    # Go to next query
                    continue

            except (TimeoutException, StaleElementReferenceException) as e:
                pass

            # Where a record was found in the system
            # Get pdvl info
            pdvl_status = WebDriverWait(driver,5).until(
                          EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div/div/div[2]/div[2]/form/div[2]/div/p"))
                          )

            # Get car_make
            car_make = WebDriverWait(driver,5).until(
                       EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div/div/div[2]/div[2]/form/div[3]/div/p"))
                       )

            # Get decal info
            decal_num = WebDriverWait(driver,5).until(
                        EC.presence_of_element_located((By.XPATH, "//*[@id=\"main-content\"]/div/div/div[2]/div[2]/form/div[4]/div/p"))
                        )

            driver_info = [driver_count, driver_num, pdvl_status.text, car_make.text, decal_num.text]
            logging.info(driver_info)

            # Write the LTA data into the .csv file
            with open('drivers_pdvl.csv', 'ab') as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow(driver_info)
                query_success = True

            # If query complete, remove the driver number from text file
            if query_success == True:
                with open("driver_numbers.txt", "r") as f:
                    f_lines = f.readlines()
                with open("driver_numbers.txt","w") as f:
                    for line in f_lines:
                        if line != driver_num + "\n":
                            f.write(line)
                        else:
                            logging.info("1 line removed")

                logging.info(f"{driver_num} has been successfully queried")

