from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging

logger = logging.getLogger('FirstPageService')

class FirstPageService:
    def __init__(self, driver, t2_data, billing_code):
        logger.info("Initializing FirstPageService")
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.t2_data = t2_data
        self.billing_code = billing_code

    def format_phone(self, phone):
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone

    def fill_first_page(self):
        try:
            time.sleep(2)
            logger.info("Starting first page form fill process")
            
            form_mapping = {
                "event": ("Event Name", "#event"),
                "host": ("Contact Department", "#host"),
                "firstName": ("Contact First Name", "#contact\\.firstName"),
                "lastName": ("Contact Last Name", "#contact\\.lastName"),
                "email": ("Contact E-mail", "#contact\\.email"),
                "phoneNumber": ("Contact Phone", "#contact\\.phoneNumber"),
                "billingCode": (None, "#billingCode")
            }
            
            for field, (json_key, selector) in form_mapping.items():
                try:
                    logger.debug(f"Filling field: {field}")
                    element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if json_key:
                        value = self.t2_data.get(json_key, "")
                        if field == "phoneNumber" and value:
                            value = self.format_phone(value)
                    else:
                        value = self.billing_code
                        
                    if value:
                        element.clear()
                        element.send_keys(value)
                        time.sleep(0.5)
                        logger.debug(f"Field {field} filled with value: {value}")
                    else:
                        logger.warning(f"No value found for field: {field}")
                        
                except Exception as field_error:
                    logger.error(f"Error filling field {field}: {str(field_error)}")
            
            self.click_continue()
            logger.info("First page form submitted successfully")
            
            return True
        except Exception as e:
            logger.error(f"Error in fill_first_page: {str(e)}")
            return False
            
    def click_continue(self):
        logger.info("Proceeding to next step")
        continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        continue_button.click()
        logger.debug("Continue button clicked")