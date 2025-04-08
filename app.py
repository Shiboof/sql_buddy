import os
import sys
from tkinter import Tk, Label, Entry, Button, StringVar, filedialog
import pandas as pd
from database.connection import get_connection
from models.lockbox import Lockbox
import database.db_config as db_config  # Import the configuration file
from utils.helpers import process_csv  # Import the refactored function
from utils.driver_installer import check_and_install_odbc_driver

# Check and install ODBC driver if necessary
if not check_and_install_odbc_driver():
    print("Failed to install ODBC Driver. Exiting...")
    sys.exit(1)

def find_location_gui():
    # Get the serial number from the input field
    serial_number = serial_number_var.get()
    if not serial_number:
        result_var.set("Please enter a serial number.")
        return

    # Connect to the database
    try:
        connection = get_connection(
            db_config.server,
            db_config.database,
            db_config.username,
            db_config.password
        )
        lockbox = Lockbox(serial_number)
        location = lockbox.find_location(connection)
        connection.close()

        # Display the result
        if location:
            result_var.set(f"Location: {location}")
        else:
            result_var.set(f"Lockbox {serial_number} not found.")
    except Exception as e:
        result_var.set(f"Error: {e}")

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the main GUI window
root = Tk()
root.title("Lockbox Finder")

# Set the Window Icon
icon_path = os.path.join(BASE_DIR, "assets", "app_icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
else:
    print(f"Icon file not found at {icon_path}. Using default icon.")

# Input field for serial number
Label(root, text="Enter Lockbox Serial Number:").grid(row=0, column=0, padx=10, pady=10)
serial_number_var = StringVar()
Entry(root, textvariable=serial_number_var).grid(row=0, column=1, padx=10, pady=10)

# Button to find the location
Button(root, text="Find Location", command=find_location_gui).grid(row=1, column=0, columnspan=2, pady=10)

# Button to upload and process CSV
Button(root, text="Upload CSV", command=lambda: process_csv(db_config, result_var)).grid(row=2, column=0, columnspan=2, pady=10)
# Label to display the result
result_var = StringVar()
Label(root, textvariable=result_var, wraplength=300).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Run the GUI event loop
root.mainloop()