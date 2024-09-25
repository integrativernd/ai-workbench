from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def get_web_page_content(url, wait_time=10):
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Set up the Chrome driver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Navigate to the URL
        driver.get(url)

        # Wait for the page to load
        WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )

        # Allow some time for JavaScript to execute
        time.sleep(wait_time)

        # Get the page source
        page_source = driver.page_source

        # Get the text content
        text_content = driver.find_element(By.TAG_NAME, "body").text

        return text_content

    finally:
        # Close the browser
        driver.quit()

# Example usage
if __name__ == "__main__":
    url = "https://example.com"  # Replace with the URL you want to scrape
    page_source, text_content = read_webpage_content(url)

    print("Page Source:")
    print(page_source[:500] + "...")  # Print first 500 characters of page source

    print("\nText Content:")
    print(text_content[:500] + "...")  # Print first 500 characters of text content