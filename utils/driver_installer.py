import os
import subprocess
import sys
import urllib.request

def check_and_install_odbc_driver():
    try:
        # Check if any ODBC Driver for SQL Server is installed
        import pyodbc
        drivers = pyodbc.drivers()
        print(f"Installed ODBC Drivers: {drivers}")

        # Check for ODBC Driver 18
        if "ODBC Driver 18 for SQL Server" in drivers:
            print("ODBC Driver 18 for SQL Server is already installed.")
            return True

        # Check for older versions of the ODBC Driver
        older_versions = [driver for driver in drivers if "ODBC Driver" in driver and "18" not in driver]
        if older_versions:
            print(f"Older ODBC Drivers detected: {older_versions}")
            print("Uninstalling older ODBC Drivers...")
            for driver in older_versions:
                uninstall_odbc_driver(driver)

        # If ODBC Driver 18 is not installed, download and install it
        print("ODBC Driver 18 for SQL Server not found. Downloading and installing...")

        # URL for the ODBC Driver 18 for SQL Server installer (64-bit)
        driver_url = "https://go.microsoft.com/fwlink/?linkid=2307162"  # Direct link to the installer
        installer_path = os.path.join(os.getcwd(), "msodbcsql.msi")

        # Download the installer
        print(f"Downloading ODBC Driver installer from {driver_url}...")
        urllib.request.urlretrieve(driver_url, installer_path)
        print(f"Downloaded installer to {installer_path}")

        # Verify the installer file exists and is not empty
        if not os.path.exists(installer_path) or os.path.getsize(installer_path) == 0:
            print("Downloaded installer is invalid or empty.")
            return False

        # Run the installer
        print("Running the installer...")
        result = subprocess.run(
            ["msiexec", "/i", installer_path, "/quiet", "/norestart"],
            check=False,
            capture_output=True,
            text=True
        )

        # Check the result of the installation
        if result.returncode != 0:
            print(f"Installer failed with return code {result.returncode}")
            print(f"Installer stdout: {result.stdout}")
            print(f"Installer stderr: {result.stderr}")
            return False

        print("ODBC Driver 18 for SQL Server installed successfully.")

        # Clean up the installer file
        os.remove(installer_path)
        print("Installer file deleted.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error during ODBC Driver installation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def uninstall_odbc_driver(driver_name):
    """
    Uninstall the specified ODBC driver using the Windows registry and msiexec.
    """
    try:
        print(f"Attempting to uninstall {driver_name}...")
        # Use the Windows registry to find the uninstall string for the driver
        uninstall_command = f"msiexec /x {driver_name} /quiet /norestart"
        result = subprocess.run(
            uninstall_command,
            check=False,
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0:
            print(f"Failed to uninstall {driver_name}. Return code: {result.returncode}")
            print(f"Uninstall stdout: {result.stdout}")
            print(f"Uninstall stderr: {result.stderr}")
        else:
            print(f"Successfully uninstalled {driver_name}.")
    except Exception as e:
        print(f"Error uninstalling {driver_name}: {e}")