class Owner:
    def __init__(self, serial_number=None, user_id=None):
        self.serial_number = serial_number
        self.user_id = user_id

    def find_user_and_lockboxes(self, connection):
        """
        Queries the database to:
        1. Find the user_id associated with the given serial_number in Lockbox_Current.
        2. Count how many serial_numbers are assigned to the user_id.
        3. Retrieve the first_name and last_name of the user from dbo.[User].
        4. Return the count, list of serial_numbers, and user details.
        """
        cursor = connection.cursor()

        # Query to find the user_id from Lockbox_Current
        query_user_id = """
            SELECT lc.user_id
            FROM dbo.Lockbox_Current lc
            WHERE lc.serial_number = ?
        """

        # Query to count serial_numbers and retrieve them for the user_id
        query_lockboxes = """
            SELECT COUNT(*), STRING_AGG(lc.serial_number, ', ')
            FROM dbo.Lockbox_Current lc
            WHERE lc.user_id = ?
        """

        # Query to retrieve user details from dbo.[User]
        query_user_details = """
            SELECT u.first_name, u.last_name
            FROM dbo.[User] u
            WHERE u.user_id = ?
        """

        try:
            # Step 1: Determine the user_id
            if self.serial_number:
                cursor.execute(query_user_id, (self.serial_number,))
                user_id_result = cursor.fetchone()

                if not user_id_result or user_id_result[0] is None:
                    return f"No user found for lockbox {self.serial_number}."

                self.user_id = user_id_result[0]

            if not self.user_id:
                return "Please provide a valid user_id or serial_number."

            # Step 2: Count serial_numbers and retrieve them for the user_id
            cursor.execute(query_lockboxes, (self.user_id,))
            lockbox_data = cursor.fetchone()

            if not lockbox_data or lockbox_data[0] == 0:
                return f"No lockboxes found for user_id {self.user_id}."

            lockbox_count, serial_numbers = lockbox_data

            # Step 3: Retrieve user details from dbo.[User]
            cursor.execute(query_user_details, (self.user_id,))
            user_details = cursor.fetchone()

            if not user_details:
                return f"No user details found for user_id {self.user_id}."

            first_name, last_name = user_details

            # Return the count, serial_numbers, and user details
            return (
                f"User ID: {self.user_id}\n"
                f"Name: {first_name} {last_name}\n"
                f"Lockboxes Count: {lockbox_count}\n"
                f"Serial Numbers: {serial_numbers}"
            )
        finally:
            cursor.close()