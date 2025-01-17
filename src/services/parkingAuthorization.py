from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import random
import time

class ParkingAuthorizationService:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)


    def select_location_by_similarity(self, t2_data):
        try:
            print("\nSelecting location by similarity...")
            requested_lot = t2_data.get("Requested Lot", "")
            print(f"  - Requested lot from T2: {requested_lot}")
            
            location_selector = "select[name='location.id']"
            location_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, location_selector)))
            location_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, location_selector)))
            
            options = location_element.find_elements(By.TAG_NAME, "option")
            valid_options = [opt for opt in options if opt.get_attribute("value")]
            
            if valid_options and requested_lot:
                # Function to count matching characters in sequence
                def match_score(str1, str2):
                    str1 = str1.lower()
                    str2 = str2.lower()
                    count = 0
                    min_len = min(len(str1), len(str2))
                    for i in range(min_len):
                        if str1[i] == str2[i]:
                            count += 1
                    return count
                
                # Find best matching option
                best_match = None
                best_score = -1
                
                for option in valid_options:
                    option_text = option.text.strip()
                    score = match_score(option_text, requested_lot)
                    print(f"  - Comparing '{option_text}' with '{requested_lot}' - Score: {score}")
                    
                    if score > best_score:
                        best_score = score
                        best_match = option
                
                if best_match:
                    print(f"  - Selected best match: {best_match.text}")
                    best_match.click()
                    return True
                
            print("  - No match found or no valid options available")
            return False
            
        except Exception as e:
            print(f"Error selecting location: {str(e)}")
            return False

    def select_random_location(self):
        try:
            print("\nSelecting random location...")
            location_selector = "#location\\.id"
            location_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, location_selector)))
            location_element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, location_selector)))
            
            options = location_element.find_elements(By.TAG_NAME, "option")
            valid_options = [opt for opt in options if opt.get_attribute("value")]
            
            if valid_options:
                random_option = random.choice(valid_options)
                random_option.click()
                print(f"  - Selected location: {random_option.text}")
                return True
            return False

        except Exception as e:
            print(f"Error selecting location: {str(e)}")
            return False
        

    def fill_dates_and_times(self, t2_data):
        try:
            print("\nFilling dates and times...")
            
            # Get dates from T2 data
            start_date = t2_data["Begin Date"]  # Format: "1/15/2025"
            end_date = t2_data["End Date"]      # Format: "1/15/2025"
            
            # Split dates into components
            start_month, start_day, start_year = start_date.split('/')
            end_month, end_day, end_year = end_date.split('/')

            # Fill start date
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='month'][aria-label='month, Start Date']").send_keys(start_month)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='day'][aria-label='day, Start Date']").send_keys(start_day)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='year'][aria-label='year, Start Date']").send_keys(start_year)
            time.sleep(0.5)

            # Fill end date
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='month'][aria-label='month, Expiry Date']").send_keys(end_month)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='day'][aria-label='day, Expiry Date']").send_keys(end_day)
            time.sleep(0.5)
            self.driver.find_element(By.CSS_SELECTOR, "div[data-segment-type='year'][aria-label='year, Expiry Date']").send_keys(end_year)
            time.sleep(0.5)

            # Fill start time (6:00 AM)
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

            # Fill end time (11:59 PM)
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
            print(f"Error filling dates and times: {str(e)}")
            return False

          

    def click_continue(self):
        try:
            print("\nLocating continue button...")
            continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            print("Clicking continue button...")
            continue_button.click()
            return True
        except Exception as e:
            print(f"Error clicking continue: {str(e)}")
            return False

    def fill_parking_authorization_form(self):
        print("\nStarting parking authorization form fill...")
        success = (
            self.select_random_location() and
            self.fill_dates_and_times() and
            self.click_continue()
        )
        return success