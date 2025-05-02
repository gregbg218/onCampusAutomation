from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
import logging
import time

logger = logging.getLogger('ThirdPage')

class ThirdPageService:
    def __init__(self, driver):
        logger.info("Initializing ThirdPageService")
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

    def log_all_options(self, location_element):
        logger.info("Retrieving available parking locations")
        options = location_element.find_elements(By.TAG_NAME, "option")
        valid_options = [opt for opt in options if opt.get_attribute("value")]
        logger.info(f"Found {len(valid_options)} available parking locations")
        
        for option in valid_options:
            value = option.get_attribute("value")
            name = option.get_attribute("data-name")
            country = option.get_attribute("data-country")
            logger.debug(f"Location option - ID: {value:5} | Name: {name:40} | Country: {country}")
        return valid_options

    def click_add_locations_button(self):
        logger.info("Clicking 'Add Locations' button")
        try:
            # Using XPath to find the button with "Add Locations" text and the plus icon
            add_locations_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(@class, 'inline-flex') and contains(., 'Add Locations')]"))
            )
            
            logger.info("Found 'Add Locations' button")
            add_locations_button.click()
            logger.info("Successfully clicked 'Add Locations' button")
            return True
        except Exception as e:
            logger.error(f"Failed to click 'Add Locations' button: {str(e)}")
            return False
    
    def search_for_location(self, t2_data):
        logger.info("Searching for location in the search bar")
        try:
            # Get the requested lot name from t2_data
            requested_lot = t2_data.get("Requested Lot", "")
            if not requested_lot:
                logger.warning("No requested lot found in T2 data")
                return False
                
            logger.info(f"Searching for requested lot: {requested_lot}")
            
            # Wait for the search input to be visible and clickable
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input#search[placeholder='Search...']"))
            )
            
            # Clear any existing text and enter the requested lot name
            search_input.clear()
            search_input.send_keys(requested_lot)
            logger.info(f"Entered '{requested_lot}' in search bar")
            
            # Allow time for search results to appear
            time.sleep(1.5)
            
            return True
        except Exception as e:
            logger.error(f"Failed to search for location: {str(e)}")
            return False
    
    def select_location_from_search_results(self, t2_data):
        logger.info("Selecting location from search results")
        try:
            requested_lot_full = t2_data.get("Requested Lot", "")
            requested_lot = requested_lot_full.split()[0] if requested_lot_full else ""

            
            # Find all rows in the search results table
            rows = self.driver.find_elements(By.CSS_SELECTOR, "tbody tr")
            logger.info(f"Found {len(rows)} rows in search results")
            
            if not rows:
                logger.warning("No rows found in search results")
                return False
            
            # Special case for Biggy Structure
            if "biggy" in requested_lot.lower():
                logger.info("Looking for Biggy Structure in search results")
                for row in rows:
                    location_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                    location_text = location_cell.text
                    
                    if "BIGGY" in location_text.upper():
                        logger.info(f"Found Biggy Structure: {location_text}")
                        # Find and click the checkbox in the first cell
                        checkbox = row.find_element(By.CSS_SELECTOR, "td:first-child span[role='checkbox']")
                        checkbox.click()
                        logger.info(f"Selected {location_text}")
                        return True
            
            # Regular case: use scoring to find the best match
            def match_score(str1, str2):
                str1 = str1.lower()
                str2 = str2.lower()
                count = 0
                min_len = min(len(str1), len(str2))
                for i in range(min_len):
                    if str1[i] == str2[i]:
                        count += 1
                return count
            
            matches = []
            for row in rows:
                try:
                    location_cell = row.find_element(By.CSS_SELECTOR, "td:nth-child(2)")
                    location_text = location_cell.text.strip()
                    
                    score = match_score(location_text, requested_lot)
                    matches.append((row, location_text, score))
                    logger.debug(f"Match score - Location: {location_text:30} | Score: {score:2}")
                except Exception as e:
                    logger.error(f"Error processing row: {str(e)}")
                    continue
            
            if not matches:
                logger.warning("No valid matches found in search results")
                # If no matches, select the first row if available
                if rows:
                    first_row = rows[0]
                    checkbox = first_row.find_element(By.CSS_SELECTOR, "td:first-child span[role='checkbox']")
                    checkbox.click()
                    logger.info("Selected first row as fallback")
                    return True
                return False
            
            # Sort by score and select the best match
            matches.sort(key=lambda x: x[2], reverse=True)
            logger.info("Top 3 matching locations:")
            for i, (row, location_text, score) in enumerate(matches[:3 if len(matches) >= 3 else len(matches)], 1):
                logger.info(f"{i}. {location_text:30} | Score: {score:2}")
            
            best_match = matches[0]
            best_row = best_match[0]
            checkbox = best_row.find_element(By.CSS_SELECTOR, "td:first-child span[role='checkbox']")
            checkbox.click()
            logger.info(f"Selected best match: {best_match[1]} with score: {best_match[2]}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to select location from search results: {str(e)}")
            return False
    
    
            
    def select_location_by_similarity(self, t2_data):
        logger.info("Starting location selection by similarity")
        requested_lot = t2_data.get("Requested Lot", "")
        logger.info(f"Requested parking lot: {requested_lot}")
        
        location_selector = "select[name='locations.0.id']"
        location_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, location_selector)))
        location_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, location_selector)))
        
        valid_options = self.log_all_options(location_element)
        
        if valid_options and requested_lot:
            if "biggy" in requested_lot.lower():
                for option in valid_options:
                    if "P8 - BIGGY STRUCTURE" in option.text.upper():
                        logger.info(f"Direct match found for Biggy Structure: {option.text}")
                        option.click()
                        return True

            def match_score(str1, str2):
                str1 = str1.lower()
                str2 = str2.lower()
                count = 0
                min_len = min(len(str1), len(str2))
                for i in range(min_len):
                    if str1[i] == str2[i]:
                        count += 1
                return count
            
            matches = []
            for option in valid_options:
                option_text = option.text.strip()
                score = match_score(option_text, requested_lot)
                matches.append((option, score))
                logger.debug(f"Match score - Location: {option_text:30} | Score: {score:2}")
            
            matches.sort(key=lambda x: x[1], reverse=True)
            logger.info("Top 3 matching locations:")
            for i, (option, score) in enumerate(matches[:3], 1):
                logger.info(f"{i}. {option.text:30} | Score: {score:2}")
            
            if matches:
                best_match = matches[0][0]
                logger.info(f"Selected best match: {best_match.text} with score: {matches[0][1]}")
                best_match.click()
                return True
            
        logger.warning("No suitable location match found")
        return False

    def select_random_location(self):
        logger.info("Selecting random location")
        location_selector = "#locations\\.0\\.id"
        location_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, location_selector)))
        location_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, location_selector)))
        
        valid_options = self.log_all_options(location_element)
        
        if valid_options:
            random_option = random.choice(valid_options)
            logger.info(f"Randomly selected location: {random_option.text}")
            random_option.click()
            return True
            
        logger.warning("No valid location options found")
        return False

    def click_continue(self):
        try:
            logger.info("Attempting to click continue button")
            continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            continue_button.click()
            logger.info("Continue button clicked successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to click continue button: {str(e)}")
            return False
            
    def click_choose_button(self):
        logger.info("Attempting to click Choose button")
        try:
            choose_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, 
                "//button[contains(@class, 'bg-primary-600') and contains(., 'Choose')]"))
            )
            
            logger.info("Found Choose button")
            choose_button.click()
            logger.info("Successfully clicked Choose button")
            return True
        except Exception as e:
            logger.error(f"Failed to click Choose button: {str(e)}")
            return False

    def process_third_page(self, t2_data):
        logger.info("Starting third page processing")
        
        # First click "Add Locations" button
        if not self.click_add_locations_button():
            logger.error("Failed to click 'Add Locations' button")
            # Try the old way as fallback
            return self.select_location_by_similarity(t2_data) and self.click_continue()
        
        # Then search for the location by name
        if not self.search_for_location(t2_data):
            logger.error("Failed to search for location")
            # Try the old way as fallback
            return self.select_location_by_similarity(t2_data) and self.click_continue()
        
        # Select the location from search results
        if not self.select_location_from_search_results(t2_data):
            logger.error("Failed to select location from search results")
            # Try the old way as fallback
            return self.select_location_by_similarity(t2_data) and self.click_continue()
        
        # Confirm the selection
        # if not self.click_confirm_selection():
        #     logger.warning("Failed to confirm location selection, continuing anyway")
        
        # Click the Choose button before continuing
        if not self.click_choose_button():
            logger.warning("Failed to click Choose button, attempting to continue anyway")
        
        # Finally click continue
        success = self.click_continue()
        
        logger.info(f"Third page completion {'successful' if success else 'failed'}")
        return success
    


    