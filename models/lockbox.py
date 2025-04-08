class Lockbox:
    def __init__(self, serial_number, location=None):
        self.serial_number = serial_number
        self.location = location

    def find_location(self, connection):
        cursor = connection.cursor()
        # Query to join Inventory_History and qs_location on loc_code
        # PostgreSQL query
        # query = """
        #     SELECT q.loc_desc
        #     FROM "Inventory_History" ih
        #     INNER JOIN "qs_location" q ON ih.loc_code = q.loc_code
        #     WHERE ih.serial_number = %s
        # """

        #SQL Server query
        query = """
            SELECT q.loc_desc
            FROM dbo.Inventory_History ih
            INNER JOIN dbo.qs_location q ON ih.loc_code = q.loc_code
            WHERE ih.serial_number = ?
        """
        try:
            cursor.execute(query, (self.serial_number,))
            result = cursor.fetchone()
        finally:
            cursor.close()
        
        if result:
            self.location = result[0]  # loc_desc
            return self.location
        else:
            return None