import json
import argparse
import os
from tabulate import tabulate
import datetime
import sys

EXPENSE_FILE = "expense.json"

def load_expenses():
    if not os.path.exists(EXPENSE_FILE):
        return {"metadata": {"last_id": 0}, "expenses": []}
    
    try:
        with open(EXPENSE_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Error: The expense file is corrupted. Please check or delete 'expense.json' and try again.")
        sys.exit(1)

def save_expenses(data):
    with open(EXPENSE_FILE, 'w') as file:
        json.dump(data, file, indent=2)

def validate_id(data, id):
    if id <= 0 or id > data["metadata"]["last_id"]:
        print("Invalid id, Try again.")
        sys.exit(1)

def validate_description(description):
    if description.strip() == '':
        print("Description cannot be empty.")
        sys.exit(1)

def validate_amount(amount):
    if amount < 0:
        print("Amount cannot be negative.")
        sys.exit(1)

def validate_month(month):
    if month <= 0 or month > 12:
        print("Invalid month. Please provide a number between 1 and 12.")
        sys.exit(1)

def add_expense(description, amount):
    data = load_expenses()

    validate_description(description)
    validate_amount(amount)

    # Increment last_id
    data["metadata"]["last_id"] += 1
    new_id = data["metadata"]["last_id"]

    created_date = datetime.date.today()

    # Create new expense
    new_expense = {
        "id": new_id,
        "description": description,
        "amount": amount,
        "createdAt": created_date.strftime("%Y, %m, %d")
    }
    
    data["expenses"].append(new_expense)

    print(f"Expense added successfully (ID: {new_id})")
    save_expenses(data)

def update_expense(id, description, amount):
    data = load_expenses()

    validate_id(data, id)

    if description == "None" and amount == -1:
        print("Provide either a description or amount to update, or both.")
        sys.exit(1)
    
    if description != "None":
        validate_description(description)
    if amount != -1:
        validate_amount(amount)

    # Find and update the expense
    for expense in data["expenses"]:
        if expense["id"] == id:
            if description != "None":
                expense["description"] = description
            if amount != -1:
                expense["amount"] = amount
            break

    print("Expense updated successfully")
    save_expenses(data)

def delete_expense(id):
    data = load_expenses()

    validate_id(data, id)

    # Find and remove the expense
    for i, expense in enumerate(data["expenses"]):
        if expense["id"] == id:
            data["expenses"].pop(i)
            break

    print("Expense deleted successfully")
    save_expenses(data)

def list_expenses():
    data = load_expenses()

    if not data["expenses"]:
        print("No expenses found.")
        return

    table_data = []
    for expense in data["expenses"]:
        table_data.append([
            expense["id"], 
            expense["createdAt"], 
            expense["description"], 
            expense["amount"]
        ])

    headers = ["ID", "Date", "Description", "Amount"]
    print(tabulate(table_data, headers=headers, tablefmt="grid"))

def summary():
    data = load_expenses()
    
    if not data["expenses"]:
        print("No expenses found.")
        return
        
    total_spent = sum(expense["amount"] for expense in data["expenses"])
    print(f"Total expenses: ${total_spent}")

def monthly_summary(month):
    validate_month(month)

    # Convert month to string format
    month_str = f"{month:02d}"
    
    data = load_expenses()

    monthly_total = 0
    for expense in data["expenses"]:
        expense_month = expense["createdAt"][6:8]  # Extract month from date string
        if expense_month == month_str:
            monthly_total += expense["amount"]

    print(f"Summary for month: ${monthly_total}")

def parse_arguments():
    parser = argparse.ArgumentParser(prog="Expense Tracker")
    subparser = parser.add_subparsers(dest="command")

    # Add subcommand
    add_parser = subparser.add_parser("add", help="Add a new expense")
    add_parser.add_argument("--description", required=True, help="Description of expense")
    add_parser.add_argument("--amount", type=float, required=True, help="Amount spent")
    
    # Update subcommand
    update_parser = subparser.add_parser("update", help="Update the description or amount of an expense")
    update_parser.add_argument("--id", type=int, required=True, help="ID of expense to update")
    update_parser.add_argument("--description", default="None", required=False, help="Updated description of expense")
    update_parser.add_argument("--amount", default=-1, type=float, required=False, help="Updated amount spent")

    # Delete subcommand
    delete_parser = subparser.add_parser("delete", help="Delete an existing expense")
    delete_parser.add_argument("--id", type=int, required=True, help="ID of expense to delete")

    # List subcommand
    list_parser = subparser.add_parser("list", help="List all expenses")

    # Summary subcommand
    summary_parser = subparser.add_parser("summary", help="Summary of all expenses")
    summary_parser.add_argument("--month", type=int, default=-1, required=False, help="Month for summary (1-12)")

    return parser.parse_args()

def main():
    args = parse_arguments()

    if args.command == "add":
        add_expense(args.description, args.amount)
    elif args.command == "update":
        update_expense(args.id, args.description, args.amount)
    elif args.command == "delete":
        delete_expense(args.id)
    elif args.command == "list":
        list_expenses()
    elif args.command == "summary":
        if args.month == -1:
            summary()
        else:
            monthly_summary(args.month)

if __name__ == "__main__":
    main()