from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import logging
import os
import sys
from selenium import webdriver

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
                time.sleep(1)
                logger.info("Branding enabled")
                self.select_transport_image()
            else:
                logger.info("Branding was already enabled")
        except Exception as e:
            logger.error(f"Error enabling branding: {str(e)}")

    def select_transport_image(self):
        try:
            logger.info("Starting to select transport.png image")
            
            add_previous_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Add Previous Files']"))
            )
            add_previous_button.click()
            logger.info("Clicked Add Previous Files button")
            time.sleep(2)
            
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search...']"))
            )
            search_input.clear()
            search_input.send_keys("transport.png")
            logger.info("Entered 'transport.png' in search box")
            time.sleep(2)
            
            first_result_checkbox = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//tr[contains(@aria-label, 'transport.png')][1]//span[@role='checkbox']"))
            )
            first_result_checkbox.click()
            logger.info("Selected the first transport.png result")
            time.sleep(1)
            
            next_button = self.wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(@class, 'bg-primary') and normalize-space(text())='Next']"))
                )
            next_button.click()
            logger.info("Clicked Next button")
            time.sleep(1)          # give the follow-up modal a moment to appear

            # 4️⃣  click **Save** in the new window
            save_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(@class, 'bg-primary') and normalize-space(text())='Save']"
                ))
            )
            save_button.click()
            logger.info("Clicked Save button")
            time.sleep(2)
            return True
            
        except Exception as e:
            logger.error(f"Error selecting transport.png image: {str(e)}")
            return False

    def add_instructions(self):
        try:
            logger.info("Adding instructions")
            time.sleep(5)

            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))

            # Use correct toggle ID: 'hasInstructions'
            instructions_toggle = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "hasInstructions"))
            )

            if "bg-primary-600" not in instructions_toggle.get_attribute("class"):
                self.driver.execute_script("arguments[0].scrollIntoView(true);", instructions_toggle)
                time.sleep(1)
                instructions_toggle.click()
                time.sleep(3)

            requested_lot = self.t2_data.get('Requested Lot', 'Structure')
            logger.debug(f"Retrieved lot name: {requested_lot}")
            instructions_text = f"Parking is now digital in the {requested_lot}. Please ensure to register your vehicle upon parking in any unmarked space."

            # Wait for at least 2 instruction fields to appear
            WebDriverWait(self.driver, 20).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, "ProseMirror")) >= 2
            )
            instruction_elements = self.driver.find_elements(By.CLASS_NAME, "ProseMirror")[:2]

            for idx, element in enumerate(instruction_elements):
                try:
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    self.driver.execute_script("arguments[0].click();", element)
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].innerHTML = '';", element)
                    self.driver.execute_script(f"arguments[0].innerHTML = `{instructions_text}`;", element)
                    logger.info(f"Instructions injected into field #{idx + 1}")
                except Exception as e:
                    logger.error(f"Failed to inject instructions into field #{idx + 1}: {str(e)}")

            time.sleep(2)

        except Exception as e:
            logger.error(f"Error adding instructions: {str(e)}")
            try:
                logger.info("Attempting alternative approach for instructions")
                time.sleep(5)
                fallback_elements = self.driver.find_elements(By.CLASS_NAME, "ProseMirror")[:2]
                for element in fallback_elements:
                    actions = webdriver.ActionChains(self.driver)
                    actions.move_to_element(element).click().send_keys(instructions_text).perform()
                logger.info("Instructions added using fallback ActionChains")
            except Exception as alt_e:
                logger.error(f"Alternative approach failed: {str(alt_e)}")


    

            
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
        time.sleep(1)
        logger.info("Starting portal settings configuration")
        self.enable_branding()
        self.add_instructions()
        logger.info("Portal settings configuration completed")
        self.click_create_event()