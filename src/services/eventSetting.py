from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time

class EventSettingsService:
    def __init__(self, driver, t2_data):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)
        self.t2_data = t2_data

    def toggle_switch(self, switch_id):
        print(f"\nToggling {switch_id}...")
        switch = self.wait.until(EC.element_to_be_clickable((By.ID, switch_id)))
        switch.click()
        time.sleep(2)

    def calculate_days_and_rate(self):
        try:
            print("\nCalculating rate based on days...")
            begin_date = datetime.strptime(self.t2_data['Begin Date'], '%m/%d/%Y')
            end_date = datetime.strptime(self.t2_data['End Date'], '%m/%d/%Y')
            days = (end_date - begin_date).days + 1
            rate = days * 20.50
            print(f"Days: {days}, Rate: ${rate}")
            return rate
        except Exception as e:
            print(f"Error calculating rate: {str(e)}")
            return 20.50

    def configure_code(self):
        try:
            print("\nConfiguring code...")
            time.sleep(2)
            
            # Click the same code option if needed
            try:
                same_code_option = self.wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//div[contains(text(), 'Parkers input the same code')]")
                ))
                same_code_option.click()
                time.sleep(1)
            except:
                print("Same code option already selected")

            # Find and fill code using ID
            code_input = self.wait.until(EC.presence_of_element_located((By.ID, "sameCode")))
            reservation_uid = self.t2_data.get('Confirmation/Reservation UID', '')
            code_input.clear()
            code_input.send_keys(reservation_uid)
            print(f"Code set to: {reservation_uid}")
            time.sleep(1)
            
        except Exception as e:
            print(f"Error configuring code: {str(e)}")

    def configure_rate(self):
        try:
            print("\nConfiguring rate...")
            time.sleep(2)
            
            # Find and fill rate input by finding input with inputmode="numeric"
            rate_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[inputmode='numeric']")
            ))
            
            rate = self.calculate_days_and_rate()
            rate_input.clear()
            rate_input.send_keys(str(rate))
            print(f"Rate set to: ${rate}")
            time.sleep(1)
                
        except Exception as e:
            print(f"Error configuring rate: {str(e)}")

    def configure_max_parkers(self):
        try:
            print("\nConfiguring max parkers...")
            max_parkers_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='e.g. 48']")
            ))
            cars_requested = self.t2_data.get('Cars Requested', '1')
            max_parkers_input.clear()
            max_parkers_input.send_keys(cars_requested)
            print(f"Max parkers set to: {cars_requested}")
            time.sleep(1)
        except Exception as e:
            print(f"Error configuring max parkers: {str(e)}")

    def fill_first_field(self):
        try:
            print("\nFilling first field with 'First Name'...")
            field_name_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='e.g. Driver Name']")
            ))
            field_name_input.clear()
            field_name_input.send_keys("First Name")
            time.sleep(1)

            first_required_toggle = self.wait.until(EC.element_to_be_clickable(
                (By.ID, "additionalInfo.0.isRequired")
            ))
            first_required_toggle.click()
            time.sleep(1)
        except Exception as e:
            print(f"Error filling first field: {str(e)}")

    def add_last_name_field(self):
        try:
            print("\nAdding Last Name field...")
            add_field_button = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[text()='Add Field']")
            ))
            add_field_button.click()
            time.sleep(1)

            field_inputs = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='e.g. Driver Name']")
            if field_inputs:
                last_input = field_inputs[-1]
                last_input.clear()
                last_input.send_keys("Last Name")
                time.sleep(1)

                second_required_toggle = self.wait.until(EC.element_to_be_clickable(
                    (By.ID, "additionalInfo.1.isRequired")
                ))
                second_required_toggle.click()
                time.sleep(1)
        except Exception as e:
            print(f"Error adding Last Name field: {str(e)}")

    def configure_additional_info(self):
        print("\nConfiguring additional info settings...")
        time.sleep(1)
        self.fill_first_field()
        time.sleep(1)
        self.add_last_name_field()
        time.sleep(1)

    def click_continue(self):
            print("\nLocating continue button...")
            continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            print("Clicking continue button...")
            continue_button.click()     

    def configure_all_settings(self):
        try:
            print("\nConfiguring event settings...")
            
            settings = {
                "hasMaxParkers": "Set Max Number of Parkers",
                "hasAdditionalInfo": "Collect Additional Information",
                "hasCode": "Require a Code",
                "hasRate": "Add Rate"
            }

            for setting_id, setting_name in settings.items():
                print(f"\nEnabling {setting_name}...")
                self.toggle_switch(setting_id)
                time.sleep(2)
                
                if setting_id == "hasMaxParkers":
                    self.configure_max_parkers()
                elif setting_id == "hasAdditionalInfo":
                    self.configure_additional_info()
                elif setting_id == "hasCode":
                    self.configure_code()
                elif setting_id == "hasRate":
                    self.configure_rate()

            self.click_continue()
                
            return True
            
        except Exception as e:
            print(f"Error configuring settings: {str(e)}")
            return False