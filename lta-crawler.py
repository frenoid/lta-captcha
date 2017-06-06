from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import pickle


if __name__ == "__main__":

    # Read in driver veh numbers
    with open('driver_numbers.txt', 'r') as f:
        driver_list = f.read().splitlines()

    driver_numbers = {driver_num:"Unknown" for driver_num in driver_list}

    print "%d vehicle numbers loaded" % (len(driver_numbers))

    driver =  webdriver.Firefox()
    base_page = "https://vrl.lta.gov.sg/lta/vrl/action/pubfunc2?ID=EnquirePrivateHireScheme"
    prime_page = "https://vrl.lta.gov.sg/lta/vrl/action/enquirePrivateHireCars?FUNCTION_ID=F0401023ET"

    print "Website initialized"
    driver.get(base_page)

    # Get cookie and store
    print "Get cookie. Enter veh number and captcha"

    sleep(15)
    pickle.dump(driver.get_cookies(), open("cookies.pkl","wb"))
    print "Cookies saved"

    # CLick ok
    driver.switch_to.frame('main')
    ok_button = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, "/html/body/div/div[5]/div/div/div/div[2]/div[2]/form/div[6]/div/input"))
                )
    ok_button.click()
    
    for driver_num in driver_numbers:
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))
            print "Cookies loaded"
                
            for cookie in cookies:
                print str(cookie)
                driver.add_cookie(cookie)

            driver.get(base_page)
            sleep(5)
            actions = ActionChains(driver)
            actions.send_keys(Keys.RETURN)
            actions.perform()
            
            try:
                driver.switch_to.frame('main')
                actions = ActionChains(driver)
                actions.send_keys(Keys.RETURN)
                actions.perform()
            
            except TimeoutException:
                pass

            # Send in veh no
            veh_no_field = WebDriverWait(driver, 15).until(
                   EC.presence_of_element_located((By.XPATH, "/html/body/div/div[5]/div/div[3]/div[2]/form/div[1]/div[2]/input"))
                   )
            veh_no_field.send_keys(driver_num)

            # Tick the checkbox
            checkbox = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.NAME, "tcCheckbox"))
                    )
            checkbox.click()


            """ Get CAPTCHA cookie """
            decal_no = "-"

            if decal_no == "-":
                driver_numbers[driver_num] = "No"
            else:
                driver_numbers[driver_num] = decal_no

        finally:
            driver.get(base_page)


