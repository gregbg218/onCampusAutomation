from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import logging

logger = logging.getLogger('EventSettings')

class EventSettingsService:
    def __init__(self, driver, t2_data):
        logger.info("Initializing EventSettingsService")
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.t2_data = t2_data

    def toggle_switch(self, switch_id):
        logger.info(f"Toggling switch: {switch_id}")
        switch = self.wait.until(EC.element_to_be_clickable((By.ID, switch_id)))
        switch.click()
        time.sleep(1)

    def calculate_days_and_rate(self):
        try:
            logger.info("Calculating parking rate based on days")
            begin_date = datetime.strptime(self.t2_data['Begin Date'], '%m/%d/%Y')
            end_date = datetime.strptime(self.t2_data['End Date'], '%m/%d/%Y')
            days = (end_date - begin_date).days + 1
            rate = days * 20.50
            logger.info(f"Calculated rate for {days} days: ${rate}")
            return rate
        except Exception as e:
            logger.error(f"Error calculating rate: {str(e)}")
            logger.info("Using default rate of $20.50")
            return 20.50

    def configure_code(self):
        try:
            logger.info("Configuring access code settings")
            
            try:
                same_code_option = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), 'Parkers input the same code')]")
                ))
                same_code_option.click()
                logger.debug("Selected 'same code' option")
            except:
                logger.debug("Same code option already selected")

            code_input = self.wait.until(EC.presence_of_element_located((By.ID, "sameCode")))
            reservation_uid = self.t2_data.get('Confirmation/Reservation UID', '')
            code_input.clear()
            code_input.send_keys(reservation_uid)
            logger.info(f"Access code set to: {reservation_uid}")
          
        except Exception as e:
            logger.error(f"Error configuring access code: {str(e)}")

    def configure_rate(self):
        try:
            logger.info("Configuring rate settings")
            # time.sleep(1)
            
            rate_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[inputmode='numeric']")
            ))
            
            rate = self.calculate_days_and_rate()
            rate_input.clear()
            rate_input.send_keys(str(rate))
            logger.info(f"Rate configured: ${rate}")
            # time.sleep(0.5)
                
        except Exception as e:
            logger.error(f"Error configuring rate: {str(e)}")

    def configure_max_parkers(self):
        try:
            logger.info("Configuring maximum parkers")
            max_parkers_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='e.g. 48']")
            ))
            cars_requested = self.t2_data.get('Cars Requested', '1')
            max_parkers_input.clear()
            max_parkers_input.send_keys(cars_requested)
            logger.info(f"Maximum parkers set to: {cars_requested}")
            # time.sleep(0.5)
        except Exception as e:
            logger.error(f"Error configuring maximum parkers: {str(e)}")

    def fill_first_field(self):
        try:
            logger.info("Configuring first name field")
            field_name_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='e.g. Driver Name']")
            ))
            field_name_input.clear()
            field_name_input.send_keys("First Name")
            # time.sleep(0.5)

            first_required_toggle = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "additionalInfo.0.isRequired")
            ))
            first_required_toggle.click()
            # time.sleep(0.5)
            logger.debug("First name field configured and set as required")
        except Exception as e:
            logger.error(f"Error configuring first name field: {str(e)}")

    def add_last_name_field(self):
        try:
            logger.info("Adding last name field")
            add_field_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Add Field']")
            ))
            add_field_button.click()
            # time.sleep(0.5)

            field_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g. Driver Name']")
            if field_inputs:
                last_input = field_inputs[-1]
                last_input.clear()
                last_input.send_keys("Last Name")
                # time.sleep(0.5)

                second_required_toggle = self.wait.until(EC.element_to_be_clickable(
                    (By.ID, "additionalInfo.1.isRequired")
                ))
                second_required_toggle.click()
                # time.sleep(0.5)
                logger.debug("Last name field configured and set as required")
        except Exception as e:
            logger.error(f"Error adding last name field: {str(e)}")

    def configure_additional_info(self):
        logger.info("Configuring additional information fields")
        # time.sleep(0.5)
        self.fill_first_field()
        # time.sleep(0.5)
        self.add_last_name_field()
        # time.sleep(0.5)

    def click_continue(self):
        logger.info("Proceeding to next step")
        continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        continue_button.click()
        logger.debug("Continue button clicked")

    def configure_all_settings(self):
        try:
            logger.info("Starting event settings configuration")
            
            # Check if "Exceed Car Requested Set Value" is "Yes" or "No"
            exceed_value = self.t2_data.get('Exceed Car Requested Set Value', 'No')
            logger.info(f"Exceed Car Requested Set Value: {exceed_value}")
            
            settings = {
                "hasAdditionalInfo": "Collect Additional Information",
                "hasCode": "Require a Code",
                "hasRate": "Add Rate"
            }
            
            # Only add max parkers setting if exceed_value is "No"
            if exceed_value == "No":
                settings["hasMaxParkers"] = "Set Max Number of Parkers"

            for setting_id, setting_name in settings.items():
                logger.info(f"Configuring setting: {setting_name}")
                self.toggle_switch(setting_id)
                # time.sleep(1)
                
                if setting_id == "hasMaxParkers":
                    self.configure_max_parkers()
                elif setting_id == "hasAdditionalInfo":
                    self.configure_additional_info()
                elif setting_id == "hasCode":
                    self.configure_code()
                elif setting_id == "hasRate":
                    self.configure_rate()

            self.click_continue()
            logger.info("Event settings configuration completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error configuring event settings: {str(e)}")
            return False