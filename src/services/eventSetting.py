from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class EventSettingsService:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def toggle_switch(self, switch_id):
        print(f"\nToggling {switch_id}...")
        switch = self.wait.until(EC.element_to_be_clickable((By.ID, switch_id)))
        switch.click()
        time.sleep(1)

    def fill_first_field(self):
        try:
            print("\nFilling first field with 'First Name'...")
            
            field_name_input = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "input[placeholder='e.g. Driver Name']")
            ))
            field_name_input.clear()
            field_name_input.send_keys("First Name")
            time.sleep(1)

            # Toggle required switch for first field
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

                # Toggle required switch for second field
                second_required_toggle = self.wait.until(EC.element_to_be_clickable(
                    (By.ID, "additionalInfo.1.isRequired")
                ))
                second_required_toggle.click()
                time.sleep(1)

        except Exception as e:
            print(f"Error adding Last Name field: {str(e)}")

    def configure_additional_info(self):
        print("\nConfiguring additional info settings...")
        self.fill_first_field()
        time.sleep(1)
        self.add_last_name_field()
        time.sleep(1)

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
                time.sleep(1)
                
                if setting_id == "hasAdditionalInfo":
                    time.sleep(1)
                    self.configure_additional_info()
                
            return True
            
        except Exception as e:
            print(f"Error configuring settings: {str(e)}")
            return False