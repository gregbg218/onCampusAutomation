from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
import sys

logger = logging.getLogger('PortalSettings')

class PortalSettingsService:
    def __init__(self, driver, t2_data):
        logger.info("Initializing PortalSettingsService")
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.t2_data = t2_data.get('t2_data', {})

    def enable_branding(self):
        try:
            logger.info("Enabling branding")
            branding_toggle = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hasBranding"))
            )
            if not "bg-primary-600" in branding_toggle.get_attribute("class"):
                branding_toggle.click()
                logger.info("Branding enabled")
                self.upload_image()
            else:
                logger.info("Branding was already enabled")
        except Exception as e:
            logger.error(f"Error enabling branding: {str(e)}")

    def upload_image(self):
        try:
            logger.info("Starting transport image upload")
            
            upload_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Upload')]"))
            )
            upload_button.click()
            time.sleep(1)
            
            def get_resource_path(relative_path):
                try:
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                return os.path.join(base_path, relative_path)
                
            image_path = get_resource_path("assets/transport.png")
            logger.debug(f"Using image path: {image_path}")
            
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(image_path)
            time.sleep(7)
            
            logger.debug("Locating Save button")
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
            )
            save_button.click()
            
            time.sleep(7)
            logger.info("Image upload completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            return False

    def add_instructions(self):
        try:
            logger.info("Adding instructions")
            time.sleep(5)
            
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            instructions_toggle = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "hasCustomMessage"))
            )
            
            if not "bg-primary-600" in instructions_toggle.get_attribute("class"):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", instructions_toggle)
                time.sleep(1)
                instructions_toggle.click()
                time.sleep(3)
            
            requested_lot = self.t2_data.get('Requested Lot')
            if not requested_lot:
                requested_lot = "Structure"
                logger.warning("Could not find Requested Lot in t2_data, using default value")
            
            logger.debug(f"Retrieved lot name: {requested_lot}")
            instructions_text = f"Parking is now digital in the {requested_lot}. Please ensure to register your vehicle upon parking in any unmarked space."
            
            instructions_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ProseMirror"))
            )
            
            self.driver.execute_script("arguments[0].scrollIntoView(true);", instructions_element)
            time.sleep(2)
            
            self.driver.execute_script("arguments[0].click();", instructions_element)
            time.sleep(1)
            
            self.driver.execute_script("arguments[0].innerHTML = '';", instructions_element)
            self.driver.execute_script(f"arguments[0].innerHTML = '{instructions_text}';", instructions_element)
            
            logger.info(f"Instructions added successfully for lot: {requested_lot}")
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Error adding instructions: {str(e)}")
            try:
                logger.info("Attempting alternative approach for instructions")
                time.sleep(5)
                instructions_element = self.driver.find_element(By.CLASS_NAME, "ProseMirror")
                actions = webdriver.ActionChains(self.driver)
                actions.move_to_element(instructions_element).click().perform()
                actions.send_keys(instructions_text).perform()
                logger.info("Instructions added using alternative approach")
            except Exception as alt_e:
                logger.error(f"Alternative approach failed: {str(alt_e)}")

    def enable_directions(self):
        try:
            logger.info("Enabling directions")
            directions_toggle = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hasDirections"))
            )
            if not "bg-primary-600" in directions_toggle.get_attribute("class"):
                directions_toggle.click()
                logger.info("Directions enabled")
            else:
                logger.info("Directions were already enabled")
        except Exception as e:
            logger.error(f"Error enabling directions: {str(e)}")

    def select_event_link_type(self):
        try:
            logger.info("Selecting event link type")
            event_link_radio = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='linkType'][value='EVENT']"))
            )
            if not event_link_radio.is_selected():
                event_link_radio.click()
                logger.info("Event link type selected")
            else:
                logger.info("Event link type was already selected")
        except Exception as e:
            logger.error(f"Error selecting event link type: {str(e)}")
            
    def click_create_event(self):
        try:
            logger.info("Initiating event creation")
            time.sleep(2)
            
            create_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Create Event']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
            time.sleep(1)
            
            create_button.click()
            time.sleep(3)
            logger.info("Event created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating event: {str(e)}")
            return False

    def configure_all_portal_settings(self):
        logger.info("Starting portal settings configuration")
        self.select_event_link_type()
        self.enable_branding()
        self.add_instructions()
        self.enable_directions()
        logger.info("Portal settings configuration completed")
        self.click_create_event()