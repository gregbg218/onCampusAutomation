from browser import Browser
from services.secondPageService import SecondPageService
from services.firstPageService import FirstPageService
from services.eventSetting import EventSettingsService
from services.portalSettings import PortalSettingsService
from services.emailTemplateService import EmailTemplateService
import time
import os
import sys
import tkinter as tk
from tkinter import simpledialog, messagebox
from services.credential_manager import CredentialManager
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(name)s | %(message)s',
    handlers=[
        logging.FileHandler(f'parking_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('ParkingAutomation')

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_credentials(cred_manager=None):
    logger.info("Starting credentials retrieval process")
    if cred_manager is None:
        cred_manager = CredentialManager()
        
    saved_creds = cred_manager.load_credentials()
    
    if saved_creds:
        logger.info("Retrieved saved credentials")
        return saved_creds
    
    root = tk.Tk()
    root.withdraw()
    
    default_creds = {
        "t2_username": "GregoryG",
        "t2_password": "Tommy123",
        "offstreet_email": "ggeevarg@usc.edu",
        "offstreet_password": "baYernForever$"
    }
    
    t2_username = simpledialog.askstring("T2 Credentials", "Enter T2 Username:")
    if not t2_username:
        logger.error("T2 username input cancelled")
        sys.exit("Username required")
    
    if t2_username.lower() == "plato":
        logger.info("Using default credentials")
        cred_manager.save_credentials(default_creds)
        return default_creds
        
    t2_password = simpledialog.askstring("T2 Credentials", "Enter T2 Password:", show="*")
    if not t2_password:
        logger.error("T2 password input cancelled")
        sys.exit("Password required")
    
    offstreet_email = simpledialog.askstring("Offstreet Credentials", "Enter Offstreet Email:")
    if not offstreet_email:
        logger.error("Offstreet email input cancelled")
        sys.exit("Email required")
        
    offstreet_password = simpledialog.askstring("Offstreet Credentials", "Enter Offstreet Password:", show="*")
    if not offstreet_password:
        logger.error("Offstreet password input cancelled")
        sys.exit("Password required")
    
    creds = {
        "t2_username": t2_username,
        "t2_password": t2_password,
        "offstreet_email": offstreet_email,
        "offstreet_password": offstreet_password
    }
    
    logger.info("New credentials collected and being saved")
    cred_manager.save_credentials(creds)
    return creds

def show_reservation_dialog(cred_manager=None):
    logger.info("Opening reservation input dialog")
    dialog = tk.Tk()
    dialog.title("Reservation Input")
    dialog.geometry("300x190")
    dialog.resizable(False, False)
    
    logger.info("Dialog window created")
    
    reservation_id = tk.StringVar()
    result = {"action": "submit", "id": ""}
    
    def submit():
        try:
            logger.info("Submit button clicked")
            current_id = entry.get()
            logger.info(f"Current reservation ID in field: '{current_id}'")
            
            if current_id:
                logger.info(f"Reservation ID submitted: {current_id}")
                result["id"] = current_id
                result["action"] = "submit"
                logger.info(f"Dialog result set to: {result}")
                logger.info("About to destroy dialog")
                dialog.quit()
                logger.info("Dialog mainloop ended")
                dialog.destroy()
                logger.info("Dialog destroyed after submit")
            else:
                logger.warning("Submit clicked but reservation ID is empty")
        except Exception as e:
            logger.exception(f"Error in submit function: {str(e)}")
    
    def exit_program():
        try:
            logger.info("Exit button clicked")
            result["action"] = "exit"
            dialog.quit()
            dialog.destroy()
            logger.info("Dialog destroyed after exit")
        except Exception as e:
            logger.exception(f"Error in exit_program function: {str(e)}")
    
    def logout():
        try:
            logger.info("Logout button clicked")
            if cred_manager:
                logger.info("Clearing saved credentials")
                cred_manager.clear_credentials()
            result["action"] = "logout"
            dialog.quit()
            dialog.destroy()
            logger.info("Dialog destroyed after logout")
        except Exception as e:
            logger.exception(f"Error in logout function: {str(e)}")
    
    logger.info("Creating dialog UI components")
    
    label = tk.Label(dialog, text="Enter the reservation ID:")
    label.pack(pady=10)
    
    entry = tk.Entry(dialog, textvariable=reservation_id)
    entry.pack(pady=10)
    
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    submit_button = tk.Button(button_frame, text="Submit", command=submit)
    submit_button.pack(side=tk.LEFT, padx=5)
    
    logout_button = tk.Button(button_frame, text="Logout", command=logout)
    logout_button.pack(side=tk.LEFT, padx=5)
    
    exit_button = tk.Button(button_frame, text="Exit", command=exit_program)
    exit_button.pack(side=tk.LEFT, padx=5)
    
    def on_enter_press(event):
        logger.info("Enter key pressed")
        submit()
    
    entry.bind('<Return>', on_enter_press)
    
    entry.focus()
    logger.info("Dialog UI created, starting mainloop")
    
    try:
        dialog.mainloop()
        logger.info("Dialog mainloop ended normally")
    except Exception as e:
        logger.exception(f"Error in dialog mainloop: {str(e)}")
    
    logger.info(f"Dialog closed, returning result: {result}")
    return result

def main():
    logger.info("Starting parking automation process")
    cred_manager = CredentialManager()
    
    while True:
        browser = Browser()
        creds = get_credentials(cred_manager)
        
        logger.info("Initiating T2 login")
        browser.navigate("https://usc.t2flex.com/PowerPark")
        if not browser.login(creds["t2_username"], creds["t2_password"]):
            logger.error("T2 login failed")
            browser.close()
            continue
        logger.info("T2 login successful")
            
        logger.info("Initiating Offstreet login")
        browser.navigate("https://dashboard.offstreet.io")
        if not browser.login_to_offstreet(creds["offstreet_email"], creds["offstreet_password"]):
            logger.error("Offstreet login failed")
            browser.close()
            continue
        logger.info("Offstreet login successful")
        
        while True:
            reservation_result = show_reservation_dialog(cred_manager)
            logger.info(f"Received reservation result from dialog: {reservation_result}")
            
            if reservation_result["action"] == "exit":
                logger.info("Exit requested, closing browser")
                browser.close()
                return
                
            if reservation_result["action"] == "logout":
                logger.info("Logout requested, restarting login flow")
                browser.close()
                break
                
            reservation_id = reservation_result["id"]
            if not reservation_id:
                logger.info("No reservation ID provided, closing browser")
                browser.close()
                return
            
            logger.info(f"Processing reservation ID: {reservation_id}")
            
            url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
            logger.info(f"About to navigate to T2 URL: {url}")
            
            try:
                browser.navigate(url)
                logger.info("Navigation to T2 reservation page complete")
                
                logger.info("Starting T2 data extraction")
                t2_data = browser.extract_t2_data()
                logger.info(f"T2 data extraction complete: {'Success' if t2_data else 'Failed'}")
                
                logger.info("Starting billing code retrieval")
                billing_code = browser.get_billing_code()
                logger.info(f"Billing code retrieval complete: {'Success' if billing_code else 'Failed'}")
                
                if t2_data and billing_code:
                    logger.info(f"Successfully extracted T2 data with billing code: {billing_code}")
                    logger.info("Saving data to file")
                    browser.save_data_to_file()
                    print(f"Billing Code: {billing_code}")
                    
                    logger.info("About to navigate to Offstreet events create page")
                    browser.navigate("https://dashboard.offstreet.io/events/create")
                    logger.info("Navigation to Offstreet events create page complete")
                    
                    logger.info("Starting first page form fill process")
                    first_page_service = FirstPageService(browser.driver, t2_data, billing_code)
                    first_page_result = first_page_service.fill_first_page()
                    logger.info(f"First page form result: {'Success' if first_page_result else 'Failed'}")
                    time.sleep(1)
                    
                    logger.info("Starting second page processing")
                    try:
                        second_page_service = SecondPageService(browser.driver)
                        second_page_result = second_page_service.process_second_page(t2_data)
                        logger.info(f"Second page processing result: {'Success' if second_page_result else 'Failed'}")
                    except Exception as e:
                        logger.error(f"Error in second page processing: {str(e)}")
                    
                    logger.info("Configuring event settings")
                    try:
                        settings_service = EventSettingsService(browser.driver, t2_data)
                        settings_service.configure_all_settings()
                        logger.info("Event settings configuration complete")
                    except Exception as e:
                        logger.error(f"Error in event settings configuration: {str(e)}")

                    logger.info("Configuring portal settings")
                    try:
                        formatted_data = {"t2_data": t2_data}
                        portal_settings = PortalSettingsService(browser.driver, formatted_data)
                        portal_settings.configure_all_portal_settings()
                        logger.info("Portal settings configuration complete")
                    except Exception as e:
                        logger.error(f"Error in portal settings configuration: {str(e)}")
                    
                    logger.info("Processing email templates")
                    try:
                        email_service = EmailTemplateService(browser.driver)
                        email_service.open_email_in_new_tab({"t2_data": t2_data})
                        email_service.handle_denial_process({"t2_data": t2_data})
                        logger.info("Email template processing complete")
                    except Exception as e:
                        logger.error(f"Error in email template processing: {str(e)}")
                    
                    logger.info("Completed processing reservation")
                else:
                    logger.error(f"Failed to extract data for reservation {reservation_id}")
                    if not t2_data:
                        logger.error("T2 data extraction failed")
                    if not billing_code:
                        logger.error("Billing code retrieval failed")
            except Exception as e:
                logger.exception(f"Error processing reservation {reservation_id}: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)