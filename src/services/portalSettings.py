from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class PortalSettingsService:
    def __init__(self, driver, t2_data):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.t2_data = t2_data.get('t2_data', {})

    def enable_branding(self):
        try:
            print("\nEnabling branding...")
            branding_toggle = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hasBranding"))
            )
            if not "bg-primary-600" in branding_toggle.get_attribute("class"):
                branding_toggle.click()
                print("Branding enabled")
                self.upload_image()
            else:
                print("Branding was already enabled")
        except Exception as e:
            print(f"Error enabling branding: {str(e)}")

    def upload_image(self):
        try:
            print("\nUploading transport image...")
            
            # Wait for and click the upload button
            upload_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Upload')]"))
            )
            upload_button.click()
            time.sleep(1)  # Wait for upload dialog
            
            # Get the absolute path to the image using resource helper
            import os
            import sys

            def get_resource_path(relative_path):
                try:
                    # PyInstaller creates a temp folder and stores path in _MEIPASS
                    base_path = sys._MEIPASS
                except Exception:
                    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                
                return os.path.join(base_path, relative_path)
                
            image_path = get_resource_path("assets/transport.png")
            print(f"Using image path: {image_path}")
            
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(image_path)
            time.sleep(7)
            
            print("Waiting for Save button...")
            save_button = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[text()='Save']"))
            )
            print("Clicking Save button...")
            save_button.click()
            
            # Wait for upload modal to close
            time.sleep(7)
            print("Image upload and save completed")
            return True
            
        except Exception as e:
            print(f"Error uploading image: {str(e)}")
            return False

    def add_instructions(self):
        try:
            print("\nAdding instructions...")
            # Wait longer for page to stabilize after upload
            time.sleep(5)
            
            # First ensure we're back on the main form
            self.wait.until(
                EC.presence_of_element_located((By.TAG_NAME, "form"))
            )
            
            # Try to find the instructions toggle with a longer wait
            instructions_toggle = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "hasCustomMessage"))
            )
            
            # Check if it's already enabled by looking at the class
            if not "bg-primary-600" in instructions_toggle.get_attribute("class"):
                # Scroll to make sure it's in view
                self.driver.execute_script("arguments[0].scrollIntoView(true);", instructions_toggle)
                time.sleep(1)
                instructions_toggle.click()
                time.sleep(3)  # Wait longer after clicking
            
            # Get lot info
            requested_lot = self.t2_data.get('Requested Lot')
            if not requested_lot:
                requested_lot = "Structure"
                print("Warning: Could not find Requested Lot in t2_data, using default value")
            
            print(f"Retrieved lot name from t2_data: {requested_lot}")
            instructions_text = f"Parking is now digital in the {requested_lot}. Please ensure to register your vehicle upon parking in any unmarked space."
            print(f"Generated instructions: {instructions_text}")
            
            # Try to find the editor with a longer wait
            instructions_element = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ProseMirror"))
            )
            
            # Ensure the element is interactable
            self.driver.execute_script("arguments[0].scrollIntoView(true);", instructions_element)
            time.sleep(2)
            
            # Try clicking into the element first
            self.driver.execute_script("arguments[0].click();", instructions_element)
            time.sleep(1)
            
            # Clear and set text using JavaScript
            self.driver.execute_script("arguments[0].innerHTML = '';", instructions_element)
            self.driver.execute_script(f"arguments[0].innerHTML = '{instructions_text}';", instructions_element)
            
            print(f"Instructions added with lot: {requested_lot}")
            time.sleep(2)  # Wait before moving on
            
        except Exception as e:
            print(f"Error adding instructions: {str(e)}")
            # Try alternative approach if first one fails
            try:
                print("Attempting alternative approach for instructions...")
                time.sleep(5)
                instructions_element = self.driver.find_element(By.CLASS_NAME, "ProseMirror")
                actions = webdriver.ActionChains(self.driver)
                actions.move_to_element(instructions_element).click().perform()
                actions.send_keys(instructions_text).perform()
                print("Instructions added using alternative approach")
            except Exception as alt_e:
                print(f"Alternative approach also failed: {str(alt_e)}")

    def enable_directions(self):
        try:
            print("\nEnabling directions...")
            directions_toggle = self.wait.until(
                EC.element_to_be_clickable((By.ID, "hasDirections"))
            )
            if not "bg-primary-600" in directions_toggle.get_attribute("class"):
                directions_toggle.click()
                print("Directions enabled")
            else:
                print("Directions were already enabled")
        except Exception as e:
            print(f"Error enabling directions: {str(e)}")

    def select_event_link_type(self):
        try:
            print("\nSelecting event link type...")
            event_link_radio = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='linkType'][value='EVENT']"))
            )
            if not event_link_radio.is_selected():
                event_link_radio.click()
                print("Event link type selected")
            else:
                print("Event link type was already selected")
        except Exception as e:
            print(f"Error selecting event link type: {str(e)}")
            
    def click_create_event(self):
        try:
            print("\nLocating Create Event button...")
            time.sleep(2)  # Wait for page to be stable
            
            create_button = self.wait.until(
                EC.presence_of_element_located((By.XPATH, "//button[text()='Create Event']"))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", create_button)
            time.sleep(1)
            
            print("Clicking Create Event button...")
            create_button.click()
            time.sleep(3)  # Wait for form submission
            print("Event created successfully")
            return True
        except Exception as e:
            print(f"Error clicking Create Event button: {str(e)}")
            return False

    def configure_all_portal_settings(self):
        """Configure all portal settings in sequence"""
        print("\nConfiguring portal settings...")
        self.select_event_link_type()
        self.enable_branding()
        self.add_instructions()
        self.enable_directions()
        print("Portal settings configuration completed")
        self.click_create_event()