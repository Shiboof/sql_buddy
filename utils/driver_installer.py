import os
import subprocess
import sys
import winreg

def check_and_install_odbc_driver():
    """
    Checks if ODBC Driver 18 for SQL Server is installed. If not, installs it from a local file.
    """
    try:
        # Check if any ODBC Driver for SQL Server is installed
        import pyodbc
        drivers = pyodbc.drivers()
        print(f"Installed ODBC Drivers: {drivers}")

        # Check for ODBC Driver 18
        if "ODBC Driver 18 for SQL Server" in drivers:
            print("ODBC Driver 18 for SQL Server is already installed.")
            return True

        # If ODBC Driver 18 is not installed, install it from the local file
        print("ODBC Driver 18 for SQL Server not found. Installing from local file...")

        # Determine the base directory
        if getattr(sys, 'frozen', False):  # If running as a PyInstaller bundle
            base_dir = sys._MEIPASS
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))

        # Path to the local installer
        installer_path = os.path.join(base_dir, "drivers", "msodbcsql.msi")
        print(f"Resolved installer path: {installer_path}")

        # Verify the installer file exists
        if not os.path.exists(installer_path):
            print(f"Installer file not found at {installer_path}.")
            return False

        # Run the installer
        log_path = os.path.join(os.getcwd(), "install.log")
        print(f"Running the installer from {installer_path}...")
        result = subprocess.run(
            f'msiexec /i "{installer_path}" /qf /norestart',
            check=False,
            capture_output=True,
            text=True,
            shell=True
        )


        # Check the result of the installation
        if result.returncode != 0:
            print(f"Installer failed with return code {result.returncode}")
            print(f"Installer stdout: {result.stdout}")
            print(f"Installer stderr: {result.stderr}")
            print(f"Check the log file for details: {log_path}")
            return False

        print("ODBC Driver 18 for SQL Server installed successfully.")
        return True
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def uninstall_odbc_driver(driver_name):
    """
    Uninstall the specified ODBC driver by finding its uninstall string in the Windows registry.
    """
    try:
        print(f"Attempting to uninstall {driver_name}...")

        # Registry paths to search for uninstall strings
        registry_paths = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]

        uninstall_string = None

        # Search the registry for the uninstall string
        for reg_path in registry_paths:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):  # Iterate through subkeys
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            try:
                                display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                if driver_name in display_name:
                                    uninstall_string = winreg.QueryValueEx(subkey, "UninstallString")[0]
                                    break
                            except FileNotFoundError:
                                continue
            except FileNotFoundError:
                continue

        if not uninstall_string:
            print(f"Uninstall string for {driver_name} not found in the registry.")
            return False

        # Run the uninstall command
        print(f"Uninstalling {driver_name} using: {uninstall_string}")
        result = subprocess.run(
            uninstall_string.split(),
            check=False,
            capture_output=True,
            text=True,
            shell=True
        )

        if result.returncode != 0:
            print(f"Failed to uninstall {driver_name}. Return code: {result.returncode}")
            print(f"Uninstall stdout: {result.stdout}")
            print(f"Uninstall stderr: {result.stderr}")
            return False
        else:
            print(f"Successfully uninstalled {driver_name}.")
            return True
    except Exception as e:
        print(f"Error uninstalling {driver_name}: {e}")
        return False