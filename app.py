from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, Frame
import os
import sys
import pandas as pd
from database.connection import get_connection
from models.lockbox import Lockbox
from models.owners import Owner
import database.db_config as db_config
from utils.helpers import process_csv
from utils.driver_installer import check_and_install_odbc_driver
import requests
from models.ez_sql import open_ez_sql_window

# Check and install ODBC driver if necessary
if not check_and_install_odbc_driver():
    print("Failed to install ODBC Driver. Exiting...")
    sys.exit(1)

def center_window(window, width, height):
    """Center the window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")

def find_location_gui():
    # Get the serial number from the input field
    serial_number = serial_number_var.get().strip()  # Strip whitespace
    if not serial_number:
        result_var.set("Please enter a serial number.")
        return

    # Validate the serial number
    if not serial_number.isdigit():
        result_var.set("Invalid serial number. Please enter a numeric value.")
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

def find_owner_gui():
    # Get the input from the user
    input_value = serial_number_var.get().strip()  # Strip whitespace
    if not input_value:
        result_var.set("Please enter a serial number or user ID.")
        return

    # Initialize variables
    user_id = None
    serial_number = None

    # Treat all inputs as strings to avoid overflow errors
    if input_value.isdigit() and len(input_value) < 7:  # Adjust length as per your user_id format
        user_id = input_value  # Treat as user_id
    else:
        serial_number = input_value  # Treat as serial_number

    # Connect to the database
    try:
        connection = get_connection(
            db_config.server,
            db_config.database,
            db_config.username,
            db_config.password
        )
        owner = Owner(serial_number=serial_number, user_id=user_id)
        result = owner.find_user_and_lockboxes(connection)
        connection.close()

        # Display the result
        result_var.set(result)
    except Exception as e:
        result_var.set(f"Error: {e}")

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the main GUI window
root = Tk()
root.title("Lockbox Finder")
root.configure(bg="#f0f0f0")  # Set background color
center_window(root, 400, 400)  # Center the window

# Force the window to open in the foreground
root.attributes('-topmost', True)
root.update()
root.attributes('-topmost', False)

# Set the Window Icon
icon_path = os.path.join(BASE_DIR, "assets", "app_icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
else:
    print(f"Icon file not found at {icon_path}. Using default icon.")

# Create a frame for the input and buttons
frame = Frame(root, bg="#f0f0f0")
frame.pack(pady=20)

# Input field for serial number
Label(frame, text="Enter Lockbox Serial Number or User ID:", font=("Arial", 12), bg="#f0f0f0").grid(row=0, column=0, columnspan=2, pady=5)
serial_number_var = StringVar()
Entry(frame, textvariable=serial_number_var, font=("Arial", 12), width=30).grid(row=1, column=0, columnspan=2, pady=5)

# Buttons
Button(frame, text="Find Location", command=find_location_gui, font=("Arial", 10), bg="#0078D7", fg="white").grid(row=2, column=0, padx=5, pady=10)
Button(frame, text="Find Owner", command=find_owner_gui, font=("Arial", 10), bg="#0078D7", fg="white").grid(row=2, column=1, padx=5, pady=10)
Button(frame, text="Upload CSV", command=lambda: process_csv(db_config, result_var), font=("Arial", 10), bg="#0078D7", fg="white").grid(row=3, column=0, columnspan=2, pady=10)
Button(frame, text="EZ-SQL", command=lambda: open_ez_sql_window(root), font=("Arial", 10), bg="#0078D7", fg="white").grid(row=4, column=0, columnspan=2, pady=10)

# Label to display the result
result_var = StringVar()
Label(root, textvariable=result_var, wraplength=350, font=("Arial", 10), bg="#f0f0f0", fg="black").pack(pady=10)

# Run the GUI event loop
root.mainloop()