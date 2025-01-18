
import time
from browser import Browser
from services.parkingAuthorization import ParkingAuthorizationService
from services.eventSetting import EventSettingsService

def main():
    browser = Browser()
    
    browser.navigate("https://usc.t2flex.com/PowerPark/reservation/view.aspx?id=392468&addtoqueue=1")
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
                    time.sleep(2)  # Wait for page transition
                    
                    parking_service = ParkingAuthorizationService(browser.driver)
                    parking_service.select_location_by_similarity(t2_data)
                    parking_service.fill_dates_and_times(t2_data)
                    parking_service.click_continue()

                    # Add the new settings service step
                    settings_service = EventSettingsService(browser.driver)
                    settings_service.configure_all_settings()
        
        input("Press Enter to close the browser...")
    browser.close()

if __name__ == "__main__":
    main()