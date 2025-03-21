from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import time
import tkinter as tk
from tkinter import messagebox
import sys
from tkinter import simpledialog
import logging
from datetime import datetime

logger = logging.getLogger('Browser')

class Browser:
    def __init__(self):
        logger.info("Initializing Browser")
        options = Options()
        options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        self.wait = WebDriverWait(self.driver, 10)
        self.t2_data = {}
        self.billing_code = None
        logger.info("Browser initialized successfully")
        
    def handle_isd_search_failure(self, r_number):
        try:
            logger.info(f"Handling ISD search failure for R#: {r_number}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Error", "ISDN not found use 3rd party search")
            
            search_url = "https://usc.t2flex.com/PowerPark/thirdparty/search.aspx"
            
            logger.info("Opening third party search in new tab")
            self.driver.execute_script("window.open('');")
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.get(search_url)
            
            logger.info("Entering R# in search field")
            search_field = self.wait.until(
                EC.presence_of_element_located((By.ID, "ThirdPartyNameText_T2FormTextBox_TextBox"))
            )
            search_field.clear()
            search_field.send_keys(r_number)
            
            logger.info("Clicking search button")
            search_button = self.wait.until(
                EC.element_to_be_clickable((By.ID, "SearchButton"))
            )
            search_button.click()
            
            gl_account = simpledialog.askstring("Input", "Enter GL Account Number:")
            
            if gl_account:
                self.billing_code = f"{r_number} & {gl_account}"
                logger.info(f"Billing code set manually: {self.billing_code}")
                root.destroy()
                return self.billing_code
            else:
                logger.error("No GL Account provided")
                root.destroy()
                self.driver.quit()
                sys.exit()
                
        except Exception as e:
            logger.error(f"Error in ISD search handling: {str(e)}")
            root.destroy()
            self.driver.quit()
            sys.exit()
        
    def navigate(self, url):
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def extract_t2_data(self):
        try:
            logger.info("Extracting T2 data")
            rows = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "T2FormRow")))
            for row in rows:
                try:
                    label_elem = row.find_element(By.CLASS_NAME, "T2FormLabelReadOnly") if row.find_elements(By.CLASS_NAME, "T2FormLabelReadOnly") else row.find_element(By.CLASS_NAME, "T2FormLabelRequired")
                    value_cell = row.find_element(By.CLASS_NAME, "T2FormControlCell")
                    
                    # Get the label text from the span inside the label element
                    label = label_elem.find_element(By.TAG_NAME, "span").text
                    
                    # Get the value text, handling different possible element structures
                    value = ""
                    if value_cell.find_elements(By.TAG_NAME, "span"):
                        value = value_cell.find_element(By.TAG_NAME, "span").text
                    elif value_cell.find_elements(By.TAG_NAME, "a"):
                        value = value_cell.find_element(By.TAG_NAME, "a").text
                    
                    logger.debug(f"Extracted field: {label} = {value}")
                    self.t2_data[label] = value
                except Exception as e:
                    logger.error(f"Error extracting row data: {str(e)}")
                    continue
            
            logger.info("T2 data extraction completed")
            return self.t2_data
        except Exception as e:
            logger.error(f"Error extracting T2 data: {str(e)}")
            return None

    def get_r_number(self):
        try:
            logger.info("Getting R number")
            r_number_element = self.wait.until(EC.presence_of_element_located((By.ID, "MySettings_custom_Reservation_REQ_NUMBER_T2Label_Label")))
            result = r_number_element.text.strip()
            logger.info(f"R number found: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting R number: {str(e)}")
            return None

    def click_requisition_link(self):
        try:
            logger.info("Attempting to click requisition link")
            link = self.wait.until(EC.element_to_be_clickable((By.ID, "MySettings_ResponsibleThirdPartyLink_T2FormLinkButton")))
            link.click()
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            logger.info("Requisition link clicked successfully")
            return True
        except Exception as e:
            logger.error(f"Error with requisition link: {str(e)}")
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning("Error", "ISDN not found use 3rd party search")
            root.destroy()
            self.driver.quit()
            sys.exit()

    def get_gl_account(self):
        try:
            logger.info("Getting GL Account")
            gl_account_element = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_MySettings_custom_ThirdParty_ACCT_NUMBER_T2Label_Label")))
            result = gl_account_element.text.strip()
            logger.info(f"GL Account found: {result}")
            return result
        except Exception as e:
            logger.error(f"Error getting GL Account: {str(e)}")
            return None

    def get_billing_code(self):
        logger.info("Starting billing code retrieval process")
        r_number = self.get_r_number()
        if not r_number:
            return None
                    
        if not self.click_requisition_link():
            return None
        try:
            exp_date_element = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_MySettings_custom_ThirdParty_REQ_EXP_DATE_T2Label_Label")))
            exp_date_str = exp_date_element.text.strip()
            exp_date = time.strptime(exp_date_str, "%m/%d/%Y")
            today = time.localtime()
                    
            if time.mktime(exp_date) < time.mktime(today):
                logger.error("Requisition has expired")
                return self.handle_isd_search_failure(r_number)
                
            logger.info("Requisition expiration date verified")
        except Exception as e:
            logger.error(f"Error checking expiration date: {str(e)}")
            return self.handle_isd_search_failure(r_number)
                    
        gl_account = self.get_gl_account()
        if not gl_account:
            return self.handle_isd_search_failure(r_number)
                    
        self.billing_code = f"{r_number} & {gl_account}"
        logger.info(f"Final billing code generated: {self.billing_code}")
        return self.billing_code

    def login(self, username, password):
        try:
            logger.info("Attempting T2 login")
            username_field = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_UserID_T2FormTextBox_TextBox")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "ctl00_pageContent_Password_T2FormTextBox_TextBox")))
            
            username_field.clear()
            username_field.send_keys(username)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "ctl00_pageContent_LoginButton")))
            login_button.click()
            logger.info("T2 login successful")
            return True
        except Exception as e:
            logger.error(f"T2 login failed: {str(e)}")
            return False

    def login_to_offstreet(self, email, password):
        try:
            logger.info("Attempting Offstreet login")
            email_field = self.wait.until(EC.presence_of_element_located((By.ID, "email")))
            password_field = self.wait.until(EC.presence_of_element_located((By.ID, "password")))
            
            email_field.clear()
            email_field.send_keys(email)
            password_field.clear()
            password_field.send_keys(password)
            
            login_button = self.wait.until(EC.element_to_be_clickable((By.ID, "login")))
            login_button.click()
            
            self.wait.until(EC.url_contains("dashboard.offstreet.io/dashboard"))
            logger.info("Offstreet login successful")
            return True
        except Exception as e:
            logger.error(f"Offstreet login failed: {str(e)}")
            return False

    def navigate_to_events_create(self):
        try:
            logger.info("Navigating to events create page")
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            time.sleep(3)
            
            self.driver.get("https://dashboard.offstreet.io/events/create")
            
            time.sleep(2)
            self.wait.until(EC.url_contains("/events/create"))
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "form")))
            logger.info("Successfully reached events create page")
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to events create: {str(e)}")
            return False

    def get_all_data(self):
        return {
            "t2_data": self.t2_data,
            "billing_code": self.billing_code
        }

    def save_data_to_file(self, filename="t2_data.json"):
        data = self.get_all_data()
        try:
            logger.info(f"Saving data to {filename}")
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data successfully saved to {filename}")
            logger.debug(f"Saved data: {json.dumps(data, indent=2)}")
            return True
        except Exception as e:
            logger.error(f"Failed to save data to file: {str(e)}")
            return False

    def close(self):
        logger.info("Closing browser")
        self.driver.quit()