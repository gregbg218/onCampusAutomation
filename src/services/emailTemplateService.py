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
        html_content = self.generate_email_content(t2_data)
        script = f'''
            var newWindow = window.open();
            newWindow.document.write(`{html_content}`);
            newWindow.document.close();
        '''
        self.driver.execute_script(script)