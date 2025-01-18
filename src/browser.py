from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time

class Browser:
    def __init__(self):
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.t2_data = {}
        self.billing_code = None

    def format_phone(self,phone):
        digits = ''.join(filter(str.isdigit, phone))
        if len(digits) == 10:
            return f"+1 ({digits[:3]}) {digits[3:6]}-{digits[6:]}"
        return phone


    def fill_offstreet_form(self):
        try:
            time.sleep(2)
            print("\nStarting form fill process...")
            
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
                    print(f"\nFilling {field}:")
                    element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    element = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    
                    if json_key:
                        value = self.t2_data.get(json_key, "")
                        print(f"  - Found value from JSON: {value}")
                        if field == "phoneNumber" and value:
                            print(f"Raw phone number: {value}")
                            value = self.format_phone(value)
                    else:
                        value = self.billing_code
                        print(f"  - Using billing code: {value}")
                        
                    if value:
                        print(f"  - Clearing field")
                        element.clear()
                        print(f"  - Setting value: {value}")
                        element.send_keys(value)
                        time.sleep(0.5)
                    else:
                        print(f"  - No value found for {field}")
                        
                except Exception as field_error:
                    print(f"  - Error filling field {field}: {str(field_error)}")
            
            time.sleep(1)
            print("\nLocating continue button...")
            continue_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
            print("Clicking continue button...")
            continue_button.click()
            
            return True
        except Exception as e:
            print(f"\nError in fill_offstreet_form: {str(e)}")
            return False
        


    def navigate(self, url):
        print(f"\nNavigating to: {url}")
        self.driver.get(url)

    def extract_t2_data(self):
        try:
            print("\nExtracting T2 data...")
            rows = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "T2FormRow")))
            for row in rows:
                label_elem = row.find_element(By.CLASS_NAME, "T2FormLabelReadOnly") if row.find_elements(By.CLASS_NAME, "T2FormLabelReadOnly") else row.find_element(By.CLASS_NAME, "T2FormLabelRequired")
                value_cell = row.find_element(By.CLASS_NAME, "T2FormControlCell")
                
                label = label_elem.find_element(By.TAG_NAME, "span").text
                value = value_cell.find_element(By.TAG_NAME, "span").text if value_cell.find_elements(By.TAG_NAME, "span") else value_cell.find_element(By.TAG_NAME, "a").text
                
                print(f"  - Found field: {label} = {value}")
                self.t2_data[label] = value
            
            return self.t2_data
        except Exception as e:
            print(f"Error extracting T2 data: {str(e)}")
            return None

    def get_r_number(self):
        try:
            print("\nGetting R number...")
            r_number_element = self.wait.until(EC.presence_of_element_located((By.ID, "MySettings_custom_Reservation_REQ_NUMBER_T2Label_Label")))
            result = r_number_element.text.strip()
            print(f"  - Found R number: {result}")
            return result
        except Exception as e:
            print(f"Error getting R number: {str(e)}")
            return None

    def click_requisition_link(self):
        try:
            print("\nLocating requisition link...")
            link = self.wait.until(EC.element_to_be_clickable((By.ID, "MySettings_ResponsibleThirdPartyLink_T2FormLinkButton")))
            print(f"Found link with text: {link.text}")
            link.click()
            
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            return True
        except Exception as e:
            print(f"Error with requisition link: {str(e)}")
            return False

    def get_gl_account(self):
        try:
            print("\nGetting GL Account...")
            gl_account_element = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_MySettings_custom_ThirdParty_ACCT_NUMBER_T2Label_Label")))
            result = gl_account_element.text.strip()
            print(f"  - Found GL Account: {result}")
            return result
        except Exception as e:
            print(f"Error getting GL Account: {str(e)}")
            return None

    def get_billing_code(self):
        print("\nGetting billing code...")
        r_number = self.get_r_number()
        if not r_number:
            return None
            
        if not self.click_requisition_link():
            return None
            
        gl_account = self.get_gl_account()
        if not gl_account:
            return None
            
        self.billing_code = f"{r_number} & {gl_account}"
        print(f"  - Final billing code: {self.billing_code}")
        return self.billing_code

    def login(self, username, password):
        try:
            print("\nLogging into T2...")
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_UserID_T2FormTextBox_TextBox")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_Password_T2FormTextBox_TextBox")))
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "ctl00_pageContent_LoginButton")))
            login_button.click()
            print("Login successful")
            return True
        except Exception as e:
            print(f"Error during login: {str(e)}")
            return False

    def login_to_offstreet(self, email, password):
        try:
            print("\nLogging into Offstreet...")
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            
            email_field.clear()
            email_field.send_keys(email)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login")))
            login_button.click()
            
            print("Waiting for dashboard...")
            self.wait.until(EC.url_contains("dashboard.offstreet.io/dashboard"))
            print("Login successful")
            return True
        except Exception as e:
            print(f"Error during Offstreet login: {str(e)}")
            return False

    def navigate_to_events_create(self):
        try:
            print("\nNavigating to events create page...")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            self.driver.get("https://dashboard.offstreet.io/events/create")
            
            time.sleep(2)
            self.wait.until(EC.url_contains("/events/create"))
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            print("Successfully reached events create page")
            
            return True
        except Exception as e:
            print(f"Error navigating to events create: {str(e)}")
            return False

    def get_all_data(self):
        return {
            "t2_data": self.t2_data,
            "billing_code": self.billing_code
        }

    def save_data_to_file(self, filename="t2_data.json"):
        data = self.get_all_data()
        try:
            print(f"\nSaving data to {filename}...")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data successfully saved to {filename}")
            print(f"Saved data: {json.dumps(data, indent=2)}")
            return True
        except Exception as e:
            print(f"Error saving data to file: {str(e)}")
            return False

    def close(self):
        print("\nClosing browser...")
        self.driver.quit()