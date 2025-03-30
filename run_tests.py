import time
import pandas as pd
import allure
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# Load test cases from CSV
df = pd.read_csv("test_cases.csv")

@allure.step("Initialize WebDriver")
def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")  # Run in headless mode for CI/CD
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

@allure.step("Run Test Cases from CSV")
def run_tests():
    driver = init_driver()

    for index, row in df.iterrows():
        website_url = row["website_url"]
        username = row["username"]
        password = row["password"]
        username_field = row["username_field"]
        password_field = row["password_field"]
        submit_button = row["submit_button"]
        success_indicators = row["success_indicators"].split(",")
        expected = row["expected"]

        allure.attach(f"Testing {website_url}", name="Website URL", attachment_type=allure.attachment_type.TEXT)

        try:
            driver.get(website_url)
            time.sleep(2)

            # Fill username and password fields
            driver.find_element(By.NAME, username_field).send_keys(username)
            driver.find_element(By.NAME, password_field).send_keys(password)
            driver.find_element(By.NAME, submit_button).click()

            time.sleep(3)  # Wait for login result

            # Check success indicators
            actual_result = "Failed"
            for indicator in success_indicators:
                if indicator and driver.current_url.find(indicator) != -1:
                    actual_result = "Success"
                    break

            allure.attach(actual_result, name="Actual Result", attachment_type=allure.attachment_type.TEXT)

            # Capture screenshot
            screenshot_path = f"screenshots/test_{index}.png"
            driver.save_screenshot(screenshot_path)
            allure.attach.file(screenshot_path, attachment_type=allure.attachment_type.PNG)

            print(f"Test {index}: {expected} - {actual_result}")

        except Exception as e:
            allure.attach(str(e), name="Error", attachment_type=allure.attachment_type.TEXT)
            print(f"Error in Test {index}: {e}")

    driver.quit()

if __name__ == "__main__":
    run_tests()
