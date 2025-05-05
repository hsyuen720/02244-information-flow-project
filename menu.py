from features import offer, search, purchase

def menu():
    print("Welcome to the Book Marketplace Prototype!")
    while True:
        try:
            print("\nPlease choose an action:")
            print("1. Offer a book (Vendor)")
            print("2. Search for books (Customer)")
            print("3. Purchase a book (Customer)")
            print("4. Exit")
            choice = input("Enter your choice (1-4): ")

            if choice == "1":
                vendor_id = input("Enter your vendor ID: ")
                title = input("Enter book title: ")
                author = input("Enter book author: ")
                year = input("Enter book year: ")
                edition = input("Enter book edition: ")
                publisher = input("Enter book publisher: ")
                condition = input("Enter book condition: ")
                description = input("Enter book description: ")
                price = input("Enter book price: ")
                book_details = {
                    "title": title, "author": author, "year": year, "edition": edition,
                    "publisher": publisher, "condition": condition, "description": description, "price": price
                }
                try:
                    result = offer(vendor_id, **book_details)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "2":
                customer_id = input("Enter your customer ID: ")
                search_field = input("Enter field to search (e.g., title, author): ")
                search_value = input(f"Enter value for {search_field}: ")
                search_query = {search_field: search_value}
                try:
                    results = search(customer_id, **search_query)
                    if not results:
                        print("No match found. Showing all available books:")
                        results = search(customer_id)  

                    for result in results:
                        print(result)

                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "3":
                customer_id = input("Enter your customer ID: ")
                offer_id = input("Enter the offer ID of the book to purchase: ")
                shipping_address = input("Enter your shipping address: ")
                try:
                    result = purchase(customer_id, offer_id, shipping_address)
                    print(result)
                except ValueError as e:
                    print(f"Error: {e}")

            elif choice == "4":
                print("Exiting the program.")
                break

            else:
                print("Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\nProgram interrupted by user. Exiting gracefully.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
