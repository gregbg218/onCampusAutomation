from browser import Browser

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
                    
    input("Press Enter to close the browser...")
    browser.close()

if __name__ == "__main__":
    main()