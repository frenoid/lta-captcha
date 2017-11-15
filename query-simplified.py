from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import csv

if __name__ == "__main__":
    driver = webdriver.Chrome()
    base_page = "https://www.onemotoring.com.sg/content/onemotoring/en/lta_e_services/online_enquiries/vocational_licences.html"
    driver.get(base_page)

    # Enter NRIC
    nric_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "nric"))
                )
    nric_field.send_keys("S0135604F")

    # Enter DOB
    day_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "day"))
                )
    day_field.send_keys("27")

    month_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "month"))
                )
    month_field.send_keys("05")


    year_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "year"))
                )
    year_field.send_keys("1954")

    # Click the proceed button
    proceed_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "innerpage-btnsubmit"))
                )
    proceed_btn.click()

    
    # Wait for the website to complete loading
    # Normally you would write use a try-except clause
    sleep(5)

    # Read the data
    licence_type = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div[2]/div[1]/p"))
                    ).text
    validity = WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div[2]/div[2]/p"))
                ).text
    expiry_date = WebDriverWait(driver, 0.1).until(
                EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div[2]/div[3]/p"))
                ).text


    nric = "S0135604F"
    bod = "27-05-1954"
    driver_info = nric, bod, licence_type, validity, expiry_date

    # Write it into a csv file
    with open("example.csv", "ab") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(driver_info)
        
    
    
