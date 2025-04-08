class Owner:
    def __init__(self, serial_number):
        self.serial_number = serial_number

    def find_owner(self, connection):
        """
        Queries the database to find the owner of a lockbox by serial number.
        """
        cursor = connection.cursor()

        # SQL Server query to find the user_id from dbo.lockbox_current
        query_user_id = """
            SELECT lc.user_id
            FROM dbo.lockbox_current lc
            WHERE lc.serial_number = ?
        """

        # SQL Server query to find the owner's details from dbo.User
        query_owner_details = """
            SELECT u.first_name, u.last_name, u.license_number
            FROM dbo.User u
            WHERE u.user_id = ?
        """

        try:
            # Step 1: Get the user_id from dbo.lockbox_current
            cursor.execute(query_user_id, (self.serial_number,))
            user_id_result = cursor.fetchone()

            if not user_id_result:
                return f"No owner found for lockbox {self.serial_number}."

            user_id = user_id_result[0]

            # Step 2: Get the owner's details from dbo.User
            cursor.execute(query_owner_details, (user_id,))
            owner_details = cursor.fetchone()

            if owner_details:
                first_name, last_name, license_number = owner_details
                return f"Owner: {first_name} {last_name}, License Number: {license_number}"
            else:
                return f"No owner details found for user_id {user_id}."
        finally:
            cursor.close()