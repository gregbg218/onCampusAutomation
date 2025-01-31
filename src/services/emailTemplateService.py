import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

class EmailTemplateService:
    def __init__(self, driver):
        self.driver = driver

    def format_parking_structure(self, name):
        if 'Biggy' in name:
            return 'Biggy Structure'
        elif 'San Pablo' in name:
            return 'San Pablo Parking Structure'
        elif 'Figueroa' in name:
            return 'Figueroa Street Structure'
        return name

    def get_event_link(self):
        try:
            event_link = self.driver.find_element('css selector', 'a[href^="https://www.offstreet.io/events/"]')
            return event_link.get_attribute('href')
        except:
            return '[EVENT_LINK_NOT_FOUND]'

    def generate_email_content(self, t2_data):
        event_data = t2_data['t2_data']
        formatted_date = event_data['Begin Date']
        event_name = event_data['Event Name']
        contact_name = event_data['Contact First Name']
        email = event_data['Contact E-mail']
        parking_structure = self.format_parking_structure(event_data['Requested Lot'])
        passcode = event_data['Confirmation/Reservation UID']
        event_link = self.get_event_link()
        
        html_content = f'''
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                ul {{ list-style-type: disc; padding-left: 40px; }}
                .underline {{ text-decoration: underline; }}
                .bold {{ font-weight: bold; }}
            </style>
        </head>
        <body>
            <p>OFST- RE: {event_name}</p>
            <p>Transportation Parking Reservations</p>
            <p>{email}</p>
            <p><strong>Reference: {event_name} {formatted_date}</strong></p><br>
            <p>Hello <span style="color: black;">{contact_name}</span>,</p><br>
            <p>Please note that RSVP {passcode} is no longer eligible for a manual/paper pass and has been converted to our Digital Platform Offstreet.</p><br>
            <p>Below you will find important information regarding our new digital parking pass system which will allow your guests to easily and conveniently park without needing to stop at a Gate Entrance Booth. Simply send your guests the below Link with instructions and they will take it from there!</p><br>
            <p class="underline bold">GUEST INSTRUCTIONS:</p>
            <p><strong>Here's how to obtain a ONE-DAY Digital Parking Pass at USC:</strong></p>
            <ul>
                <li><strong>Registration Link/QR Code:</strong> To register for Parking no earlier than 1-2 days prior to your event, please click on this link: <a href="{event_link}" style="color: blue;">{event_link}</a></li>
                <li><strong>Vehicle License Plate:</strong> Once in our system, please enter license plate information</li>
                <li><strong>Enter Pass Code:</strong> <span style="font-weight: bold; color: #386600;">{passcode}</span></li>
                <li><strong>Parking Confirmation Receipt:</strong> After completing your registration, enter your e-mail for a receipt copy (optional). Your License plate is your permit. No paper pass required to be displayed. You are now all set to park!</li>
                <li><strong>Additional Notes:</strong> Your assigned parking structure is: <span style="font-weight: bold;">{parking_structure}</span> (Refer to Welcome Registration page for Parking Map)</li>
            </ul><br>
            <p>Please make sure you do NOT park in any reserved/signage space as these are for reserved permit holders only! Thank you!</p>
        </body>
        </html>
        '''
        return html_content

    def open_email_in_new_tab(self, t2_data):
        try:
            # Open email in new tab
            html_content = self.generate_email_content(t2_data)
            script = f'''
                var newWindow = window.open();
                newWindow.document.write(`{html_content}`);
                newWindow.document.close();
            '''
            self.driver.execute_script(script)
            
            # Open T2 page in new tab
            reservation_id = t2_data['t2_data']['Confirmation/Reservation UID']
            t2_url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
            script = f'''window.open("{t2_url}", "_blank");'''
            self.driver.execute_script(script)
        except Exception as e:
            print(f"Error opening tabs: {str(e)}")

    def handle_denial_process(self, t2_data):
        try:
            # Set up wait
            wait = WebDriverWait(self.driver, 10)
            
            # Switch to the correct window by finding the tab with the reservation view URL
            for window_handle in self.driver.window_handles:
                self.driver.switch_to.window(window_handle)
                if 'PowerPark/reservation/view.aspx' in self.driver.current_url:
                    break
            
            # Click the deny link by matching exact sidebar structure
            deny_selector = '.PageSideBarItemEnabled a[href*="modifyType=Deny"]'
            deny_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, deny_selector))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", deny_link)
            deny_link.click()

            # Wait for 1 second for page load
            time.sleep(1)

            # Select Note Type dropdown by exact ID
            note_type_dropdown = wait.until(
                EC.presence_of_element_located((
                    By.ID,
                    'insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList'
                ))
            )
            
            # Ensure dropdown is visible and clickable
            self.driver.execute_script("arguments[0].scrollIntoView(true);", note_type_dropdown)
            wait.until(EC.element_to_be_clickable((
                By.ID,
                'insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList'
            )))
            
            # Select "Note for Dept Reservations" option (value "2005")
            select = Select(note_type_dropdown)
            select.select_by_value('2005')
            
            # Wait for potential AJAX updates
            time.sleep(0.5)

            # Fill the form with event reference
            event_name = t2_data['t2_data']['Event Name']
            note_text = f'OFST- RE: {event_name}'
            
            # Find and fill the textarea using exact ID
            textarea = wait.until(
                EC.presence_of_element_located((
                    By.ID,
                    'insertEditNoteControl1_WizardStep1_S1NoteText_T2FormTextBox_TextBox'
                ))
            )
            
            # Ensure textarea is visible
            self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            textarea.clear()
            textarea.send_keys(note_text)
            
            # Find and click Save button using exact ID
            save_selector = '#insertEditNoteControl1_SaveButton'
            save_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, save_selector))
            )
            
            # Click save button
            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            save_button.click()
            
            # Wait for save operation to complete
            time.sleep(1)
            
            # Switch back to original tab
            self.driver.switch_to.window(self.driver.window_handles[0])
            
        except Exception as e:
            print(f"Error in denial process: {str(e)}")
            # Try to switch back to original tab even if error occurs
            try:
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                pass
            raise e