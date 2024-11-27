import os
import requests
import base64
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
import time


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service("/Users/mac/Downloads/chromedriver-mac-arm64/chromedriver"), options=options)
    return driver


def handle_privacy_popup(driver):
    """
    Handles the privacy popup for Google.
    """
    try:
        reject_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Alle ablehnen')]"))
        )
        reject_button.click()
        print("Privacy popup dismissed.")
        time.sleep(2)
    except TimeoutException:
        print("No privacy popup found or already handled.")


def set_safesearch(driver, mode="aus"):
    """
    Sets the SafeSearch mode directly on the SafeSearch settings page.
    """
    try:
        driver.get("https://www.google.com/safesearch")
        time.sleep(2)

        if mode.lower() == "filter":
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Filter')]"))
            )
        elif mode.lower() == "blur":
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Unkenntlich machen')]"))
            )
        else:
            option = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Aus')]"))
            )

        option.click()
        print(f"SafeSearch set to: {mode.capitalize()}")
        time.sleep(2)
    except TimeoutException:
        print("Failed to configure SafeSearch. It might already be set.")


def scrape_all_images(driver):
    """
    Scrapes all image URLs from the Google Images results page.
    """
    try:
        images = driver.find_elements(By.TAG_NAME, "img")
        image_urls = []
        for img in images:
            image_url = img.get_attribute("src") or img.get_attribute("data-src")
            if image_url and "data:image/gif" not in image_url:
                width = int(img.get_attribute("width") or 0)
                height = int(img.get_attribute("height") or 0)
                if width >= 100 and height >= 100:
                    image_urls.append(image_url)
        return image_urls
    except Exception as e:
        print(f"Error scraping images: {e}")
        return []


def save_image(image_url, folder_name, file_name, retry_count=3):
    """
    Saves an image to the specified folder with a given file name.
    """
    try:
        file_path = os.path.join(folder_name, f"{file_name}.jpg")

        if image_url.startswith("data:image/"):
            header, encoded = image_url.split(",", 1)
            image_data = base64.b64decode(encoded)
            with open(file_path, "wb") as f:
                f.write(image_data)
        else:
            for attempt in range(retry_count):
                response = requests.get(image_url, timeout=10)
                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    break
                else:
                    print(f"Failed attempt {attempt + 1} for image: {image_url}")
                    time.sleep(2)
    except Exception as e:
        print(f"Error saving image {file_name}: {e}")


def scrape_and_save_images(base_folder, search_terms, num_images=10, safesearch_mode="aus"):
    """
    Main function to scrape and save images for a list of search terms.
    """
    driver = init_driver()

    # Set SafeSearch mode
    set_safesearch(driver, mode=safesearch_mode)

    for search_term in search_terms:
        print(f"Scraping images for: {search_term}")

        # Create a folder for each search term
        folder_path = os.path.join(base_folder, search_term.replace(" ", "_"))
        os.makedirs(folder_path, exist_ok=True)

        driver.get(f"https://www.google.com/search?q={search_term}&tbm=isch")
        handle_privacy_popup(driver)
        time.sleep(5)

        # Scroll down to load more images
        last_height = driver.execute_script("return document.body.scrollHeight")
        scroll_attempts = 0
        while scroll_attempts < 5:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
            last_height = new_height

        # Scrape and save images
        image_urls = scrape_all_images(driver)[:num_images]

        for index, image_url in enumerate(image_urls, start=1):
            file_name = f"{search_term}_{index}"
            save_image(image_url, folder_path, file_name)

        print(f"Finished scraping {len(image_urls)} images for {search_term}.")

    driver.quit()


if __name__ == "__main__":
    base_folder = "./images"
    search_terms = ["Harry Potter"] # List of search terms to be decided
    scrape_and_save_images(base_folder, search_terms, num_images=10, safesearch_mode="filter")
