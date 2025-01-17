import tkinter as tk
from tkinter import messagebox

class PopUp:
    def __init__(self):
        # Initialize a flag to keep track of whether the popup should be shown
        self.suppress_warning = False
    
    def show_popup(self, title, message):
        """Display a popup with an option to suppress it for this session."""
        if self.suppress_warning:
            return  # Don't show the popup if it's suppressed
        
        # Create a root window but don't show it
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        # Ask the user if they want to suppress the warning
        response = messagebox.askyesno(
            title, message + "\n\nDo you want to hide this warning in the future during this session?"
        )

        # If the user clicks 'YES', save the preference to suppress future warnings for the session
        if response:
            self.suppress_warning = True
        
        root.destroy()  # Destroy the root window after the popup

    def show_popup_yesno(self, title, message):
        """Display a popup with 'Yes' and 'No' options."""
        root = tk.Tk()
        root.withdraw()

        response = messagebox.askyesno(title, message)

        root.destroy()
        return response

    def reset_suppression(self):
        """Reset the suppression flag, allowing popups to show again."""
        self.suppress_warning = False
