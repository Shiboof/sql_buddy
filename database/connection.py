import pyodbc

# SQL Server connection 
def get_connection(server, database, username, password):
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        connection = pyodbc.connect(connection_string)
        return connection
    except pyodbc.Error as e:
        error_message = f"Error connecting to the database: {e}"
        print(error_message)
        raise Exception(error_message)

# PostgreSQL connection

# import psycopg2

# def get_connection(server, username, password):
#     try:
#         connection = psycopg2.connect(
#             host=server,
#             user=username,
#             password=password
#         )
#         return connection
#     except psycopg2.Error as e:
#         print(f"Error connecting to PostgreSQL: {e}")
#         raise