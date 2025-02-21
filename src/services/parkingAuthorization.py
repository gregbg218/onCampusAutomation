from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import random
import time
import logging

logger = logging.getLogger('ParkingAuth')

class ParkingAuthorizationService:
    def __init__(self, driver):
        logger.info("Initializing ParkingAuthorizationService")
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

    def fill_dates_and_times(self, t2_data):
        logger.info("Starting date and time fill process")
        try:
            start_date = t2_data["Begin Date"]
            end_date = t2_data["End Date"]
            
            start_month, start_day, start_year = start_date.split('/')
            end_month, end_day, end_year = end_date.split('/')
            
            logger.info(f"Processing dates - Start: {start_month}/{start_day}/{start_year}, End: {end_month}/{end_day}/{end_year}")

            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='month'][aria-label='month, Start Date']").send_keys(start_month)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='day'][aria-label='day, Start Date']").send_keys(start_day)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='year'][aria-label='year, Start Date']").send_keys(start_year)
            time.sleep(0.5)
            logger.debug("Start date fields filled")

            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='month'][aria-label='month, Expiry Date']").send_keys(end_month)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='day'][aria-label='day, Expiry Date']").send_keys(end_day)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='year'][aria-label='year, Expiry Date']").send_keys(end_year)
            time.sleep(0.5)
            logger.debug("End date fields filled")

            logger.info("Setting start time to 6:00 AM")
            start_time_container = self.driver.find_element(By.ID, "startTime")
            hour = start_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='hour']")
            self.driver.execute_script("arguments[0].click();", hour)
            hour.send_keys("06")
            time.sleep(0.5)
            
            minute = start_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='minute']")
            self.driver.execute_script("arguments[0].click();", minute)
            minute.send_keys("00")
            time.sleep(0.5)
            
            day_period = start_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='dayPeriod']")
            self.driver.execute_script("arguments[0].click();", day_period)
            day_period.send_keys("AM")
            time.sleep(0.5)
            logger.debug("Start time set successfully")

            logger.info("Setting end time to 11:59 PM")
            end_time_container = self.driver.find_element(By.ID, "endTime")
            hour = end_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='hour']")
            self.driver.execute_script("arguments[0].click();", hour)
            hour.send_keys("11")
            time.sleep(0.5)
            
            minute = end_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='minute']")
            self.driver.execute_script("arguments[0].click();", minute)
            minute.send_keys("59")
            time.sleep(0.5)
            
            day_period = end_time_container.find_element(By.CSS_SELECTOR, "div[data-segment-type='dayPeriod']")
            self.driver.execute_script("arguments[0].click();", day_period)
            day_period.send_keys("PM")
            time.sleep(0.5)
            logger.debug("End time set successfully")

            return True

        except Exception as e:
            logger.error(f"Failed to fill dates and times: {str(e)}")
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

    def fill_parking_authorization_form(self, t2_data):
        logger.info("Starting parking authorization form fill process")
        success = (
            self.select_location_by_similarity(t2_data) and
            self.fill_dates_and_times(t2_data) and
            self.click_continue()
        )
        logger.info(f"Form completion {'successful' if success else 'failed'}")
        return success