import os
import subprocess

def check_and_install_odbc_driver():
    try:
        # Check if the ODBC Driver is installed
        import pyodbc
        drivers = [driver for driver in pyodbc.drivers() if "ODBC Driver" in driver]
        if drivers:
            print(f"ODBC Driver already installed: {drivers}")
            return True

        # If not installed, run the installer
        print("ODBC Driver not found. Installing...")
        installer_path = os.path.join(os.path.dirname(__file__), "../drivers/msodbcsql.msi")
        subprocess.run(["msiexec", "/i", installer_path, "/quiet", "/norestart"], check=True)
        print("ODBC Driver installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing ODBC Driver: {e}")
        return False