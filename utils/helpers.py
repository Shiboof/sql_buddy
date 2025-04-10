import pandas as pd
from tkinter import filedialog, Tk  # Explicitly import filedialog and Tk to avoid redundant Tk windows
from models.lockbox import Lockbox
from database.connection import get_connection
import customtkinter as ctk  # Import CustomTkinter

def validate_serial_number(serial_number):
    if not isinstance(serial_number, str):
        raise ValueError("Serial number must be a string.")
    if len(serial_number) == 0:
        raise ValueError("Serial number cannot be empty.")
    return True

def format_output(lockbox_location):
    if lockbox_location:
        return f"The lockbox is located at: {lockbox_location}"
    else:
        return "Lockbox not found."
    
def process_csv(db_config, result_var):
    """Process a CSV file and find lockbox locations."""
    # Create a hidden Tk instance to avoid redundant windows
    root = Tk()
    root.withdraw()  # Hide the root window

    # Open a file dialog to select the CSV file
    file_path = filedialog.askopenfilename(
        title="Select CSV File",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    root.destroy()  # Destroy the hidden Tk instance

    if not file_path:
        result_var.set("No file selected.")
        return

    try:
        # Read the CSV file
        data = pd.read_csv(file_path)

        # Check if 'LBSN' column exists
        if 'LBSN' not in data.columns:
            result_var.set("CSV file must contain an 'LBSN' column.")
            return

        # Connect to the database
        connection = get_connection(
            db_config.server,
            db_config.database,
            db_config.username,
            db_config.password
        )

        # Process each serial number and find its location
        locations = []
        for serial_number in data['LBSN']:
            try:
                lockbox = Lockbox(serial_number)
                location = lockbox.find_location(connection)
                if location:
                    locations.append(f"{serial_number}: {location}")
                else:
                    locations.append(f"{serial_number}: Not found")
            except Exception as e:
                locations.append(f"{serial_number}: Error - {e}")

        connection.close()

        # Display the results
        result_var.set("\n".join(locations))
    except Exception as e:
        result_var.set(f"Error processing CSV: {e}")