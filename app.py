import customtkinter as ctk
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
from tkinter import filedialog, Tk  # Import Tk explicitly

# Define constants for the GitHub API URL and current version
GITHUB_API_URL = "https://api.github.com/repos/shiboof/sql_buddy/releases/latest"
CURRENT_VERSION = "v1.1.3"  # Replace with your current version

# Set the default appearance mode
ctk.set_appearance_mode("light")  # Default to light mode
ctk.set_default_color_theme("blue")  # Use the blue color theme

# Global variable for dark mode state
is_dark_mode = False

def toggle_dark_mode():
    """Toggle between light and dark mode."""
    global is_dark_mode
    is_dark_mode = not is_dark_mode

    # Define light and dark mode colors
    if is_dark_mode:
        ctk.set_appearance_mode("dark")  # Set customtkinter to dark mode
    else:
        ctk.set_appearance_mode("light")  # Set customtkinter to light mode

def show_ctk_messagebox(root, title, message, message_type="info"):
    """Custom message box using customtkinter."""
    # Create a Toplevel window tied to the main root window
    dialog = ctk.CTkToplevel(root)  # Pass the root window explicitly
    dialog.title(title)
    dialog.geometry("400x200")
    dialog.resizable(False, False)

    # Add message label
    label = ctk.CTkLabel(dialog, text=message, font=("Helvetica", 14), wraplength=350)
    label.pack(pady=20, padx=20)

    # Add OK button
    ok_button = ctk.CTkButton(dialog, text="OK", command=dialog.destroy, fg_color="blue", hover_color="darkblue")
    ok_button.pack(pady=10)

    # Make the dialog modal
    dialog.grab_set()
    dialog.wait_window(dialog)  # Ensure the window is destroyed after closing

def check_for_updates():
    """Check GitHub for the latest release version."""
    try:
        response = requests.get(GITHUB_API_URL, timeout=5)
        response.raise_for_status()
        latest_release = response.json()
        latest_version = latest_release.get("tag_name", "0.0.0")

        if latest_version > CURRENT_VERSION:
            message = (
                f"A new version ({latest_version}) is available!\n"
                f"Please update your application.\n\n"
                f"Visit\nhttps://github.com/Shiboof/sql_buddy/releases\n to download the latest version."
            )
            show_ctk_messagebox(root, "Update Available", message)
        else:
            show_ctk_messagebox(root, "Up-to-Date", "You are using the latest version.")
    except requests.RequestException as e:
        show_ctk_messagebox(root, "Update Check Failed", f"Could not check for updates: {e}", message_type="error")

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
        show_ctk_messagebox(root, "Save to CSV", "No output to save.")
        return

    # Create a hidden Tk instance to avoid redundant windows
    root_tk = Tk()
    root_tk.withdraw()  # Hide the root window

    # Ask the user where to save the file
    file_path = filedialog.asksaveasfilename(
        title="Save Output to CSV",
        defaultextension=".csv",
        filetypes=(("CSV Files", "*.csv"), ("All Files", "*.*"))
    )
    root_tk.destroy()  # Destroy the hidden Tk instance

    if not file_path:
        return  # User canceled the save dialog

    try:
        # Parse the output into rows
        rows = [line.split(": ") for line in output.split("\n") if line]

        # Convert to a DataFrame and save to CSV
        df = pd.DataFrame(rows, columns=["Key", "Value"])
        df.to_csv(file_path, index=False)

        show_ctk_messagebox(root, "Save to CSV", f"Output successfully saved to {file_path}.")
    except Exception as e:
        show_ctk_messagebox(root, "Save to CSV", f"Error saving output to CSV: {e}", message_type="error")

# Get the directory of the current script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Create the main GUI window
root = ctk.CTk()
root.title("Lockbox Finder")  # Set background color
center_window(root, 600, 500)  # Center the window

# Force the window to open in the foreground
# root.attributes('-topmost', True)
# root.update()
# root.attributes('-topmost', False)

# Check for updates (after root is created)
check_for_updates()

# Set the Window Icon
icon_path = os.path.join(BASE_DIR, "assets", "app_icon.ico")
if os.path.exists(icon_path):
    root.iconbitmap(icon_path)
else:
    print(f"Icon file not found at {icon_path}. Using default icon.")

# Add a dark mode toggle button
dark_mode_button = ctk.CTkButton(
    root,
    text="Dark Mode",
    command=toggle_dark_mode,
    fg_color="#0078D7",
    text_color="white",
    hover_color="#005BB5",
    width=100,
    height=30,
    corner_radius=15
)
dark_mode_button.place(x=10, y=10)  # Position the button at the top left corner

# Create a frame for the input and buttons
frame = ctk.CTkFrame(root)
frame.pack(pady=20)

# Input field for serial number
ctk.CTkLabel(frame, text="Enter Lockbox Serial Number or User ID:", font=("Arial", 12)).grid(row=0, column=0, columnspan=2, pady=5)
serial_number_var = ctk.StringVar()
ctk.CTkEntry(frame, textvariable=serial_number_var, font=("Arial", 12), width=300).grid(row=1, column=0, columnspan=2, pady=5)

# Buttons
ctk.CTkButton(frame, text="Find Location", command=find_location_gui, font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=2, column=0, padx=5, pady=10)
ctk.CTkButton(frame, text="Find Owner", command=find_owner_gui, font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=2, column=1, padx=5, pady=10)
ctk.CTkButton(frame, text="Upload CSV", command=lambda: process_csv(db_config, result_text), font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=3, column=0, columnspan=2, pady=10)
ctk.CTkButton(frame, text="EZ-SQL", command=lambda: open_ez_sql_window(root), font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=4, column=0, columnspan=2, pady=10)
ctk.CTkButton(frame, text="Save to CSV", command=save_output_to_csv, font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=5, column=0, columnspan=2, pady=10)

# Create a frame for the output box and scrollbar
output_frame = ctk.CTkFrame(root)
output_frame.pack(pady=10, padx=10)

# Create the output box (Text widget)
result_text = ctk.CTkTextbox(output_frame, wrap="word", font=("Arial", 10), width=500, height=300)
result_text.grid(row=0, column=0, sticky="nsew")

# Create the scrollbar
scrollbar = ctk.CTkScrollbar(output_frame, orientation="vertical", command=result_text.yview)
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