from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config.settings import IS_HEROKU_APP

def chrome_driver_path():
    if IS_HEROKU_APP:
        return "/app/.chrome-for-testing/chromedriver-linux64/chromedriver"
    else:
        return "/opt/homebrew/bin/chromedriver"
    
def get_web_page_content(url):
    # Set up the Chrome WebDriver
    service = Service(chrome_driver_path())
    # Replace with your chromedriver path
    options = Options()
    # Run in headless mode (optional)
    options.add_argument("--headless")  # Run in headless mode (no GUI)
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # Navigate to the webpage
        driver.get(url)

        # Wait for the body to be present
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

        # Get the full HTML content
        html_content = driver.page_source

        return html_content

    finally:
        # Close the browser
        driver.quit()

# Example usage
if __name__ == "__main__":
    url = "https://example.com"  # Replace with the URL you want to scrape
    html = get_web_page_content(url)
    print(html)