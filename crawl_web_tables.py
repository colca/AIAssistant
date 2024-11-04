from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import time

loginUrl = "https://secret wiki"
service = Service('/opt/homebrew/bin/chromedriver')
output_file_name = "oe_data.json"

driver = webdriver.Chrome(service=service)

driver.get(loginUrl)
#driver.execute_script("window.focus();")  # Bring the current window to the front
driver.switch_to.window(driver.current_window_handle)

email_input = driver.find_element(By.ID, 'emailAddressField')
email_input.send_keys("xifeng@coupang.com")  # Enter the email

#time.sleep(20)  # This is a simple wait; consider using WebDriverWait for better handling

# Find the new field with the specified class
#okta = driver.find_element(By.CLASS_NAME, 'button select-factor link-button')
#okta.click()  # Click the button

time.sleep(60)

import pandas as pd
import json

def extract_from_root(driver, url):
    # Navigate to the root wiki page
    driver.get(url)

    # Wait for the page to load
    time.sleep(5)

    # Find the parent element with the specified class
    parent_element = driver.find_element(By.CLASS_NAME, 'wiki-content')  # Replace with your class name

    # Find all links inside the parent element
    links = parent_element.find_elements(By.TAG_NAME, 'a')  # Find all <a> tags

    link_data = [link.get_attribute('href') for link in links if link.get_attribute('href')]

    all_data = []
    # Iterate through each link and extract data
    for link in link_data:
        try:
            data = extract_wiki_table(driver, link)
            all_data.extend(data)
        except Exception as e:
                print(f"Could not find a table in {link}: {e}")

    # Save the extracted data to a JSON file
    try:
        with open(output_file_name, 'w') as json_file:
            json.dump(all_data, json_file, indent=4)
    except Exception as e:
                    print(f"could not write json file {output_file_name}: {e}")

    # Write the list to a plain text file
    with open('data.txt', 'w') as txt_file:
        for item in all_data:
            txt_file.write(f"{item}\n")

def extract_wiki_table(driver, url):

    driver.get(url)
    time.sleep(5)
    page_content = driver.page_source

    print("page_content\n")
    #print(page_content)

    confluence_table = driver.find_element(By.CSS_SELECTOR, '[class*="confluenceTable"]')

    rows = confluence_table.find_elements(By.TAG_NAME, 'tr')

    rows_data = []
    # Read columns data from each row
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, 'td')  # Get all columns in the row
        column_data = [column.text for column in columns if column.text]  # Extract text from each column

        if column_data is None or not column_data:
            continue

        # Find images in the current row
        images = row.find_elements(By.TAG_NAME, 'img')  # Get all images in the row
        image_data = [img.get_attribute('src') for img in images]  # Extract the 'src' attribute of each image

        # Combine column data and image data
        row_data = {
            'columns': column_data,
            'images': image_data
        }
        print(row_data)
        rows_data.append(row_data)

    return rows_data


url = 'https://wiki.coupang.net/display/SD/%5B2024+Q2%5D%5BW16%5D+Infra'
root_url = 'https://wiki.coupang.net/display/SD/Operational+Excellence+-+Infrastructure'
extract_from_root(driver, root_url)

# Close the driver
driver.quit()
