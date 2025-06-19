import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import logging
import tkinter as tk
from tkinter import messagebox

logger = logging.getLogger('EmailTemplate')

class EmailTemplateService:
    """Handle Offstreet e‑mail generation and T2 reservation denial.

    If the reservation is already denied—or the **Deny Reservation** link is
    missing/disabled—we pop a small info dialog that says *"Reservation already
    denied."*  When the user presses **OK** we simply return `True` so the
    automation can proceed to the next reservation without raising.  This keeps
    the flow smooth while still notifying the operator.
    """

    def __init__(self, driver):
        logger.info("Initializing EmailTemplateService")
        self.driver = driver

    # ------------------------------------------------------------------
    # Basic helpers
    # ------------------------------------------------------------------
    def format_parking_structure(self, raw_name: str) -> str:
        logger.debug(f"Formatting parking structure name: {raw_name}")
        mappings = {
            'Biggy': 'Biggy Structure',
            'San Pablo': 'San Pablo Parking Structure',
            'Figueroa': 'Figueroa Street Structure',
        }
        for key, val in mappings.items():
            if key.lower() in raw_name.lower():
                return val
        return raw_name

    def show_already_denied_popup(self):
        """Top‑most info dialog telling the user the reservation is already denied."""
        logger.info("Showing 'already denied' popup")
        try:
            root = tk.Tk()
            root.attributes('-topmost', True)
            root.withdraw()  # keep the root window hidden
            messagebox.showinfo("Already Denied", "Reservation already denied.", parent=root)
            root.destroy()
        except Exception as e:
            # If Tk blows up (e.g. DISPLAY issues on headless boxes) just log.
            logger.error(f"Failed to display Tk popup: {str(e)}")

    # ------------------------------------------------------------------
    # Email generation helpers
    # ------------------------------------------------------------------
    def _get_event_link(self):
        logger.info("Retrieving event link from Offstreet")
        try:
            link_el = self.driver.find_element(By.CSS_SELECTOR, 'a[href^="https://www.offstreet.io/events/"]')
            href = link_el.get_attribute('href')
            logger.debug(f"Event link found: {href}")
            return href
        except Exception:
            logger.warning("Event link not found – using placeholder")
            return '[EVENT_LINK_NOT_FOUND]'

    def _build_email_html(self, t2_data: dict) -> str:
        data = t2_data['t2_data']
        begin_date = data['Begin Date']
        event_name = data['Event Name']
        contact_name = data['Contact First Name']
        email_addr = data['Contact E-mail']
        parking_structure = self.format_parking_structure(data['Requested Lot'])
        passcode = data['Confirmation/Reservation UID']
        event_link = self._get_event_link()

        logger.debug("Composing HTML e‑mail body")
        return f"""
        <html><head><style>
          body {{font-family: Arial, sans-serif;}}
          ul {{list-style-type: disc; padding-left: 40px;}}
        </style></head><body>
          <p>OFST- RE: {event_name}</p>
          <p>Transportation Parking Reservations</p>
          <p>{email_addr}</p>
          <p><strong>Reference: {event_name} {begin_date}</strong></p><br>
          <p>Hello {contact_name},</p><br>
          <p>Please note that RSVP {passcode} has been moved to our digital
          platform.  Below are the instructions for guests:</p><br>
          <ul>
            <li><b>Registration link:</b> <a href='{event_link}'>{event_link}</a></li>
            <li><b>License plate</b> will serve as the permit – no paper pass.</li>
            <li><b>Pass Code:</b> {passcode}</li>
            <li><b>Assigned structure:</b> {parking_structure}</li>
          </ul><br>
          <p>Please avoid reserved spaces.  Thank you!</p>
        </body></html>"""

    def open_email_in_new_tab(self, t2_data: dict):
        logger.info("Opening generated e‑mail + T2 tab in browser")
        try:
            html = self._build_email_html(t2_data)
            self.driver.execute_script(
                "var w = window.open(); w.document.write(arguments[0]); w.document.close();",
                html,
            )
            res_id = t2_data['t2_data']['Confirmation/Reservation UID']
            t2_url = f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={res_id}&addtoqueue=1"
            self.driver.execute_script("window.open(arguments[0], '_blank');", t2_url)
        except Exception as e:
            logger.error(f"Error opening e‑mail/T2 tabs: {str(e)}")

    # ------------------------------------------------------------------
    # Denial flow
    # ------------------------------------------------------------------
    def handle_denial_process(self, t2_data: dict):
        """Deny the reservation if possible; otherwise pop‑up & return True."""
        logger.info("Starting denial process")
        wait = WebDriverWait(self.driver, 10)
        res_id = t2_data['t2_data']['Confirmation/Reservation UID']
        frag = f"PowerPark/reservation/view.aspx?id={res_id}"

        # ------------------------------------------------------------------
        # 1) Switch to reservation tab (if any)
        # ------------------------------------------------------------------
        for h in self.driver.window_handles:
            self.driver.switch_to.window(h)
            if frag in self.driver.current_url:
                break
        else:
            logger.warning("Reservation tab not found – treating as already denied")
            self.show_already_denied_popup()
            return True

        # ------------------------------------------------------------------
        # 2) If status already Denied → popup & done
        # ------------------------------------------------------------------
        try:
            status = self.driver.find_element(By.ID, 'MySettings_Reservation_ReservationStatus_T2Label_Label').text.strip()
            if status.lower() == 'denied':
                logger.info("Status already Denied")
                self.show_already_denied_popup()
                return True
        except Exception:
            pass

        # ------------------------------------------------------------------
        # 3) Is the Deny link enabled?
        # ------------------------------------------------------------------
        deny_css = '.PageSideBarItemEnabled a[href*="modifyType=Deny"]'
        if not self.driver.find_elements(By.CSS_SELECTOR, deny_css):
            logger.info("Deny link missing/disabled – popup & continue")
            self.show_already_denied_popup()
            return True

        # ------------------------------------------------------------------
        # 4) Proceed with normal Deny flow
        # ------------------------------------------------------------------
        try:
            deny_link = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, deny_css)))
            self.driver.execute_script("arguments[0].scrollIntoView(true);", deny_link)
            deny_link.click()
            time.sleep(1)

            # Select note type
            dropdown = wait.until(EC.presence_of_element_located((By.ID,
                'insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList')))
            Select(dropdown).select_by_value('2005')  # Department Reservations

            # Note text
            textarea = wait.until(EC.presence_of_element_located((By.ID,
                'insertEditNoteControl1_WizardStep1_S1NoteText_T2FormTextBox_TextBox')))
            note = f"OFST- RE: {t2_data['t2_data']['Event Name']}"
            textarea.clear(); textarea.send_keys(note)

            # Save
            save_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                '#insertEditNoteControl1_SaveButton')))
            save_btn.click()
            time.sleep(1)
            logger.info("Reservation denied successfully")
        except Exception as e:
            logger.error(f"Deny flow failed – {str(e)} (showing popup but continuing)")
            self.show_already_denied_popup()

        # Always return to Offstreet tab (first handle)
        if self.driver.window_handles:
            self.driver.switch_to.window(self.driver.window_handles[0])
        return True
