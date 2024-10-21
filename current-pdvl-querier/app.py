import csv
import logging
import typing
import sys
import random
import requests
from time import sleep


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

INPUT_FILE = "vl-validity.csv"
### Sample input CSV
# ID,Full name (as per NRIC),Full NRIC (E.g. SxxxxxxxG),Date of Birth in ddmmyyyy format (e.g 23071959)
# 1,TAN TOCK SENG,S1234567B,31011991
# 2,LIM AH KOW,S1234567D,31021992
# 3,MUHAMMAD BIN MUHMMAD,S1234567G,31031993

OUTPUT_FILE = "vl-validity-output.csv"
### Sample output CSV
# 1,TAN TOCK SENG,S1234567B,31011991,Private Hire Car Driver's Vocational Licence (PDVL),Valid,26-02-2027
# 2,LIM AH KOW,S1234567D,31021992hPrivate Hire Car Driver's Vocational Licence (PDVL),Valid,25-03-2027
# 3,MUHAMMAD BIN MUHMMAD,S1234567G,31031993,Private Hire Car Driver's Vocational Licence (PDVL),Valid,22-04-2027

# LTA URLs
LTA_URL = "https://onemotoring.lta.gov.sg/content/onemotoring/home/driving/vocational_licence/vocational_licence_renewal.html"  # URL to the UI
API_URL = "https://onemotoring.lta.gov.sg/onem/ptls/vldatainfo"   # URL of the API underlying the UI


# For randomness when opening the website
MIN_SLEEP_SECONDS = 1
MAX_SLEEP_SECONDS = 3


def random_sleep():
  sleep(random.randint(MIN_SLEEP_SECONDS, MAX_SLEEP_SECONDS))

def read_and_process_driver_csv(drop_first_line: bool) -> list[dict]:
  rows = []
  rows_read = 0
  with open(INPUT_FILE, mode ='r')as file:
    csvFile = csv.reader(file)

    for lines in csvFile:
      if rows_read == 0 and drop_first_line:
        logging.info("SKIP FIRST LINE")
      else:
        rows.append({"id": lines[0],
          "name": lines[1],
          "nric": lines[2],
          "dob": lines[3]
        })
        # Sample row: {'id': '1', 'name': 'KOH TA MING', 'nric': 'S9222554B', 'dob': '26061992'}
      
      rows_read += 1

  logging.info(f"Drivers read: {rows_read}")

  return rows


def processDateString(date_string) -> str:
  if len(date_string) == 8:
    return date_string[0:2] + "-" + date_string[2:4] + "-" + date_string[4:8]
  elif len(date_string) == 7:
    return "0" + date_string[0:1] + "-" + date_string[1:3] + "-" + date_string[3:7]
  else:
    raise ValueError("date string must be either 7 or 8 characters long")
  
  return "Invalid date string"


def create_lta_session():
  ses = requests.Session()

  res = ses.get(LTA_URL)
  res.raise_for_status()

  return ses


def query_pdvl_endpoint(ses, nric: str, raw_dob_string: str):
  processed_date_string = processDateString(raw_dob_string)
  logging.info(processed_date_string)

  headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
             'Accept': '*/*',
             'Accept-Encoding': 'gzip, deflate, br, zstd',
             'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
             'Origin': 'https://onemotoring.lta.gov.sg',
             'Referer': 'https://onemotoring.lta.gov.sg/content/onemotoring/home/driving/vocational_licence/vocational_licence_renewal.html',
             'X-Requested-With': 'XMLHttpRequest',
             'Content-Type': 'application/x-www-form-urlencoded'
  }
  res = ses.post(f"{API_URL}?dateOfBirth={processed_date_string}&identificationNumber={nric}&identificationType=1", headers=headers) 

  res.raise_for_status()

  data = res.json()

  return data

def parse_response(driver_data: str):
  if driver_data["status"]["statusMessage"] == "Success":
    logging.info(driver_data["vlInfos"])
  else:
    raise ValueError("LTA API did not return success")

  return driver_data["vlInfos"]
  

def write_data(successful_query: bool, driver, licenses):
    with open(OUTPUT_FILE, 'a') as csv_file:
      writer = csv.writer(csv_file)
      if successful_query:
        if len(licenses) > 0:
          for lic in licenses:
            logging.info(lic)
            driver_info = [driver['id'], driver['nric'], driver['name'], driver['dob'], lic['type'], lic['status'], lic['expiryDate']]
            writer.writerow(driver_info)
        else:
          driver_info = [driver['id'],driver['nric'], driver['name'], driver['dob'], "NO LICENSE", "NO LICENSE", "NO LICENSE"]
          writer.writerow(driver_info)
      else:
        driver_info = [driver['id'], driver['nric'],driver['name'], driver['dob'], "ERROR", "ERROR", "ERROR"]
        writer.writerow(driver_info)
      
  




if __name__ == "__main__":
  logging.info("***** START")


  logging.info(f"Input: {INPUT_FILE}")
  logging.info(f"Output: {OUTPUT_FILE}")

  drivers = read_and_process_driver_csv(drop_first_line=True)
  #logging.info(drivers)


  logging.info("Sample: ")
  logging.info(drivers[0]) # {'id': '1', 'name': 'KOH TA MING', 'nric': 'S9222554B', 'dob': '26061992'}

  #webdriver = open_lta_website()
  #cookies_d = get_cookie_dict(webdriver)

  ses = create_lta_session()

  for d in drivers:
    try:
      licenses = []
      logging.info("Query driver: " + d['name'])
      driver_data = query_pdvl_endpoint(ses=ses, nric=d['nric'], raw_dob_string=d['dob'])
      logging.info(driver_data)  # {'status': {'statusCode': 1, 'statusMessage': 'Success'}, 'vlInfos': [{'type': "Private Hire Car Driver's Vocational Licence (PDVL)", 'status': 'Valid', 'expiryDate': '25-02-2027'}]}
      licenses = parse_response(driver_data) # {'type': "Private Hire Car Driver's Vocational Licence (PDVL)", 'status': 'Valid', 'expiryDate': '25-02-2027'}
      write_data(successful_query=True, driver=d, licenses=licenses)
    except Exception as e:
      write_data(successful_query=False, driver=d, licenses=licenses)
    finally:
      logging.info("Query and write complete for " + d['name'])
      random_sleep()


  logging.info("------ END")
