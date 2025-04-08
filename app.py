from tkinter import Tk, Label, Entry, Button, StringVar, filedialog, Frame, messagebox, Scrollbar, Text
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
import json

def get_current_version():
    """Read the current version from version.json."""
    version_file_path = os.path.join(BASE_DIR, "version.json")
    try:
        with open(version_file_path, "r") as version_file:
            version_data = json.load(version_file)
            return version_data.get("version", "0.0.0")  # Default to "0.0.0" if version is missing
    except FileNotFoundError:
        print("version.json not found. Defaulting to version 0.0.0.")
        return "0.0.0"
    except json.JSONDecodeError:
        print("Error decoding version.json. Defaulting to version 0.0.0.")
        return "0.0.0"

def check_for_updates():
    """Check GitHub for the latest version of the app."""
    current_version = get_current_version()
    repo_owner = "shiboof"  # Replace with your GitHub username
    repo_name = "sql_buddy"  # Replace with your repository name
    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        latest_release = response.json()
        latest_version = latest_release["tag_name"].lstrip("v")  # Remove 'v' prefix if present
        download_url = latest_release.get("html_url", "https://github.com")

        if latest_version != current_version:
            changelog = latest_release.get("body", "No changelog available.")
            messagebox.showinfo(
                "Update Available",
                f"A new version ({latest_version}) is available!\n\n"
                f"Changelog:\n{changelog}\n\n"
                f"Visit {download_url} to download the latest version."
            )
        else:
            print("You are using the latest version of the app.")
    except requests.RequestException as e:
        print(f"Error checking for updates: {e}")

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
        update_result_display("Please enter a serial number.")
        return

    # Validate the serial number
    if not serial_number.isdigit():
        update_result_display("Invalid serial number. Please enter a numeric value.")
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
            update_result_display(f"Location: {location}")
        else:
            update_result_display(f"Lockbox {serial_number} not found.")
    except Exception as e:
        update_result_display(f"Error: {e}")

def find_owner_gui():
    # Get the input from the user
    input_value = serial_number_var.get().strip()  # Strip whitespace
    if not input_value:
        update_result_display("Please enter a serial number or user ID.")
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
        update_result_display(result)
    except Exception as e:
        update_result_display(f"Error: {e}")
    
def save_output_to_csv():
    """Save the current output to a CSV file."""
    # Get the current output from the Text widget
    output = result_text.get("1.0", "end").strip()  # Get all text and strip trailing newline
    if not output:
        messagebox.showinfo("Save to CSV", "No output to save.")
        return

    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Output to CSV",
        defaultextension=".csv",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    if not file_path:
        return  # User canceled the save dialog

    try:
        # Parse the output into rows
        rows = [line.split(": ") for line in output.split("\n") if line]

        # Convert to a DataFrame and save to CSV
        df = pd.DataFrame(rows, columns=["Key", "Value"])
        df.to_csv(file_path, index=False)

        messagebox.showinfo("Save to CSV", f"Output successfully saved to {file_path}.")
    except Exception as e:
        messagebox.showerror("Save to CSV", f"Error saving output to CSV: {e}")


# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Check for updates
check_for_updates()

# Create the main GUI window
root = Tk()
root.title("Lockbox Finder")
root.configure(bg="#f0f0f0")  # Set background color
center_window(root, 500, 500)  # Center the window

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
Button(frame, text="Save to CSV", command=save_output_to_csv, font=("Arial", 10), bg="#0078D7", fg="white").grid(row=5, column=0, columnspan=2, pady=10)

# Create a frame for the output box and scrollbar
output_frame = Frame(root, bg="#f0f0f0")
output_frame.pack(pady=10, padx=10)

# Create the output box (Text widget)
result_text = Text(output_frame, wrap="word", font=("Arial", 10), width=50, height=15)
result_text.grid(row=0, column=0, sticky="nsew")

# Create the scrollbar
scrollbar = Scrollbar(output_frame, orient="vertical", command=result_text.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

# Link the scrollbar to the output box
result_text.configure(yscrollcommand=scrollbar.set)

# Configure the frame to expand with the window
output_frame.grid_rowconfigure(0, weight=1)
output_frame.grid_columnconfigure(0, weight=1)

# Update the result display logic to use the Text widget
def update_result_display(result):
    result_text.delete("1.0", "end")  # Clear the output box
    result_text.insert("end", result)  # Insert the new result

# Run the GUI event loop
root.mainloop()