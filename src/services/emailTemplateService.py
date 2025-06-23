import time
import logging
import tkinter as tk
import tkinter.messagebox as mbox

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  # ⬅ add at top of file
logger = logging.getLogger("EmailTemplate")


class EmailTemplateService:
    """
    • Builds the Offstreet e-mail (original HTML kept verbatim).
    • Tries to deny the reservation in T2; if already denied, shows a popup.
    • Always jumps back to Offstreet, clicks the **Share** tab, then:
        1. Clicks **Load Template**
        2. Waits 0.5 s
        3. Clicks **Event Template w/Code**
    """

    # ─────────────────────────────  setup  ──────────────────────────────
    def __init__(self, driver):
        logger.info("Initializing EmailTemplateService")
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    # ─────────────────────────  UI helpers  ────────────────────────────
    def _info_popup(self, msg: str):
        """Always-on-top modal so the operator *sees* the message."""
        logger.info(f"Popup → {msg}")
        try:
            root = tk.Tk()
            root.withdraw()                # hide the empty root window
            root.after(10, lambda: root.focus_force())
            root.after(10, lambda: root.attributes("-topmost", True))
            mbox.showinfo("Info", msg, parent=root)
            root.destroy()
        except Exception as exc:
            logger.error(f"Popup failed: {exc}")


# ───────────────────────  Share & templates  ──────────────────────
    def click_load_template_button(self):
        """Standalone helper to click the **Load Template** button."""
        logger.info("Clicking standalone 'Load Template' button")
        try:
            load_btn = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//button[normalize-space()='Load Template']")))
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", load_btn)
            load_btn.click(); logger.info("Load Template clicked (standalone)")
        except Exception as exc:
            logger.error(f"Standalone Load Template click failed: {exc}")

        # ───────────────────────  Share-template sequence  ───────────────────────
    def _apply_share_template(self):
        """
        1) Click the outer **Load Template** button in the Share form.
        2) Wait a moment for the “Load Template” dialog to render.
        3) Inside that dialog, click **Event Template w/Code**.
        4) Click the dialog-footer **Load Template** button to confirm.

        Uses separate XPaths (no string concatenation) so they remain valid.
        """
        try:
            # ---------- 1️⃣  OUTER “Load Template” (in Share form) ----------
            outer_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        # must NOT be inside any dialog
                        "//form//button[normalize-space()='Load Template' "
                        "and not(ancestor::*[@role='dialog'])]"
                    )
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", outer_btn
            )
            outer_btn.click()
            logger.info("Outer 'Load Template' clicked")

            # ---------- give the modal time to appear ----------
            time.sleep(0.5)

            # ---------- 2️⃣  “Event Template w/Code” inside the dialog ----------
            dlg_xpath   = "//div[@role='dialog' and .//h2[normalize-space()='Load Template']]"
            event_xpath = "//div[@role='dialog']//button[normalize-space()='Event Template w/Code']"

            # make sure the dialog is present
            self.wait.until(EC.presence_of_element_located((By.XPATH, dlg_xpath)))

            event_btn = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, event_xpath))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", event_btn
            )
            event_btn.click()
            logger.info("'Event Template w/Code' clicked")

            # ---------- 3️⃣  INNER “Load Template” (dialog footer) ----------
            inner_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        # footer button inside the same dialog
                        f"{dlg_xpath}//button[normalize-space()='Load Template']"
                    )
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", inner_btn
            )
# ─ inside  _apply_share_template() ─
            inner_btn.click()
            logger.info("Inner 'Load Template' clicked")

            # NEW ↓ – wait until the dialog goes away
            self.wait.until(
                EC.invisibility_of_element_located(
                    (By.XPATH,
                    "//div[@role='dialog' and .//h2[normalize-space()='Load Template']]")
                )
            )

            self._fill_reply_to_email()
            
            self._fill_subject()          #  ← keep this call, but now the field is interactable
            self._clear_all_recipient_pills()
            

        except Exception as exc:
            logger.error(f"Share-template sequence failed: {exc}")




    def _fill_reply_to_email(self, address: str = "parkrsvp@usc.edu") -> bool:
        """Types the address, presses Enter, confirms pill appears."""
        try:
            logger.info(f"Setting Reply-To address → {address}")

            inp = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='replyToEmails']"))
            )
            inp.click()
            inp.clear()
            inp.send_keys(address)
            inp.send_keys(Keys.ENTER)

            # pill confirmation: look for the span text (class is 'truncate')
            self.wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//button/span[normalize-space()='{address}']")
                )
            )
            logger.info("Reply-To address set successfully")
            return True

        except Exception as exc:
            logger.error(f"Failed to set Reply-To address: {exc}")
            return False


    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
    import time, logging

    def _clear_all_recipient_pills(self) -> None:
        """
        Remove every recipient pill in the combobox.
        Checks 4× at 0.5-s intervals (max 2 s) and exits
        as soon as the pills are gone or never appear.
        """
        css = "div[role='combobox'] button svg[data-slot='icon']"
        for _ in range(4):                       # 0 s, 0.5 s, 1 s, 1.5 s
            icons = self.driver.find_elements(By.CSS_SELECTOR, css)
            if icons:
                break
            time.sleep(0.5)
        else:
            return                                # nothing ever appeared

        while True:
            icons = self.driver.find_elements(By.CSS_SELECTOR, css)
            if not icons:
                break
            for icon in icons:
                self.driver.execute_script(
                    "arguments[0].click();", icon.find_element(By.XPATH, "./..")
                )
                time.sleep(0.1)
        logging.getLogger("EmailTemplate").info("All recipient pills cleared")


    def _fill_subject(
            self,
            text: str = "Transportation Parking Reservations"
    ) -> bool:
        """Sets the e-mail subject line via JavaScript only (no send_keys)."""
        try:
            subj = self.wait.until(
                EC.presence_of_element_located((By.ID, "subject"))
            )
            self.driver.execute_script(
                """
                arguments[0].scrollIntoView({block:'center'});
                arguments[0].value = arguments[1];
                arguments[0].dispatchEvent(new Event('input', { bubbles:true }));
                """,
                subj,
                text,
            )

            # verify the value actually stuck
            self.wait.until(
                EC.text_to_be_present_in_element_value((By.ID, "subject"), text)
            )
            logger.info("Subject line set successfully")
            return True

        except Exception as exc:
            logger.error(f"Failed to set subject via JS: {exc}")
            return False








    def _click_share_tab(self):
        """Focus Offstreet, click **Share**, then load the e-mail template."""
        logger.info("Switching to Offstreet & clicking Share tab")
        try:
            # find Offstreet dashboard tab
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if "dashboard.offstreet.io" in self.driver.current_url:
                    break
            else:  # fallback to first handle
                if self.driver.window_handles:
                    self.driver.switch_to.window(self.driver.window_handles[0])

            share_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//button[contains(@class,'snap-center') "
                        "and contains(normalize-space(.),'Share')]",
                    )
                )
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", share_btn
            )
            share_btn.click()
            logger.info("Share tab clicked")

            # now load the standard template
            self._apply_share_template()
        except Exception as exc:
            logger.error(f"Share tab click failed: {exc}")

    # ─────────────────────  e-mail HTML helpers  ───────────────────────
    @staticmethod
    def _format_parking_structure(name: str) -> str:
        if "Biggy" in name:
            return "Biggy Structure"
        elif "San Pablo" in name:
            return "San Pablo Parking Structure"
        elif "Figueroa" in name:
            return "Figueroa Street Structure"
        return name

    def _get_event_link(self) -> str:
        try:
            el = self.driver.find_element(
                By.CSS_SELECTOR, 'a[href^="https://www.offstreet.io/events/"]'
            )
            return el.get_attribute("href")
        except Exception:
            return "[EVENT_LINK_NOT_FOUND]"

    def generate_email_content(self, t2_data: dict) -> str:
        d = t2_data["t2_data"]
        formatted_date = d["Begin Date"]
        event_name = d["Event Name"]
        contact_name = d["Contact First Name"]
        email = d["Contact E-mail"]
        parking_structure = self._format_parking_structure(d["Requested Lot"])
        passcode = d["Confirmation/Reservation UID"]
        event_link = self._get_event_link()

        return f"""
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
                <li><strong>Parking Confirmation Receipt:</strong> After completing your registration, enter your e-mail for a receipt copy (optional). Your license plate is your permit. No paper pass required to be displayed. You are now all set to park!</li>
                <li><strong>Additional Notes:</strong> Your assigned parking structure is: <span style="font-weight: bold;">{parking_structure}</span> (Refer to Welcome Registration page for Parking Map)</li>
            </ul><br>
            <p>Please make sure you do NOT park in any reserved/signage space as these are for reserved permit holders only! Thank you!</p>
        </body>
        </html>
        """

    # ─────────────────────  preview e-mail & T2  ────────────────────────
    def open_email_in_new_tab(self, t2_data: dict):
        logger.info("Opening email + T2 tabs")
        try:
            html = self.generate_email_content(t2_data)
            # email preview
            self.driver.execute_script(
                "var w=window.open(); w.document.write(arguments[0]); w.document.close();",
                html,
            )
            # T2 reservation tab
            rid = t2_data["t2_data"]["Confirmation/Reservation UID"]
            self.driver.execute_script(
                "window.open(arguments[0],'_blank');",
                f"https://usc.t2flex.com/PowerPark/reservation/view.aspx?id={rid}&addtoqueue=1",
            )
        except Exception as exc:
            logger.error(f"Tab open failed: {exc}")

    # ────────────────────────────  denial  ─────────────────────────────
    def handle_denial_process(self, t2_data: dict):
        logger.info("Denial process started")
        rid = t2_data["t2_data"]["Confirmation/Reservation UID"]
        frag = f"PowerPark/reservation/view.aspx?id={rid}"

        # 1) switch to reservation tab
        for h in self.driver.window_handles:
            self.driver.switch_to.window(h)
            if frag in self.driver.current_url:
                break
        else:
            logger.warning("Reservation tab not found – assume already denied")
            self._info_popup("Reservation already denied.")
            self._click_share_tab()
            return True

        # 2) already denied?
        try:
            status = (
                self.driver.find_element(
                    By.ID, "MySettings_Reservation_ReservationStatus_T2Label_Label"
                )
                .text.strip()
                .lower()
            )
            if status == "denied":
                logger.info("Already denied")
                self._info_popup("Reservation already denied.")
                self._click_share_tab()
                return True
        except Exception:
            pass

        # 3) deny link available?
        deny_css = '.PageSideBarItemEnabled a[href*="modifyType=Deny"]'
        if not self.driver.find_elements(By.CSS_SELECTOR, deny_css):
            logger.info("Deny link disabled/missing")
            self._info_popup("Reservation already denied.")
            self._click_share_tab()
            return True

        # 4) perform denial
        try:
            deny_link = self.wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, deny_css))
            )
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", deny_link
            )
            deny_link.click()
            time.sleep(1)

            # select note type
            Select(
                self.wait.until(
                    EC.presence_of_element_located(
                        (
                            By.ID,
                            "insertEditNoteControl1_WizardStep1_S1NoteType_T2DropDownList_DropDownList",
                        )
                    )
                )
            ).select_by_value("2005")

            # note text
            note_area = self.wait.until(
                EC.presence_of_element_located(
                    (
                        By.ID,
                        "insertEditNoteControl1_WizardStep1_S1NoteText_T2FormTextBox_TextBox",
                    )
                )
            )
            note_area.clear()
            note_area.send_keys(f"OFST- RE: {t2_data['t2_data']['Event Name']}")

            # save
            save_btn = self.wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#insertEditNoteControl1_SaveButton")
                )
            )
            save_btn.click()
            time.sleep(1)
            logger.info("Reservation denied successfully")
        except Exception as exc:
            logger.error(f"Deny flow failed: {exc}")
            self._info_popup("Issue during denial – proceeding anyway.")

        # 5) finish with Share + template
        self._click_share_tab()
        return True
