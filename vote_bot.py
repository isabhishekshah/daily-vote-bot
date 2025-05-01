from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

import os
import platform

# Path to ChromeDriver
if platform.system() == "Windows":
    CHROMEDRIVER_PATH = "F:/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe"
else:
    CHROMEDRIVER_PATH = "/usr/bin/chromedriver"


# URL of the Google Form
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSf2fHJ3ehIwzNqWJL4PWIhMUa2cOGQXc_k1Sto-u3LJMqY7Qg/viewform"

# Nomination reason messages
NOMINATION_MESSAGES = [
    "The",
    "System",
    "has",
    "been",
    "Compromised",
    "---Cuz why not---",
    "SORRY"

]

# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--incognito")  # Use incognito mode
# chrome_options.add_argument("--headless")  # Uncomment for headless mode (no visible browser)

# Initialize WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Random number of submissions (7 to 14)
num_submissions = random.randint(1, 2)
print(f"Will submit {num_submissions} votes")

try:
    for i in range(num_submissions):
        print(f"Submitting form {i+1}/{num_submissions}")

        # Open the Google Form
        driver.get(FORM_URL)
        
        # Wait for the radio button group to load
        print("Waiting for radio buttons to load...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='radiogroup']"))
        )

        # Select "Abhi" radio button
        try:
            print("Selecting 'Abhi' radio button...")
            abhi_radio = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//div[@role='radio' and @data-value='Abhi']"))
            )
            abhi_radio.click()
            print("'Abhi' selected")
        except Exception as e:
            print(f"Error selecting 'Abhi' on attempt {i+1}: {e}")
            continue

        # Fill in the Nomination Reason
        try:
            print("Filling nomination reason...")
            message = NOMINATION_MESSAGES[i % len(NOMINATION_MESSAGES)]
            nomination_field = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.KHxj8b.tL9Q4c"))
            )
            nomination_field.send_keys(message)
            print(f"Nomination reason set to: {message}")
        except Exception as e:
            print(f"Error filling nomination reason on attempt {i+1}: {e}")
            continue

        # Submit the form
        try:
            print("Looking for submit button...")
            submit_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Submit']"))
            )
            submit_button.click()
            print("Submit button clicked")

            # Wait for the confirmation page
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Your response has been recorded')]"))
            )
            print(f"Submission {i+1} successful")
        except Exception as e:
            print(f"Error submitting form on attempt {i+1}: {e}")
            continue

        # Pause to avoid overwhelming the server
        time.sleep(2)

finally:
    # Close the browser
    driver.quit()
    print("Script completed")
