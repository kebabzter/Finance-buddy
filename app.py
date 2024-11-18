import datetime
import os
import tkinter as tk
from tkinter import filedialog
import csv

root = tk.Tk()
root.withdraw()

def ensure_file_exists(file_path='data.txt'):
    """Check if the file exists, and create it if it doesn't."""
    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            pass  # Create an empty file

def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select a CSV file",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )
    return file_path

# Process the CSV file
def process_csv(file_path):
    with open(file_path, 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter=';') 
        rows = list(csv_reader)

        printSuccess("Processing CSV file...")
        for row in reversed(rows):
            date = row["Date"]
            debit_credit = row["Debit/credit"]
            amount = row["Amount (EUR)"]

            #Fixes date in correct format
            year = date[:4] 
            month = date[4:6]  
            day = date[6:] 

            date = f"{day}:{month}:{year}"
            
            process_transaction(date, "income" if debit_credit.lower() == "credit" else "expense", float(amount.replace(',', '.')) )

def process_transaction(date, trans_type, amount, file_path='data.txt'):
    # Open the file and read the last line to get the current index and netbalance
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    # If the file is empty, set starting values for index and netbalance
    if not lines:
        index = 1
        net_balance = 0
    else:
        # Get the last line, split by spaces, and extract index and net_balance
        last_line = lines[-1].strip()
        last_entry = last_line.split()
        index = int(last_entry[0]) + 1  # Increment index for new entry
        net_balance = float(last_entry[4])  # Get the last netbalance value
    
    # Calculate the new net balance based on the transaction type
    if trans_type.lower() == "income":
        net_balance += amount
    elif trans_type.lower() == "expense":
        net_balance -= amount
    else:
        printEr("Invalid transaction type. Use 'income' or 'expense'.")
        return
    
    if date.lower() == "today":
        date = datetime.datetime.now().strftime("%d:%m:%Y");
    
    # Create the new line to be appended
    new_line = f"{index} {date} {trans_type} {round(amount,2)} {round(net_balance, 2)}\n"

    # Append the new transaction to the file
    with open(file_path, 'a') as f:
        f.write(new_line)
    
    printSuccess(f"Transaction added: {new_line.strip()}")

def process_report(report_type, date_input=None, file_path='data.txt'):
    # Read all lines from data.txt
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Parse the current date if 'Current' is chosen
    if report_type.lower() == 'current':
        current_date = datetime.date.today()  # Get today's date
        month = current_date.strftime("%B")  # Get the full month name
        year = current_date.year  # Get the current year
    else:
        # If it's Month and Year, use the provided date_input
        try:
            month, year = date_input.split()
            year = int(year)
        except ValueError:
            printEr("Invalid format. Please enter Month and Year like 'January 2024'.")
            return

    # Initialize variables for calculating investments and spending money
    filtered_entries = []
    final_net_balance = 0
    net_balance = 0
    for line in lines:
        # Split each line and extract the date and netbalance
        parts = line.split()
        if len(parts) == 5:
            date = parts[1].strip()  # Date in DD:MM:YYYY format, strip any extra spaces
            trans_type = parts[2].lower()  # Transaction type: income/expense
            amount = float(parts[3])  # Transaction amount

            try:
                # Parse the date with DD:MM:YYYY format
                entry_date = datetime.datetime.strptime(date, "%d:%m:%Y").date()
            except ValueError:
                printEr(f"Skipping invalid date format: {date}")
                continue

            entry_month = entry_date.strftime("%B")
            entry_year = entry_date.year

            if entry_month != month or entry_year != year:
                continue

            if trans_type == "income":
                net_balance += amount
            else:
                net_balance -= amount

            # Check if the entry matches the month and year

            if entry_month.lower() == month.lower() and entry_year == year:
                filtered_entries.append((date, trans_type, "€" + str(amount), "€" + str(round(net_balance, 2))))
                final_net_balance = net_balance

    # If there are no entries for the specified month/year, notify the user
    if not filtered_entries:
        printEr(f"No transactions found for {month} {year}.")
    
        return  # Exit the function if no transactions are found

    # Print table header
    print(f"\nReport for {month} {year}:\n")
    print("    Date    |   Type  | Amount |  NetBalance ")
    print("---------------------------------------------")

    # Display the filtered transactions in a table format
    for entry in filtered_entries:
        print(f" {entry[0]} | {entry[1].capitalize()}  | {entry[2]} | {entry[3]}")

    # Calculate and display Investments and Spending Money
    print()
    investments = final_net_balance * 0.50
    spending_money = final_net_balance * 0.50

    print("---------------------------------------------")
    print(f"Investments: {investments:.2f}  |  Spending Money: {spending_money:.2f}\n")

def printEr(err):
    dashes = '-' * len(err)

    print(f"\n\033[38;5;214m\033[1m{dashes}\033[0m")
    print(f"\033[38;5;214m\033[1m{err}\033[0m")
    print(f"\033[38;5;214m\033[1m{dashes}\033[0m\n")

def printSuccess(msg):
    dashes = '-' * len(msg)

    print(f"\n\033[32m\033[1m{dashes}\033[0m")
    print(f"\033[32m\033[1m{msg}\033[0m")
    print(f"\033[32m\033[1m{dashes}\033[0m\n")

def main():
    ensure_file_exists();
    print("Enter 'Input / I' to start entering transactions, 'Report / R' for reports 'Back / B' to go back once in entering mode, or 'Quit / Q' to exit.")
    while True:
        command = input("Enter command:").strip().lower()
        
        # Handle combinations of commands like 'r c' for 'report current'
        command_parts = command.split()
        
        if command_parts == ["q"] or command_parts == ["quit"]:
            print("Exiting the program.")
            break  # Exit the program if 'Quit' or 'Q' is typed
        
        elif "i" in command_parts or "input" in command_parts:
            # Check if shorthand 'i {date} {type} {amount}' is used
            if len(command_parts) == 4:
                try:
                    date = command_parts[1]  # Expected format: DD:MM:YYYY
                    trans_type = command_parts[2].lower()  # 'income' or 'expense's
                    amount = float(command_parts[3])  # Convert amount to integer
                    
                    process_transaction(date, trans_type, amount)
                except ValueError:
                    printEr("Invalid amount. Please enter a valid integer.")
            else:
                # If the long version ('Input') is typed, start interactive transaction input
                print("Now you can start entering transactions (type 'Back / B' to go back).")
                
                while True:
                    user_input = input("Enter transaction (DD:MM:YYYY Type Amount): ").strip()
                    
                    if user_input.lower() == "b" or user_input.lower() == "back":
                        print("Going back.")
                        break  # Stop reading input if 'Back' or 'B' is typed
                    
                    elif user_input.lower() == "quit":
                        print("Exiting the program.")
                        return  # Exit the program immediately if 'Quit' is typed

                    parts = user_input.split()
                    
                    if len(parts) == 3:
                        try:
                            date = parts[0]  # Expected format: DD:MM:YYYY
                            trans_type = parts[1].lower()  # 'income' or 'expense'
                            amount = float(parts[2])  # Ensure any extra spaces are removed and convert to integer

                            process_transaction(date, trans_type, amount)
                        except ValueError:
                            
                            printEr("Invalid amount. Please enter a valid number.")
                    else:
                        printEr("Invalid format. Please enter the transaction as: DD:MM:YYYY Type Amount")
        
        elif "r" in command_parts or "report" in command_parts:            
            # Check if the user entered a combination like 'r c'
            if "c" in command_parts or "current" in command_parts:
                process_report("current")  # Process the current month's report
            else:
                while True:
                    report_input = input("Enter Month and Year (e.g., 'January 2024') or 'Current / C': ").strip()
                    
                    if report_input.lower() == "b" or report_input.lower() == "back":
                        print("Going back.")
                        break  # Stop reading report input if 'Back' or 'B' is typed
                    
                    elif report_input.lower() == "quit":
                        print("Exiting the program.")
                        return  # Exit the program immediately if 'Quit' is typed
                    
                    elif report_input.lower() == "c" or report_input.lower() == "current":
                        process_report("current")  # Process the current month's report
                    else:
                        process_report("monthyear", report_input)  # Process the report for a specific month/year
        
        elif "ibs" in command_parts or "import" in command_parts:
            file_path = select_csv_file()
            if file_path:
                try:
                    process_csv(file_path)
                except Exception as e:
                    printEr(f"Error processing the file: {e}")
            else:
                printEr("No file selected.")

        else:
            printEr("Invalid command. Please enter 'Input / I', 'Report / R', 'Import / ibs' or 'Quit / Q'.")

if __name__ == "__main__":
    main()

