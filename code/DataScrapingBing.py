import json
import time
from time import sleep

from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By


class DataScrapingBing:

    def get_images(self,driver, search_term, mode):
        # List to store all information of current search term
        images_list = []
        driver.get("https://www.bing.com/images")
        time.sleep(2)
        # Reject cookie
        try:
            reject_button = driver.find_element(By.XPATH, "//button[@id='bnp_btn_reject']")
            reject_button.click()
        except NoSuchElementException:
            pass
        time.sleep(2)
        # Enter images page of BING and input the search term
        search_box = driver.find_element(By.XPATH, "//input[@class='b_searchbox ' and @id='sb_form_q']")
        search_box.send_keys(search_term)
        search_box.send_keys(Keys.ENTER)
        time.sleep(2)
        # Get all images from current page in different search mode
        self.adjust_safe_search(driver, mode)
        time.sleep(2)
        # Remove advertisement
        try:
            driver.execute_script(""" var element = arguments[0]; 
                                      element.parentNode.removeChild(element); """,
                                  driver.find_element(By.XPATH, "//div[@id='pole']"))
        except NoSuchElementException:
            pass
        time.sleep(2)
        images = driver.find_elements(By.XPATH, "//ul[@class='dgControl_list']/li/div/div/a/div/img")
        for index, image in enumerate(images):
            # Check whether the current image exists in the browser window
            is_in_viewport = driver.execute_script("""
                    const rect = arguments[0].getBoundingClientRect();
                    return (
                        rect.top >= 0 &&
                        rect.left >= 0 &&
                        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
                        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
                    );
                """, image)

            if is_in_viewport:
                # Save src and location as a dictionary
                '''Example:
                [
                    "tom and jerry horror_1":{
                        "src" : "xxx",
                        "location" : "xxx"
                    }
                ]
                '''
                images_list.append({f"{search_term}_"+str(index):
                                        {"location":image.location,
                                         "src":image.get_attribute("src")}})
        sleep(2)

        return images_list



    def adjust_safe_search(self,driver,mode):
        driver.find_element(By.XPATH, "//span[@id='ftr_ss_hl']").click()
        if mode == "strict":
            driver.find_element(By.XPATH, "//a[@id='ss-strict']").click()
        if mode == "off":
            driver.find_element(By.XPATH, "//a[@id='ss-off']").click()



if __name__ == '__main__':
    """
             a new automated browser window with all tell-tales of automated browser disabled
            """
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")

    # remove all signs of this being an automated browser
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # open the browser with the new options
    chrome_driver = webdriver.Chrome(options=options)

    search = {
        "game" : ["Roblox", "Minecraft", "Among Us", "Clash Royale", "Pokémon Go"],
        "cartoon" : ["Gravity Falls", "The Owl House", "Dexter's Laboratory", "SpongeBob SquarePants", "Powerpuff Girls"],
        "disney": ["Inside Out", "Elemental", "The Little Mermaid", "Turning Red", "Pirates of the Caribbean"],
        "toy":["Barbie", "Pokemon card", "Lego", "Hot Wheels", "Rubik’s Cube"]
    }

    search_keywords = {
        "violence" : ["torture", "murder", "violence", "Bullying", "fights", "weapons", "gunshot", "assault"],
        "sexual content" : ["sex", "nude", "fuck", "porn", "vulgar", "dick", "nsfw", "explicit"],
        "shock and disgusting" : ["horror", "horrible", "creepy","creepiness","dark", "bloody", "decapitation", "dismemberment"]
    }

    # Search all information in dictionary
    search_info_dict = {
        "off_mode": {
            "game_violence" : [],
            "game_sexual content" : [],
            "game_shock and disgusting" : [],
            "cartoon_violence" : [],
            "cartoon_sexual content" : [],
            "cartoon_shock and disgusting" : [],
            "disney_violence": [],
            "disney_sexual content": [],
            "disney_shock and disgusting": [],
            "toy_violence": [],
            "toy_sexual content": [],
            "toy_shock and disgusting": [],
        },
        "strict_mode": {
            "game_violence" : [],
            "game_sexual content" : [],
            "game_shock and disgusting" : [],
            "cartoon_violence" : [],
            "cartoon_sexual content" : [],
            "cartoon_shock and disgusting" : [],
            "disney_violence": [],
            "disney_sexual content": [],
            "disney_shock and disgusting": [],
            "toy_violence": [],
            "toy_sexual content": [],
            "toy_shock and disgusting": [],
        },
    }

    for search_type, search_contents in search.items():
        for keywords_type, keywords in search_keywords.items():
            for search_content in search_contents:
                for keyword in keywords:
                    search = f"{search_content} {keyword}"
                    bing = DataScrapingBing()
                    # Scarp data when safe search is off
                    images_off_mode = bing.get_images(chrome_driver, search, "off")
                    # Scarp data when safe search is strict
                    images_strict_mode = bing.get_images(chrome_driver, search, "strict")
                    search_info_dict["off_mode"][f"{search_type}_{keywords_type}"].append({
                        search : images_off_mode
                    })
                    search_info_dict["strict_mode"][f"{search_type}_{keywords_type}"].append({
                        search: images_off_mode
                    })
    with open("bing_data.json", "w") as f:
        f.write(json.dumps(search_info_dict))
    chrome_driver.close()