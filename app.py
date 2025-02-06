import datetime
import os
import tkinter as tk
from tkinter import filedialog
import csv

root = tk.Tk()
root.withdraw()

def ensure_file_exists(file_path='data.txt'):
    """Check if the file exists, and create it if it doesn't."""
    try:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass  # Create an empty file
    except OSError as e:
        printEr(f"Error creating or checking file: {e}")
        return False
    return True

def select_csv_file():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    try:
        file_path = filedialog.askopenfilename(
            title="Select a CSV file",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        return file_path
    except Exception as e:
        printEr(f"Error opening file dialog: {e}")
        return None

# Process the CSV file
def process_csv(file_path):
    try:
        with open(file_path, 'r') as csvfile:
            csv_reader = csv.DictReader(csvfile, delimiter=';')
            rows = list(csv_reader)

            printSuccess("Processing CSV file...")
            for row in reversed(rows):
                date = row["Date"]
                debit_credit = row["Debit/credit"]
                amount = row["Amount (EUR)"]

                # Fixes date in correct format
                year = date[:4]
                month = date[4:6]
                day = date[6:]

                date = f"{day}:{month}:{year}"

                process_transaction(
                    date,
                    "income" if debit_credit.lower() == "credit" else "expense",
                    float(amount.replace(',', '.')),
                )
    except FileNotFoundError:
        printEr("CSV file not found.")
    except csv.Error as e:
        printEr(f"CSV parsing error: {e}")
    except ValueError:
        printEr("Invalid data in CSV file (e.g., non-numeric amount).")
    except Exception as e:
        printEr(f"Error processing CSV file: {e}")

def process_transaction(date, trans_type, amount, file_path='data.txt'):
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()

        if not lines:
            index = 1
            net_balance = 0
        else:
            last_line = lines[-1].strip()
            last_entry = last_line.split()
            index = int(last_entry[0]) + 1
            net_balance = float(last_entry[4])

        if trans_type.lower() == "income":
            net_balance += amount
        elif trans_type.lower() == "expense":
            net_balance -= amount
        else:
            printEr("Invalid transaction type. Use 'income' or 'expense'.")
            return

        if date.lower() == "today":
            date = datetime.datetime.now().strftime("%d:%m:%Y")

        new_line = f"{index} {date} {trans_type} {round(amount,2)} {round(net_balance, 2)}\n"

        with open(file_path, 'a') as f:
            f.write(new_line)

        printSuccess(f"Transaction added: {new_line.strip()}")

    except FileNotFoundError:
        printEr("Data file not found.")
    except ValueError:
        printEr("Invalid data in data file (e.g., non-numeric balance).")
    except Exception as e:
        printEr(f"Error processing transaction: {e}")

def process_report(report_type, date_input=None, file_path='data.txt'):
    try:
        if report_type.lower() == 'current':
            current_date = datetime.date.today()
            month = current_date.strftime("%B")
            year = current_date.year
        else:
            try:
                month, year = date_input.split()
                year = int(year)
                month = month.lower().capitalize()  # Make month case-insensitive
            except ValueError:
                printEr("Invalid format. Please enter Month and Year like 'January 2024'.")
                return

        month_year_str = f"{month} {year}"

        filtered_entries = []
        total_income = 0
        total_expenses = 0
        final_net_balance = 0
        net_balance = 0

        previous_month, previous_year = get_previous_month_year(month, year)
        if previous_month is None or previous_year is None:
            return  # Exit if there's an error getting previous month/year

        previous_month_year_str = f"{previous_month} {previous_year}"
        starting_balance = get_previous_month_balance(
            previous_month_year_str, file_path
        )
        net_balance = starting_balance

        with open(file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            parts = line.split()
            if len(parts) == 5:
                date = parts[1].strip()
                trans_type = parts[2].lower()
                amount = float(parts[3])

                try:
                    entry_date = datetime.datetime.strptime(date, "%d:%m:%Y").date()
                except ValueError:
                    printEr(f"Skipping invalid date format: {date}")
                    continue

                entry_month = entry_date.strftime("%B")
                entry_year = entry_date.year
                entry_month = entry_month.lower().capitalize()  # Standardize month name
                entry_month_year_str = f"{entry_month} {entry_year}"

                if entry_month_year_str != month_year_str:
                    continue

                if trans_type == "income":
                    total_income += amount
                    net_balance += amount
                elif trans_type == "expense":
                    total_expenses += amount
                    net_balance -= amount

                filtered_entries.append(
                    (
                        date,
                        trans_type,
                        "€" + str(amount),
                        "€" + str(round(net_balance, 2)),
                    )
                )
                final_net_balance = net_balance

        leftover_money = total_income - total_expenses
        savings = leftover_money * 0.50
        investments = leftover_money * 0.50

        print(f"\nReport for {month} {year}:\n")
        print(f"Starting Balance: €{starting_balance:.2f}")
        print("    Date    |   Type  | Amount |  NetBalance ")
        print("---------------------------------------------")
        for entry in filtered_entries:
            print(
                f" {entry[0]} | {entry[1].capitalize()}  | {entry[2]} | {entry[3]}"
            )
        print("---------------------------------------------")
        print(f"Total Income: €{total_income:.2f}")
        print(f"Total Expenses: €{total_expenses:.2f}")
        print(f"Leftover Money: €{leftover_money:.2f}")
        print(f"Savings: €{savings:.2f}")
        print(f"Investments: €{investments:.2f}")
        print(f"Final Net Balance: €{final_net_balance:.2f}\n")

    except FileNotFoundError:
        printEr("Data file not found.")
    except ValueError:
        printEr("Invalid data in data file (e.g., non-numeric balance).")
    except Exception as e:
        printEr(f"Error processing report: {e}")

def get_previous_month_year(month, year):
    try:
        month = month.lower().capitalize()  # Standardize month name
        month_number = datetime.datetime.strptime(month, "%B").month
        if month_number == 1:
            previous_month = "December"
            previous_year = year - 1
        else:
            previous_month_number = month_number - 1
            previous_month = datetime.datetime(
                year=year, month=previous_month_number, day=1
            ).strftime("%B")
            previous_year = year
        return previous_month, previous_year
    except ValueError as e:
        printEr(f"Invalid month format: {e}")
        return None, None

def get_previous_month_balance(previous_month_year_str, file_path='data.txt'):
    previous_balance = 0.0
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
            for line in reversed(lines):
                parts = line.split()
                if len(parts) == 5:
                    date = parts[1].strip()
                    try:
                        entry_date = datetime.datetime.strptime(date, "%d:%m:%Y").date()
                        entry_month = entry_date.strftime("%B")
                        entry_year = entry_date.year
                        entry_month = entry_month.lower().capitalize()  # Standardize month name
                        entry_month_year_str_file = f"{entry_month} {entry_year}"

                        if entry_month_year_str_file == previous_month_year_str:
                            return float(parts[4])
                    except ValueError:
                        continue
    except FileNotFoundError:
        printEr("Data file not found.")
    except Exception as e:
        printEr(f"Error getting previous month balance: {e}")
    return previous_balance

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
    if not ensure_file_exists():
        printEr("Failed to ensure data file exists. Exiting.")
        return

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