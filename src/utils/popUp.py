import tkinter as tk
from tkinter import messagebox

def show_popup(title, message):
    """Display a popup message with a given title and message."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showwarning(title, message)
    root.destroy()  # Destroy the root window after the popup
