from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
import tempfile
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
chrome_options.add_argument("--incognito")
chrome_options.add_argument("--headless")                # run without UI
chrome_options.add_argument("--no-sandbox")              # required in many Linux CI environments
chrome_options.add_argument("--disable-dev-shm-usage")   # overcome limited /dev/shm
chrome_options.add_argument("--disable-gpu")             # recommended for headless
chrome_options.add_argument("--window-size=1920,1080")   # ensure proper rendering
chrome_options.add_argument("--disable-extensions")      # reduce interference

# create a unique user-data-dir so profiles never collide
tmp_profile = tempfile.mkdtemp()
chrome_options.add_argument(f"--user-data-dir={tmp_profile}")

# Initialize WebDriver
service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# Random number of submissions (7 to 14)
num_submissions = random.randint(7, 14)
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

        # Fill in the Nomination Reason (optional)
        message = NOMINATION_MESSAGES[i % len(NOMINATION_MESSAGES)]
        try:
            print("Filling nomination reason...")
            # Try primary selector
            try:
                nomination_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//textarea[@aria-label='Your answer']"))
                )
            except:
                print("Primary nomination selector failed, trying fallback...")
                nomination_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "textarea.KHxj8b.tL9Q4c"))
                )
            nomination_field.clear()  # Clear any existing text
            nomination_field.send_keys(message)
            print(f"Nomination reason set to: {message}")
        except Exception as e:
            print(f"Error filling nomination reason on attempt {i+1}: {e}")
            # Continue to submission since nomination is optional

        # Submit the form
        try:
            print("Looking for submit button...")
            # Try primary selector
            try:
                submit_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[@role='button' and .//span[text()='Submit']]"))
                )
            except:
                print("Primary submit selector failed, trying fallback...")
                submit_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'uArJ5e') and .//span[contains(text(), 'Submit')]]"))
                )
            
            # Log button attributes for debugging
            button_attrs = driver.execute_script(
                "return { 'outerHTML': arguments[0].outerHTML, 'aria-disabled': arguments[0].getAttribute('aria-disabled'), 'class': arguments[0].getAttribute('class') };",
                submit_button
            )
            print(f"Submit button attributes: {button_attrs}")

            # Check if button is disabled
            if button_attrs.get('aria-disabled') == 'true' or 'disabled' in button_attrs.get('class', '') or 'NPEfkd' in button_attrs.get('class', ''):
                print("Submit button is disabled, cannot proceed")
                continue

            time.sleep(2)  # Delay to ensure form is ready
            try:
                submit_button.click()
                print("Submit button clicked (standard)")
            except:
                print("Standard click failed, trying JavaScript click...")
                driver.execute_script("arguments[0].click();", submit_button)
                print("Submit button clicked (JavaScript)")
            
            # Try JavaScript form submission as final fallback
            try:
                form = driver.find_element(By.XPATH, "//form")
                driver.execute_script("arguments[0].submit();", form)
                print("Form submitted via JavaScript")
            except:
                print("JavaScript form submission not attempted (form not found)")

            # Check for CAPTCHA
            try:
                captcha_container = driver.find_element(By.XPATH, "//div[@data-should-execute-invisible-captcha-challenge='true']")
                print("CAPTCHA challenge detected, cannot proceed automatically")
                continue
            except:
                pass  # No CAPTCHA detected

            # Check for validation errors
            try:
                error_message = driver.find_element(By.XPATH, "//div[@role='alert' or contains(@class, 'error')]")
                print(f"Form validation error detected: {error_message.text}")
                continue
            except:
                pass  # No validation error found

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
    # Clean up temporary profile
    try:
        os.rmdir(tmp_profile)
    except:
        pass
    print("Script completed")
