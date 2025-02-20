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

def get_resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_credentials():
    cred_manager = CredentialManager()
    saved_creds = cred_manager.load_credentials()
    
    if saved_creds:
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
        sys.exit("Username required")
    
    if t2_username.lower() == "ajax":
        cred_manager.save_credentials(default_creds)
        return default_creds
        
    t2_password = simpledialog.askstring("T2 Credentials", "Enter T2 Password:", show="*")
    if not t2_password:
        sys.exit("Password required")
    
    offstreet_email = simpledialog.askstring("Offstreet Credentials", "Enter Offstreet Email:")
    if not offstreet_email:
        sys.exit("Email required")
        
    offstreet_password = simpledialog.askstring("Offstreet Credentials", "Enter Offstreet Password:", show="*")
    if not offstreet_password:
        sys.exit("Password required")
    
    creds = {
        "t2_username": t2_username,
        "t2_password": t2_password,
        "offstreet_email": offstreet_email,
        "offstreet_password": offstreet_password
    }
    
    cred_manager.save_credentials(creds)
    return creds

def show_exit_dialog(browser):
    dialog = tk.Tk()
    dialog.title("Exit Application")
    dialog.geometry("200x100")
    dialog.resizable(False, False)
    
    def close_application():
        dialog.destroy()
        browser.close()
        sys.exit()
        
    label = tk.Label(dialog, text="Ready to exit?")
    label.pack(pady=10)
    
    exit_button = tk.Button(dialog, text="Exit", command=close_application)
    exit_button.pack(pady=10)
    
    dialog.mainloop()

def main():
    browser = Browser()
    creds = get_credentials()
    
    root = tk.Tk()
    root.withdraw()
    
    reservation_id = simpledialog.askstring("Input", "Enter the reservation ID:")
    url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
    browser.navigate(url)
    
    if browser.login(creds["t2_username"], creds["t2_password"]):
        t2_data = browser.extract_t2_data()
        billing_code = browser.get_billing_code()
        
        if t2_data and billing_code:
            browser.save_data_to_file()
            print(f"Billing Code: {billing_code}")
            
            browser.navigate("https://dashboard.offstreet.io")
            if browser.login_to_offstreet(creds["offstreet_email"], creds["offstreet_password"]):
                if browser.navigate_to_events_create():
                    browser.fill_offstreet_form()
                    time.sleep(1)
                    
                    parking_service = ParkingAuthorizationService(browser.driver)
                    parking_service.select_location_by_similarity(t2_data)
                    parking_service.fill_dates_and_times(t2_data)
                    parking_service.click_continue()
                    
                    settings_service = EventSettingsService(browser.driver, t2_data)
                    settings_service.configure_all_settings()

                    formatted_data = {"t2_data": t2_data}
                    portal_settings = PortalSettingsService(browser.driver, formatted_data)
                    portal_settings.configure_all_portal_settings()
                    email_service = EmailTemplateService(browser.driver)
                    email_service.open_email_in_new_tab({"t2_data": t2_data})
                    email_service.handle_denial_process({"t2_data": t2_data})
        
        show_exit_dialog(browser)

if __name__ == "__main__":
    main()