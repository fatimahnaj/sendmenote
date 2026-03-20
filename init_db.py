import sqlite3

def build_database():
    try:
        # Connect to the database, it will create the file if it is not yet exist
        connection = sqlite3.connect('database.db')
        
        # Open and read the SQL file
        with open('database.sql', 'r') as f:
            sql_script = f.read()
        
        # Execute the script
        connection.executescript(sql_script)
        
        connection.commit()
        connection.close()
        print("Successfully built the database and created tables!")
        
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    build_database()