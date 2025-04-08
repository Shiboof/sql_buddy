class Owner:
    def __init__(self, serial_number=None, user_id=None):
        self.serial_number = serial_number
        self.user_id = user_id

    def find_user_and_lockboxes(self, connection):
        """
        Queries the database to:
        1. If input is a serial_number:
            - Query Lockbox_Current to find the associated user_id.
            - Query Lockbox_Current to find all serial_numbers associated with that user_id.
            - Query dbo.[User] to find first_name, last_name, and license_number using the user_id.
        2. If input is a user_id:
            - Query dbo.[User] to find first_name, last_name, and license_number.
            - Query Lockbox_Current to find all serial_numbers associated with that user_id.
        3. Return first_name, last_name, license_number, and all associated serial_numbers.
        """
        cursor = connection.cursor()

        # Query to find the user_id from Lockbox_Current using serial_number
        query_user_id_from_serial = """
            SELECT lc.user_id
            FROM dbo.Lockbox_Current lc
            WHERE lc.serial_number = ?
        """

        # Query to find all serial_numbers associated with a user_id
        query_serial_numbers_from_user_id = """
            SELECT STRING_AGG(lc.serial_number, ', ')
            FROM dbo.Lockbox_Current lc
            WHERE lc.user_id = ?
        """

        # Query to retrieve user details from dbo.[User]
        query_user_details = """
            SELECT u.first_name, u.last_name, u.license_number
            FROM dbo.[User] u
            WHERE u.user_id = ?
        """

        try:
            # Step 1: Determine if input is a serial_number or user_id
            if self.serial_number:
                # Input is a serial_number
                cursor.execute(query_user_id_from_serial, (self.serial_number,))
                user_id_result = cursor.fetchone()

                if not user_id_result or user_id_result[0] is None:
                    return f"No user found for lockbox {self.serial_number}."

                self.user_id = user_id_result[0]

            if not self.user_id:
                return "Please provide a valid user_id or serial_number."

            # Step 2: Retrieve user details from dbo.[User]
            cursor.execute(query_user_details, (self.user_id,))
            user_details = cursor.fetchone()

            if not user_details:
                return f"No user details found for user_id {self.user_id}."

            first_name, last_name, license_number = user_details

            # Step 3: Retrieve all serial_numbers associated with the user_id
            cursor.execute(query_serial_numbers_from_user_id, (self.user_id,))
            serial_numbers_result = cursor.fetchone()

            if not serial_numbers_result or serial_numbers_result[0] is None:
                return f"No lockboxes found for user_id {self.user_id}."

            serial_numbers = serial_numbers_result[0]

            # Return the user details and associated serial_numbers
            return (
                f"User ID: {self.user_id}\n"
                f"Name: {first_name} {last_name}\n"
                f"License Number: {license_number}\n"
                f"Associated Serial Numbers: {serial_numbers}"
            )
        finally:
            cursor.close()