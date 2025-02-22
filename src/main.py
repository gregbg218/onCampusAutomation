from browser import Browser
from services.parkingAuthorization import ParkingAuthorizationService
import time
from services.eventSetting import EventSettingsService
from services.portalSettings import PortalSettingsService
from services.emailTemplateService import EmailTemplateService
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

def get_credentials():
    logger.info("Starting credentials retrieval process")
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

def show_reservation_dialog():
    logger.info("Opening reservation input dialog")
    dialog = tk.Tk()
    dialog.title("Reservation Input")
    dialog.geometry("300x150")
    dialog.resizable(False, False)
    
    reservation_id = tk.StringVar()
    
    def submit():
        if reservation_id.get():
            logger.info(f"Reservation ID submitted: {reservation_id.get()}")
            dialog.quit()
    
    def exit_program():
        logger.info("User initiated program exit")
        dialog.destroy()
        sys.exit()
    
    label = tk.Label(dialog, text="Enter the reservation ID:")
    label.pack(pady=10)
    
    entry = tk.Entry(dialog, textvariable=reservation_id)
    entry.pack(pady=10)
    
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    
    submit_button = tk.Button(button_frame, text="Submit", command=submit)
    submit_button.pack(side=tk.LEFT, padx=10)
    
    exit_button = tk.Button(button_frame, text="Exit", command=exit_program)
    exit_button.pack(side=tk.LEFT, padx=10)
    
    entry.focus()
    dialog.mainloop()
    
    result = reservation_id.get()
    dialog.destroy()
    return result

def main():
    logger.info("Starting parking automation process")
    browser = Browser()
    creds = get_credentials()
    
    logger.info("Initiating T2 login")
    browser.navigate("https://usc.t2flex.com/PowerPark")
    if not browser.login(creds["t2_username"], creds["t2_password"]):
        logger.error("T2 login failed")
        browser.close()
        return
    logger.info("T2 login successful")
        
    logger.info("Initiating Offstreet login")
    browser.navigate("https://dashboard.offstreet.io")
    if not browser.login_to_offstreet(creds["offstreet_email"], creds["offstreet_password"]):
        logger.error("Offstreet login failed")
        browser.close()
        return
    logger.info("Offstreet login successful")
    
    while True:
        reservation_id = show_reservation_dialog()
        if not reservation_id:
            logger.info("No reservation ID provided, closing browser")
            browser.close()
            break
            
        url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
        logger.info(f"Navigating to reservation: {url}")
        browser.navigate(url)
        
        logger.info("Extracting T2 data")
        t2_data = browser.extract_t2_data()
        billing_code = browser.get_billing_code()
        
        if t2_data and billing_code:
            logger.info(f"Successfully extracted T2 data with billing code: {billing_code}")
            browser.save_data_to_file()
            print(f"Billing Code: {billing_code}")
            
            logger.info("Starting Offstreet form fill process")
            browser.navigate("https://dashboard.offstreet.io/events/create")
            browser.fill_offstreet_form()
            time.sleep(1)
            
            logger.info("Configuring parking authorization")
            parking_service = ParkingAuthorizationService(browser.driver)
            parking_service.select_location_by_similarity(t2_data)
            parking_service.fill_dates_and_times(t2_data)
            parking_service.click_continue()
            
            logger.info("Configuring event settings")
            settings_service = EventSettingsService(browser.driver, t2_data)
            settings_service.configure_all_settings()

            logger.info("Configuring portal settings")
            formatted_data = {"t2_data": t2_data}
            portal_settings = PortalSettingsService(browser.driver, formatted_data)
            portal_settings.configure_all_portal_settings()
            
            logger.info("Processing email templates")
            email_service = EmailTemplateService(browser.driver)
            email_service.open_email_in_new_tab({"t2_data": t2_data})
            email_service.handle_denial_process({"t2_data": t2_data})
            logger.info("Completed processing reservation")
        else:
            logger.error(f"Failed to extract data for reservation {reservation_id}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("Unexpected error occurred")
        sys.exit(1)