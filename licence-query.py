from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchFrameException, StaleElementReferenceException, UnexpectedAlertPresentException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from sys import argv
import csv
# from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

def inputDriverDetails(driver, name , nric, day, month, year):
    # Send NRIC
    nric_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "nric"))
                )
    nric_field.clear()
    nric_field.send_keys(nric)

    # Send DOB : DD - MM - YYYY
    day_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "day"))
                )
    day_field.clear()
    day_field.send_keys(day)

    month_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "month"))
                )
    month_field.clear()
    month_field.send_keys(month)


    year_field = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "year"))
                )
    year_field.clear()
    year_field.send_keys(year)

    
    # Click the proceed button
    proceed_btn = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "innerpage-btnsubmit"))
                )
    proceed_btn.click()

    print nric, name, "is being queried"

    return

def readDriverLicences(driver,query_no,  nric, dax_dob, name,
                        private_car, private_car_validity, private_car_expiry,
                        taxi, taxi_validity, taxi_expiry,
                        omnibus, omnibus_validity, omnibus_expiry,
                        general_bus, general_bus_validity, general_bus_expiry,
                        bus_attendant, bus_attendant_validity, bus_attendant_expiry,
                        trishaw, trishaw_validity, trishaw_expiry):

    for licence_no in range(6):
        try:

            licence_type = WebDriverWait(driver, 2).until(
                           EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div["+str(licence_no+2)+"]/div[1]/p"))
                        ).text
            validity = WebDriverWait(driver, 0.1).until(
                       EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div["+str(licence_no+2)+"]/div[2]/p"))
                       ).text
            expiry_date = WebDriverWait(driver, 0.1).until(
                          EC.presence_of_element_located((By.XPATH, "//*[@id=\"response\"]/div[3]/div[2]/div/div["+str(licence_no+2)+"]/div[3]/p"))
                          ).text
            if "Private Hire Car" in licence_type:
                private_car = "Yes"
                private_car_validity = validity
                private_car_expiry = expiry_date
            elif "Taxi Driver" in licence_type:
                taxi = "Yes"
                taxi_validity = validity
                taxi_expiry = expiry_date
            elif "Omnibus" in licence_type:
                omnibus = "Yes"
                omnibus_validity = validity
                omnibus_expiry = expiry_date
            elif "General Bus Driver" in licence_type:
                general_bus = "Yes"
                general_bus_validity = validity
                general_bus_expiry = expiry_date
            elif "Bus Attendant" in licence_type:
                bus_attendant = "Yes"
                bus_attendant_validity = validity
                bus_attendant_expiry = expiry_date
            elif "Trishaw Rider" in licence_type:
                trishaw = "Yes"
                trishaw_validity = validity
                trishaw_expiry = expiry_date

        # Timeout means no more licences were found
        except TimeoutException:
            print "Query complete. %d licences found" % licence_no
            query_success = True
            break

    driver_info = [query_no, nric, dax_dob, name,
                   private_car, private_car_validity, private_car_expiry,\
                   taxi, taxi_validity, taxi_expiry,\
                   omnibus, omnibus_validity, omnibus_expiry,\
                   general_bus, general_bus_validity, general_bus_expiry,\
                   bus_attendant, bus_attendant_validity, bus_attendant_expiry,\
                   trishaw, trishaw_validity, trishaw_expiry]
    return driver_info

def getResponse(driver):
    record_found, query_success = False, False
    try:

        # Check if the page is still loading
        response = "Loading"
        while response == "Loading":
            response = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, 
                        "response"))
                       ).text
            sleep(0.5)

        # Check if no record is returned        
        response = WebDriverWait(driver, 2).until(
                    EC.presence_of_element_located((By.XPATH,
                    "//*[@id=\"response\"]/div[2]/div/div/div/span"))
                   ).text
        if "No record found" in response:
            print "No record found"
            record_found = False
            query_success = True

    # This is when a record is found, when no reponse was not found
    except TimeoutException:
        print "Record found!"
        record_found = True

    return record_found, query_success

# Main function begins here
if __name__ == "__main__":

    daxs = {}
    with open("drivers_nric_dob.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            # print row

            # make id_no an int
            id_no = int(row["id_no"])

            # check for 2-digit birth day
            if len(row["day"]) < 2:
                two_digit_day = "0" + row["day"]
            else:
                two_digit_day = row["day"]    

            # check for 2-digit birth month
            if len(row["month"]) < 2:
                two_digit_month = "0" + row["month"]
            else:
                two_digit_month = row["month"]    

            daxs[id_no] = [row["nric"],row["name"], two_digit_day, two_digit_month, row["year"]]
        print str(len(daxs)), "drivers loaded"
        # print daxs


    if len(argv) < 1:
        print "Need at least one argument"
        print "Either <all>"
        print "Or <start_no> <end_no>"
        print "Or <start_no> <all>"
    elif argv[1] == "all":
        queries = range(1, len(daxs)+1)
        print "Getting %d queries" % (len(daxs))
    elif argv[2] == "end":
        queries = range(int(argv[1]), len(daxs))
        print "Getting %d to %d" % (int(argv[1]), len(daxs))
    else:
        queries  = range(int(argv[1]), int(argv[2])+1)
        print "Getting %d to %d" % (int(argv[1]), int(argv[2]))


    driver = webdriver.Chrome()
    base_page = "https://www.onemotoring.com.sg/content/onemotoring/en/lta_e_services/online_enquiries/vocational_licences.html"

    print "Website initialized"
    driver.get(base_page)


    for query_no in queries:

        print "****** # %d" % (query_no)
        query_success = True

        # Data to output
        nric = daxs[query_no][0]
        name = daxs[query_no][1]
        private_car, private_car_validity, private_car_expiry = "No", "" ,""
        taxi, taxi_validity, taxi_expiry = "No", "", ""
        omnibus, omnibus_validity ,omnibus_expiry = "No", "", ""
        general_bus, general_bus_validity ,general_bus_expiry = "No", "", ""
        bus_attendant, bus_attendant_validity, bus_attendant_expiry = "No", "", ""
        trishaw, trishaw_validity ,trishaw_expiry = "No", "", ""

        # Skip if NRIC is blank, means it's an invalid NRIC
        if nric == "":
            print "Blank NRIC. Next"
            continue


        print "Querying", nric
        dax_dob = str(daxs[query_no][2]) +"-"+ str(daxs[query_no][3]) +"-"+ str(daxs[query_no][4])

        try:
            inputDriverDetails(driver, name=name, nric=nric, day=daxs[query_no][2], month=daxs[query_no][3], year=daxs[query_no][4])
            record_found, query_success = getResponse(driver)


        # UnexpectedAlert box, most likely an invalid driver data was entered
        except UnexpectedAlertPresentException:
            print "!Alert: invalid driver info added"
            record_found, query_success = False, False

            try:
                alert = driver.switch_to_alert()
                alert.dismiss()
                print "Alert closed"
            except:
                pass

        # Will only proceed to extract driver info if a record was found, other proceed to writing the csv
        if record_found == True: 
            driver_info = readDriverLicences(driver, query_no, nric, name, dax_dob,
                            private_car, private_car_validity, private_car_expiry,
                            taxi, taxi_validity, taxi_expiry,
                            omnibus, omnibus_validity, omnibus_expiry,
                            general_bus, general_bus_validity, general_bus_expiry,
                            bus_attendant, bus_attendant_validity, bus_attendant_expiry,
                            trishaw, trishaw_validity, trishaw_expiry)
        else:
            driver_info =   query_no ,nric, name, dax_dob,\
                            private_car, private_car_validity, private_car_expiry,\
                            taxi, taxi_validity, taxi_expiry,\
                            omnibus, omnibus_validity, omnibus_expiry,\
                            general_bus, general_bus_validity, general_bus_expiry,\
                            bus_attendant, bus_attendant_validity, bus_attendant_expiry,\
                            trishaw, trishaw_validity, trishaw_expiry

        with open("driver_licence_info.csv","ab") as csvfile:
            print "Writing to csv"
            writer = csv.writer(csvfile)
            writer.writerow(driver_info)

    print "Program end"



    
