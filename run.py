import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
import gspread

# Initialize the Google Sheets connection
gc = gspread.service_account(filename='cred.json')
sh = gc.open('Flight Departure Scraper').sheet1

# Input the path to your ChromeDriver executable
chrome_driver_path = r"C:\Users\calgo\Downloads\CHROME DRIVER 116\chromedriver-win64\chromedriver.exe"

# Input the path to your ChromeDriver executable
chrome_driver_path = r"C:\Users\calgo\Downloads\CHROME DRIVER 116\chromedriver-win64\chromedriver.exe"

# This is the link for Luminsons Career Page
website = 'https://apps.atl.com/passenger/flightinfo/search.aspx'

# Use the provided ChromeDriver executable path
driver = webdriver.Chrome(executable_path=chrome_driver_path)

driver.get(website)

# Click on the element you want to interact with (replace with correct XPath)
Click1 = driver.find_element(By.XPATH, '/html/body/form/section/div[4]/div/div/div[1]/span[2]/span/span/a')
Click1.click()

# Create lists to store the scraped data
date_scraped = []
airline_flight_list = []
destination_city_list = []
scheduled_list = []
actual_list = []
remarks_list = []
gate_list = []

Date = driver.find_element(By.XPATH,
                           '//*[@id="bodySection_TabContainer_Flights_tabDeparture_lblDepartureSearchTxt"]/strong')
date_scraped.append(Date.text)

# Scrape data from the current page (page 1)
flight_elements = driver.find_elements(By.XPATH, '//table[@class="GridClassDeparture"]//tr[contains(@class, "color")]')
for element in flight_elements:
    columns = element.find_elements(By.XPATH, './td')
    airline_flight_list.append(columns[0].text if columns[0].text else 'n/a')
    destination_city_list.append(columns[1].text if columns[1].text else 'n/a')
    scheduled_list.append(columns[2].text if columns[2].text else 'n/a')
    actual_list.append(columns[3].text if columns[3].text else 'n/a')
    remarks_list.append(columns[4].text if columns[4].text else 'n/a')
    gate_list.append(columns[5].text if columns[5].text else 'n/a')

# Initialize the page number to start from 2
page_number = 2

while True:
    # XPath expression to locate the <a> element with the current page number
    xpath_expression = f"//td[@colspan='8']/table/tbody/tr//td/a[contains(@href, 'Page${page_number}') and (text()='{page_number}' or text()='...')]"

    try:
        # Find the element for the current page number
        element = driver.find_element(By.XPATH, xpath_expression)

        # Print the page number before clicking
        print(f"Clicking on page {page_number}")

        Date = driver.find_element(By.XPATH,
                                   '//*[@id="bodySection_TabContainer_Flights_tabDeparture_lblDepartureSearchTxt"]/strong')
        date_scraped.append(Date.text)

        # Use JavaScript to click the element
        driver.execute_script("arguments[0].click();", element)

        # Wait for a brief moment to ensure the page is loaded before proceeding
        time.sleep(2)  # You can adjust the sleep duration if needed

        flight_elements = driver.find_elements(By.XPATH,
                                               '//table[@class="GridClassDeparture"]//tr[contains(@class, "color")]')

        # Extract and process the flight information for the current page
        for element in flight_elements:
            columns = element.find_elements(By.XPATH, './td')
            airline_flight_list.append(columns[0].text if columns[0].text else 'n/a')
            destination_city_list.append(columns[1].text if columns[1].text else 'n/a')
            scheduled_list.append(columns[2].text if columns[2].text else 'n/a')
            actual_list.append(columns[3].text if columns[3].text else 'n/a')
            remarks_list.append(columns[4].text if columns[4].text else 'n/a')
            gate_list.append(columns[5].text if columns[5].text else 'n/a')

        # Increment the page number for the next iteration
        page_number += 1

    except NoSuchElementException:
        # If the element is not found, break the loop
        break

# Close the driver after scraping is done
# driver.quit()

# Create a pandas DataFrame from the scraped data
data = {
    'Date': [date_scraped[0]] * len(airline_flight_list),
    'Airline/Flight': airline_flight_list,
    'Destination City': destination_city_list,
    'Scheduled': scheduled_list,
    'Actual': actual_list,
    'Remarks': remarks_list,
    'Gate': gate_list
}

df = pd.DataFrame(data)

# Upload data to Google Sheets
existing_data = sh.get_all_records()
existing_df = pd.DataFrame(existing_data)
combined_df = pd.concat([existing_df, df], ignore_index=True)

# Update the Google Sheet with the combined data
sh.clear()
sh.update([combined_df.columns.values.tolist()] + combined_df.values.tolist())

# Print or further process the DataFrame
print(combined_df)

