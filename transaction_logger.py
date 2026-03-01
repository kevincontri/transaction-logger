import argparse
import json
import os
import uuid
from datetime import datetime


class Transaction:

    def __init__(self, amount, category, transaction_type):
        self.id = str(uuid.uuid4())
        self.amount = amount
        self.category = category
        self.type = transaction_type
        self.timestamp = datetime.now().isoformat()

    def to_dict(self):
        """Converts a transaction into a dictionary."""
        return {
            "id": self.id,
            "amount": self.amount,
            "category": self.category,
            "type": self.type,
            "timestamp": self.timestamp
        }

    @classmethod
    def from_dict(cls, data):
        """Converts a JSON dict into a Transaction object."""
        obj = cls(
            amount=data["amount"],
            category=data["category"],
            transaction_type=data["type"],
        )
        obj.id = data["id"]
        obj.timestamp = data["timestamp"]
        return obj

    def __str__(self):
        return f"Transaction info:\nID: {self.id}\nAmount: ${self.amount}\nCategory: {self.category.capitalize()}\nType: {self.type.capitalize()}\n"


class Ledger:
    """Represents a named transaction ledger with persistent JSON storage."""

    def __init__(self, name):
        self.name = name
        self.filename = f"{self.name.lower()}_transactions.json"
        self.transactions = []

        if os.path.exists(self.filename):
            self.load_from_file()

    def __str__(self):
        return f"\n{self.name.capitalize()} Ledger\n"

    def add_transaction(self, amount, category, transaction_type):
        """Creates a new transaction and adds it to the ledger's list of transactions."""
        transaction = Transaction(amount=amount, category=category,
                                  transaction_type=transaction_type)
        self.transactions.append(transaction)
        self._save_to_file()

    def _calculate_totals(self):
        """Compute total income and total expenses."""
        total_income = 0
        total_expenses = 0
        for transaction in self.transactions:
            if transaction.type == "expense":
                total_expenses += transaction.amount
            elif transaction.type == "income":
                total_income += transaction.amount
        return total_income, total_expenses

    def total_income(self):
        income, _ = self._calculate_totals()
        return income

    def total_expense(self):
        _, expenses = self._calculate_totals()
        return expenses

    def balance(self):
        income, expenses = self._calculate_totals()
        return income - expenses

    def get_category_totals(self, category=None):
        """Calculates the total amount (expense and income) of a transaction's category."""
        income = 0
        expense = 0
        found = False
        for transaction in self.transactions:
            if transaction.category == category:
                found = True
                if transaction.type == "income":
                    income += transaction.amount
                elif transaction.type == "expense":
                    expense += transaction.amount

        if not found:
            return None

        return income, expense

    def report(self):
        """Reports all transactions from a ledger, including its index and totals."""
        content = f"{self}\n"
        for index, transaction in enumerate(self.transactions):
            content += f"Index: {index + 1}\n" + f"{transaction}" + "\n"

        content += f"Total income: ${self.total_income()}\n"
        content += f"Total expense: ${self.total_expense()}\n"
        content += f"Total balance: ${self.balance()}\n"

        return content

    def _save_to_file(self):
        """Saves all transactions from transactions list into a JSON file."""
        data = [t.to_dict() for t in self.transactions]
        with open(self.filename, "w") as file:
            json.dump(data, file, indent=4)

    def load_from_file(self):
        """Load transactions from JSON file into memory."""
        self.transactions = []
        with open(self.filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(".json file might be corrupted, starting with empty ledger.")
                return
        for item in data:
            transaction = Transaction.from_dict(item)
            self.transactions.append(transaction)

    def delete_transaction(self, index):
        """Deletes a specified transaction from the ledger based on its index."""
        if index < 1 or index > len(self.transactions):
            return None
        else:
            try:
                removed = self.transactions.pop(index - 1)
                self._save_to_file()
                return removed
            except IndexError:
                return None

    def edit_transaction(self, index, amount=None, category=None, transaction_type=None):
        """Edits a transaction amount/category/type based on its index."""
        if amount is not None:
            self.transactions[index - 1].amount = amount

        if category is not None:
            self.transactions[index - 1].category = category

        if transaction_type is not None:
            self.transactions[index - 1].type = transaction_type

        self._save_to_file()

        return True


def cli():
    """Entry point for CLI command parsing and execution."""
    parser = argparse.ArgumentParser(description='Transaction Logger')
    subparsers = parser.add_subparsers(dest='command', required=True)

    # Add command
    parser_add = subparsers.add_parser("add", help="Add a new transaction")
    parser_add.add_argument("ledger_name", type=str, help="Name of the ledger")
    parser_add.add_argument("-a", "--amount", type=float, required=True, help="Amount to be added")
    parser_add.add_argument("-c", "--category", type=str,
                            required=True, help="Category to be added")
    parser_add.add_argument("-t", "--transaction_type",
                            choices=["income", "expense"], type=str, required=True, help="Transaction type to be added")

    # Report command
    parser_report = subparsers.add_parser("report", help="Report ledger transactions")
    parser_report.add_argument("ledger_name", type=str, help="Name of the ledger")

    # Report-Category command
    parser_category = subparsers.add_parser(
        "report-category", help="Report ledger transactions by category")
    parser_category.add_argument("ledger_name", type=str, help="Name of the ledger")
    parser_category.add_argument("category", type=str, help="Category to be reported")

    # Delete command
    parser_delete = subparsers.add_parser("delete", help="Delete a transaction by index")
    parser_delete.add_argument("ledger_name", help="Name of the ledger")
    parser_delete.add_argument("index", type=int, help="Index to be deleted")

    parser_edit = subparsers.add_parser("edit", help="Edit a transaction")
    parser_edit.add_argument("ledger_name", type=str, help="Name of the ledger")
    parser_edit.add_argument("index", type=int, help="Index of transaction to be edited")
    parser_edit.add_argument("-a", "--amount", type=float, help="Edit amount")
    parser_edit.add_argument("-c", "--category", type=str, help="Edit category")
    parser_edit.add_argument("-t", "--transaction_type",
                             choices=["expense", "income"], type=str, help="Edit type")

    args = parser.parse_args()

    ledger = Ledger(args.ledger_name)

    if args.command == "add":
        if args.amount < 0:
            print("Amount cannot be negative.")
            return

        ledger.add_transaction(args.amount, args.category, args.transaction_type)
        print("Transaction added.")

    elif args.command == "report":
        print(ledger.report())

    elif args.command == "report-category":
        result = ledger.get_category_totals(args.category)
        if result:
            income, expense = result
            print(
                f"Category: {args.category.capitalize()}\nTotal income: ${income}\nTotal expense: ${expense}")
        else:
            print(f"Category {args.category.capitalize()} not found.")

    elif args.command == "delete":
        removed = ledger.delete_transaction(args.index)
        if removed:
            print(f"Transaction at index {args.index} deleted.")
        else:
            print(f"Transaction at index {args.index} not found.")

    elif args.command == "edit":
        if args.amount is None and args.category is None and args.transaction_type is None:
            print("No fields provided.")
            return
        if not ledger.transactions:
            print("No transactions found.")
            return
        if args.amount is not None and args.amount < 0:
            print("Amount cannot be negative.")
            return
        if args.index < 1 or args.index > len(ledger.transactions):
            print(f"Index {args.index} out of range.")
            return

        edited = ledger.edit_transaction(
            args.index, args.amount, args.category, args.transaction_type)

        if edited:
            print(f"Transaction at index {args.index} edited.")


if __name__ == "__main__":
    cli()
