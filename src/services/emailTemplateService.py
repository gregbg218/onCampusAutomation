import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import logging
import tkinter as tk

logger = logging.getLogger('EmailTemplate')

class EmailTemplateService:
    def __init__(self, driver):
        logger.info("Initializing EmailTemplateService")
        self.driver = driver

    def format_parking_structure(self, name):
        logger.debug(f"Formatting parking structure name: {name}")
        if 'Biggy' in name:
            return 'Biggy Structure'
        elif 'San Pablo' in name:
            return 'San Pablo Parking Structure'
        elif 'Figueroa' in name:
            return 'Figueroa Street Structure'
        return name

    def get_event_link(self):
        try:
            logger.info("Retrieving event link")
            event_link = self.driver.find_element('css selector', 'a[href^="https://www.offstreet.io/events/"]')
            link = event_link.get_attribute('href')
            logger.info(f"Event link found: {link}")
            return link
        except:
            logger.warning("Event link not found, using placeholder")
            return '[EVENT_LINK_NOT_FOUND]'

    def generate_email_content(self, t2_data):
        logger.info("Generating email content")
        event_data = t2_data['t2_data']
        formatted_date = event_data['Begin Date']
        event_name = event_data['Event Name']
        contact_name = event_data['Contact First Name']
        email = event_data['Contact E-mail']
        parking_structure = self.format_parking_structure(event_data['Requested Lot'])
        passcode = event_data['Confirmation/Reservation UID']
        event_link = self.get_event_link()
        
        logger.debug(f"Email parameters - Event: {event_name}, Date: {formatted_date}, Contact: {contact_name}")
        
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
        logger.info("Email content generated successfully")
        return html_content

    def open_email_in_new_tab(self, t2_data):
        try:
            logger.info("Opening email template in new tab")
            html_content = self.generate_email_content(t2_data)
            script = f'''
                var newWindow = window.open();
                newWindow.document.write(`{html_content}`);
                newWindow.document.close();
            '''
            self.driver.execute_script(script)
            
            logger.info("Opening T2 page in new tab")
            reservation_id = t2_data['t2_data']['Confirmation/Reservation UID']
            t2_url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={reservation_id}&addtoqueue=1"
            script = f'''window.open("{t2_url}", "_blank");'''
            self.driver.execute_script(script)
            logger.info("Both tabs opened successfully")
        except Exception as e:
            logger.error(f"Error opening tabs: {str(e)}")

    def handle_denial_process(self, t2_data):
        try:
            logger.info("Starting denial process")
            wait = WebDriverWait(self.driver, 10)
            reservation_id = t2_data['t2_data']['Confirmation/Reservation UID']
            target_url = f"PowerPark/reservation/view.aspx?id={reservation_id}"

            logger.debug(f"Switching to T2 reservation window for ID: {reservation_id}")
            window_found = False
            for window_handle in self.driver.window_handles:
                self.driver.switch_to.window(window_handle)
                if target_url in self.driver.current_url:
                    window_found = True
                    break

            if not window_found:
                raise Exception(f"Window not found for reservation {reservation_id}")
                
            # Check if the reservation is already denied
            try:
                status_elem = self.driver.find_element(By.ID, "MySettings_Reservation_ReservationStatus_T2Label_Label")
                if status_elem.text == "Denied":
                    logger.info("Reservation is already denied, no need to process denial")
                    raise Exception("Reservation is already in 'Denied' status")
            except Exception as e:
                logger.warning(f"Could not check reservation status: {str(e)}")
                
            # Check if the deny option is disabled
            try:
                deny_disabled = len(self.driver.find_elements(By.XPATH, "//tr[@class='PageSideBarItemDisabled']/td[contains(text(), 'Deny Reservation Confirmation')]")) > 0
                if deny_disabled:
                    logger.warning("Deny Reservation option is disabled")
                    raise Exception("Deny Reservation option is disabled")
            except Exception as e:
                logger.warning(f"Could not check if deny option is disabled: {str(e)}")

            logger.info("Locating and clicking deny link")
            deny_selector = '.PageSideBarItemEnabled a[href*="modifyType=Deny"]'
            deny_link = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, deny_selector))
            )
            self.driver.execute_script("arguments[0].scrollIntoView(true);", deny_link)
            deny_link.click()

            time.sleep(1)

            logger.info("Configuring note type")
            note_type_dropdown = wait.until(
                EC.presence_of_element_located((
                    By.ID,
                    'insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList'
                ))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", note_type_dropdown)
            wait.until(EC.element_to_be_clickable((
                By.ID,
                'insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList'
            )))

            select = Select(note_type_dropdown)
            select.select_by_value('2005')
            logger.debug("Note type selected: Department Reservations")

            time.sleep(0.5)

            logger.info("Adding event reference note")
            event_name = t2_data['t2_data']['Event Name']
            note_text = f'OFST- RE: {event_name}'

            textarea = wait.until(
                EC.presence_of_element_located((
                    By.ID,
                    'insertEditNoteControl1_WizardStep1_S1NoteText_T2FormTextBox_TextBox'
                ))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", textarea)
            textarea.clear()
            textarea.send_keys(note_text)

            logger.info("Saving denial note")
            save_selector = '#insertEditNoteControl1_SaveButton'
            save_button = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, save_selector))
            )

            self.driver.execute_script("arguments[0].scrollIntoView(true);", save_button)
            save_button.click()

            time.sleep(1)

            logger.info("Switching back to original tab")
            self.driver.switch_to.window(self.driver.window_handles[0])
            logger.info("Denial process completed successfully")

        except Exception as e:
            logger.error(f"Error in denial process: {str(e)}")
            try:
                logger.warning("Attempting to switch back to original tab after error")
                self.driver.switch_to.window(self.driver.window_handles[0])
            except:
                logger.error("Failed to switch back to original tab")

            root = tk.Tk()
            root.withdraw()
            error_window = tk.Toplevel(root)
            error_window.title("Error")
            error_window.geometry("400x150")
            error_window.resizable(False, False)

            error_label = tk.Label(
                error_window, 
                text="Oops something is wrong with the denial process", 
                wraplength=350,
                justify="center"
            )
            error_label.pack(pady=20)

            ok_button = tk.Button(
                error_window, 
                text="OK",
                command=error_window.destroy
            )
            ok_button.pack(pady=10)

            error_window.transient(root)
            error_window.grab_set()
            error_window.wait_window()
            root.destroy()