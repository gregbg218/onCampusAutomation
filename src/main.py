from browser import Browser
from services.parkingAuthorization import ParkingAuthorizationService
import time

from services.eventSetting import EventSettingsService
from services.portalSettings import PortalSettingsService
from services.emailTemplateService import EmailTemplateService

import os
import sys

import time

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

import tkinter as tk
from tkinter import simpledialog

def main():
    browser = Browser()
    
    root = tk.Tk()
    root.withdraw()
    
    reservation_id = simpledialog.askstring("Input", "Enter the reservation ID:")
    url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
    browser.navigate(url)
    if browser.login("GregoryG", "Tommy123"):
        t2_data = browser.extract_t2_data()
        billing_code = browser.get_billing_code()
        
        if t2_data and billing_code:
            browser.save_data_to_file()
            print(f"Billing Code: {billing_code}")
            
            browser.navigate("https://dashboard.offstreet.io")
            if browser.login_to_offstreet("ggeevarg@usc.edu", "baYernForever$"):
                if browser.navigate_to_events_create():
                    browser.fill_offstreet_form()
                    time.sleep(1)  # Wait for page transition
                    
                    parking_service = ParkingAuthorizationService(browser.driver)
                    parking_service.select_location_by_similarity(t2_data)
                    parking_service.fill_dates_and_times(t2_data)
                    parking_service.click_continue()
                    
                    # Pass t2_data to EventSettingsService
                    settings_service = EventSettingsService(browser.driver, t2_data)
                    settings_service.configure_all_settings()


                      # Add Portal Settings configuration

                    formatted_data = {"t2_data": t2_data}
                    portal_settings = PortalSettingsService(browser.driver, formatted_data)
                    portal_settings.configure_all_portal_settings()
                    email_service = EmailTemplateService(browser.driver)
                    email_service.open_email_in_new_tab({"t2_data": t2_data})
        
        input("Press Enter to close the browser...")
    browser.close()

if __name__ == "__main__":
    main()