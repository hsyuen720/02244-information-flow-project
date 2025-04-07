from database import setup_database
from menu import menu

if __name__ == "__main__":
    setup_database()  # Initialize the database with tables and sample data
    menu()  # Start the interactive menu