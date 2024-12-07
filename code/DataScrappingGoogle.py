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
import csv
from itertools import product



def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    driver = webdriver.Chrome(service=Service("/Users/mac/Downloads/chromedriver-mac-arm64/chromedriver"), options=options)
    driver.set_window_size(1920, 1080)
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

def scrape_all_images(driver, scroll_iteration):
    """
    Scrapes all image URLs along with their positions and dimensions.
    """
    try:
        images = driver.find_elements(By.TAG_NAME, "img")
        image_data_list = []
        for img in images:
            image_url = img.get_attribute("src") or img.get_attribute("data-src")
            if image_url and "data:image/gif" not in image_url:
                width = int(img.get_attribute("width") or 0)
                height = int(img.get_attribute("height") or 0)
                if width >= 100 and height >= 100:
                    location = img.location
                    size = img.size
                    image_data_list.append({
                        "url": image_url,
                        "scroll": scroll_iteration,  # Add scroll iteration here
                        "location": location,
                        "size": size
                    })
        return image_data_list
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


def is_in_center(location_x, page_width, center_percentage=0.2):
    """
    Determine if an image is in the center region of the page.
    """
    center_start = (1 - center_percentage) / 2 * page_width
    center_end = (1 + center_percentage) / 2 * page_width
    return center_start <= location_x <= center_end


def scrape_and_save_images_with_metadata(base_folder, combined_terms, safesearch_mode="aus"):
    """
    Scrape and save images along with search metadata, including SafeSearch mode.
    """
    driver = init_driver()
    set_safesearch(driver, mode=safesearch_mode)

    # Store all results
    all_results = []

    for i,term in enumerate(combined_terms):
        search_term = term["combined_term"]  # Use the combined term for search
        print(f"Scraping images for: {search_term} (SafeSearch: {safesearch_mode})")
        # Automatic refresh every 5 terms to keep session active
        if i > 0 and i % 5 == 0:
            print("Refreshing driver to keep session alive...")
            driver.refresh()
            time.sleep(5)  # Wait to ensure refresh completes


        # Create a folder for each search term
        folder_path = os.path.join(base_folder, search_term.replace(" ", "_"))
        os.makedirs(folder_path, exist_ok=True)

        driver.get(f"https://www.google.com/search?q={search_term}&tbm=isch")
        handle_privacy_popup(driver)
        time.sleep(5)  # Wait for the images to load

        # Scrape images visible in the viewport
        image_data_list = scrape_all_images(driver, scroll_iteration=1)

        positions = []
        image_counter = 1

        for image_data in image_data_list:
            location_x = image_data["location"]["x"]
            location_y = image_data["location"]["y"]

            # Save image if it's in the viewport
            if 0 <= location_x <= driver.execute_script("return window.innerWidth;") and \
                    0 <= location_y <= driver.execute_script("return window.innerHeight;"):
                file_name = f"{search_term}_image_{image_counter}"
                image_counter += 1

                # Save image and collect metadata
                save_image(image_data["url"], folder_path, file_name)

                # Append metadata to positions
                positions.append({
                    "entity_type": term["entity_type"],
                    "entity": term["entity"],
                    "harmful_type": term["harmful_type"],
                    "harmful_term": term["harmful_term"],
                    "search_term": search_term,
                    "safesearch_mode": safesearch_mode,  # Add SafeSearch mode
                    "file_name": file_name,
                    "image_url": image_data["url"],
                    "location": image_data["location"],
                    "size": image_data["size"]
                })

        # Save metadata for this search term
        all_results.extend(positions)
        save_positions_to_csv(os.path.join(folder_path, "image_positions.csv"), positions)

        print(f"Finished scraping images for {search_term}")

    driver.quit()
    print("Scraping completed.")

    # Save all results to a master CSV
    save_positions_to_csv(os.path.join(base_folder, "all_image_metadata.csv"), all_results)


def save_positions_to_csv(csv_path, positions):
    """
    Save image metadata to a CSV file, including SafeSearch mode.
    """
    with open(csv_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Add headers
        writer.writerow([
            "Entity Type", "Entity", "Harmful Type", "Harmful Term",
            "Search Term", "SafeSearch Mode", "File Name", "Image URL", "X", "Y", "Width", "Height"
        ])
        for position in positions:
            writer.writerow([
                position["entity_type"],
                position["entity"],
                position["harmful_type"],
                position["harmful_term"],
                position["search_term"],
                position["safesearch_mode"],  # Include SafeSearch mode
                position["file_name"],
                position["image_url"],
                position["location"]["x"],
                position["location"]["y"],
                position["size"]["width"],
                position["size"]["height"]
            ])
    print(f"Saved metadata to {csv_path}")





if __name__ == "__main__":
    base_folder = "./images"  # Base folder to save images
    safesearch_mode = "aus"  # SafeSearch mode: "filter", "blur", or "aus"

    # Generate the combined terms
    from itertools import product
    entity= {
    "game" : ["Roblox", "Minecraft", "Among Us", "Clash Royale", "Pokémon Go"],
    "cartoon" : ["Gravity Falls", "The Owl House", "Dexter's Laboratory", "SpongeBob SquarePants", "Powerpuff Girls"],
    "disney": ["Inside Out", "Elemental", "The Little Mermaid", "Turning Red", "Pirates of the Caribbean"],
    "toy":["Barbie", "Pokemon card", "Lego", "Hot Wheels", "Rubik’s Cube"]
}

    harmful = {
    "violence" : ["torture", "murder", "violence", "Bullying", "fights", "weapons", "gunshot", "assault"],
    "sexual content" : ["sex", "nude", "fuck", "porn", "vulgar", "dick", "nsfw", "explicit"],
    "shock and disgusting" : ["horror", "horrible", "creepy","creepiness","dark", "bloody", "decapitation", "dismemberment"]
}


    # Combine terms
    combined_terms = []
    for entity_category, entity_terms in entity.items():
        for harmful_category, harmful_terms in harmful.items():
            for x, y in product(entity_terms, harmful_terms):
                combined_terms.append({
                    "entity_type": entity_category,
                    "entity": x,
                    "harmful_type": harmful_category,
                    "harmful_term": y,
                    "combined_term": f"{x} {y}"
                })

    # Run the scraping with metadata
    scrape_and_save_images_with_metadata(base_folder, combined_terms, safesearch_mode=safesearch_mode)
