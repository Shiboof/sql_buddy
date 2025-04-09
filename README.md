# Lockbox Locator

## Overview
The Lockbox Locator is a Python application that allows users to input a lockbox's serial number and queries an existing SQL database to find its location. This application is designed to streamline the process of locating lockboxes based on their unique serial numbers.

## Project Structure
```
lockbox-locator
├── src
│   ├── app.py                # Main entry point of the application
│   ├── database
│   │   └── connection.py     # Manages database connection
│   ├── models
│   │   └── lockbox.py        # Defines the Lockbox entity
|   |   └── owners.py         # Manages Owner class
|   |   └── ez_sql.py         # Manages ez_SQL function
│   └── utils
│       └── helpers.py        # Utility functions for the processing of csv's
|       └── driver_installer.py # Downloads ODBC Driver for SQL if not found
application
├── requirements.txt          # Lists project dependencies
└── README.md                 # Documentation for the project
└── version.json
```

## Setup Instructions
1. Clone the repository:
   ```
   git clone <repository-url>
   cd lockbox-locator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Configure your database connection in `src/database/connection.py`.

## Usage
1. Run the application:
   ```
   python src/app.py
   ```

2. When prompted, enter the lockbox's serial number.

3. The application will query the database and return the location of the lockbox.

## Functionality
- Input a lockbox's serial number.
- Query an SQL database to find the lockbox's location.
- Return the location to the user in a user-friendly format.

## Contributing
Contributions are welcome! Please submit a pull request or open an issue for any enhancements or bug fixes.