import customtkinter as ctk
from database.connection import get_connection
import database.db_config as db_config

def open_ez_sql_window(root):
    """Open the EZ-SQL window for dynamic query building."""
    ez_sql_window = ctk.CTkToplevel(root)
    ez_sql_window.title("EZ-SQL")
    ez_sql_window.geometry("800x600")

    # Labels
    ctk.CTkLabel(ez_sql_window, text="Select Table:", font=("Arial", 12)).grid(row=0, column=0, padx=10, pady=10, sticky="w")
    ctk.CTkLabel(ez_sql_window, text="Select Column:", font=("Arial", 12)).grid(row=1, column=0, padx=10, pady=10, sticky="w")
    ctk.CTkLabel(ez_sql_window, text="Filter by Column (Optional):", font=("Arial", 12)).grid(row=2, column=0, padx=10, pady=10, sticky="w")
    ctk.CTkLabel(ez_sql_window, text="Value for Filter (Optional):", font=("Arial", 12)).grid(row=3, column=0, padx=10, pady=10, sticky="w")
    
    # Dropdowns and input fields
    table_var = ctk.StringVar(ez_sql_window)
    column_var = ctk.StringVar(ez_sql_window)
    where_column_var = ctk.StringVar(ez_sql_window)
    where_value_var = ctk.StringVar(ez_sql_window)

    # Fetch tables dynamically
    tables = fetch_tables()
    if not tables:
        ctk.CTkLabel(ez_sql_window, text="No tables found in the database.", font=("Arial", 12), text_color="red").grid(row=0, column=1, padx=10, pady=10)
        return

    table_var.set(tables[0])  # Set default value
    ctk.CTkOptionMenu(ez_sql_window, variable=table_var, values=tables).grid(row=0, column=1, padx=10, pady=10)

    # Fetch columns for the selected table
    columns = fetch_columns(tables[0])
    column_var.set(columns[0])  # Set default value
    column_menu = ctk.CTkOptionMenu(ez_sql_window, variable=column_var, values=columns)
    column_menu.grid(row=1, column=1, padx=10, pady=10)

    # Dropdown for WHERE clause column
    where_column_var.set(columns[0])  # Set default value
    where_column_menu = ctk.CTkOptionMenu(ez_sql_window, variable=where_column_var, values=columns)
    where_column_menu.grid(row=2, column=1, padx=10, pady=10)

    # Input field for WHERE clause value
    ctk.CTkEntry(ez_sql_window, textvariable=where_value_var, font=("Arial", 12), width=300).grid(row=3, column=1, padx=10, pady=10)

    # Update columns when the table changes
    def update_columns(*args):
        selected_table = table_var.get()
        new_columns = fetch_columns(selected_table)
        column_var.set(new_columns[0])  # Update default column
        where_column_var.set(new_columns[0])  # Update default WHERE column
        column_menu.configure(values=new_columns)
        where_column_menu.configure(values=new_columns)

    table_var.trace("w", update_columns)

    # Text box for query results
    result_text = ctk.CTkTextbox(ez_sql_window, font=("Arial", 10), width=700, height=300)
    result_text.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

    # Execute query function
    def execute_query():
        table = table_var.get()
        column = column_var.get()
        where_column = where_column_var.get()
        where_value = where_value_var.get().strip()  # Strip whitespace

        # Construct the query
        query = f"SELECT {column} FROM {table}"
        params = []
        if where_value:  # Add WHERE clause only if a value is provided
            query += f" WHERE {where_column} = ?"
            params.append(where_value)

        try:
            connection = get_connection(
                db_config.server,
                db_config.database,
                db_config.username,
                db_config.password
            )
            cursor = connection.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            connection.close()

            # Display results
            result_text.delete("1.0", "end")
            if rows:
                for row in rows:
                    result_text.insert("end", f"{row}\n")
            else:
                result_text.insert("end", "No results found.")
        except Exception as e:
            result_text.delete("1.0", "end")
            result_text.insert("end", f"Error executing query: {e}")

    # Execute button
    ctk.CTkButton(ez_sql_window, text="Execute Query", command=execute_query, font=("Arial", 10), fg_color="#0078D7", text_color="white").grid(row=4, column=0, columnspan=2, pady=10)

    # Make the EZ-SQL window model
    ez_sql_window.grab_set()
    ez_sql_window.wait_window()

def fetch_tables():
    """Fetch the list of tables from the database."""
    try:
        connection = get_connection(
            db_config.server,
            db_config.database,
            db_config.username,
            db_config.password
        )
        cursor = connection.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = [row[0] for row in cursor.fetchall()]
        connection.close()
        return tables
    except Exception as e:
        print(f"Error fetching tables: {e}")
        return []

def fetch_columns(table_name):
    """Fetch the list of columns for a given table."""
    try:
        connection = get_connection(
            db_config.server,
            db_config.database,
            db_config.username,
            db_config.password
        )
        cursor = connection.cursor()
        query = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = ?"
        cursor.execute(query, (table_name,))
        columns = [row[0] for row in cursor.fetchall()]
        connection.close()
        return columns
    except Exception as e:
        print(f"Error fetching columns for table {table_name}: {e}")
        return []