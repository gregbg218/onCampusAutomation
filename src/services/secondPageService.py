from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logger = logging.getLogger('SecondPage')

class SecondPageService:
    def __init__(self, driver):
        logger.info("Initializing SecondPageService")
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)

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

            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='month'][aria-label='month, Expiry Date']").send_keys(end_month)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='day'][aria-label='day, Expiry Date']").send_keys(end_day)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='year'][aria-label='year, Expiry Date']").send_keys(end_year)
            time.sleep(0.5)

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

    def process_second_page(self, t2_data):
        logger.info("Starting second page processing")
        success = (
            self.fill_dates_and_times(t2_data) and
            self.click_continue()
        )
        logger.info(f"Second page completion {'successful' if success else 'failed'}")
        return success