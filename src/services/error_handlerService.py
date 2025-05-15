import tkinter as tk
import logging
import sys

logger = logging.getLogger('ErrorHandler')

def handle_critical_error(message, browser=None):
    logger.error(message)
    
    # Close the browser if passed
    if browser:
        try:
            logger.info("Closing browser due to critical error")
            browser.close()
        except Exception as e:
            logger.error(f"Failed to close browser: {str(e)}")

    # Show tkinter popup
    try:
        root = tk.Tk()
        root.withdraw()
        
        error_window = tk.Toplevel(root)
        error_window.title("Critical Error")
        error_window.geometry("400x150")
        error_window.resizable(False, False)

        label = tk.Label(
            error_window, 
            text=message,
            wraplength=350,
            justify="center",
            fg="red"
        )
        label.pack(pady=20)

        button = tk.Button(
            error_window, 
            text="Exit", 
            command=error_window.destroy
        )
        button.pack(pady=10)

        error_window.transient(root)
        error_window.grab_set()
        error_window.wait_window()
        root.destroy()
    except Exception as popup_error:
        logger.error(f"Failed to show error dialog: {str(popup_error)}")

    sys.exit(1)
