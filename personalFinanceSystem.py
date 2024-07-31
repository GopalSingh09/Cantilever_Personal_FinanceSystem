import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import qdarkstyle
import ttkbootstrap as tb

# Database functions
def create_connection():
    return sqlite3.connect('finance.db')

def setup_database():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          name TEXT,
                          balance REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          amount REAL,
                          category TEXT,
                          date TEXT,
                          account_id INTEGER,
                          FOREIGN KEY (account_id) REFERENCES accounts(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          category TEXT,
                          budget_limit REAL,
                          spent REAL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS income (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          amount REAL,
                          date TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses (
                          id INTEGER PRIMARY KEY AUTOINCREMENT,
                          amount REAL,
                          date TEXT)''')

setup_database()
import tkinter as tk
from tkinter import ttk
import ttkbootstrap as tb
import sqlite3
from tkinter import messagebox
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


# Database connection setup
def create_connection():
    return sqlite3.connect("finance5.db")


def setup_database():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS accounts (
                          id INTEGER PRIMARY KEY,
                          name TEXT NOT NULL,
                          balance REAL NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
                          id INTEGER PRIMARY KEY,
                          account_id INTEGER,
                          amount REAL NOT NULL,
                          type TEXT NOT NULL,
                          date TEXT NOT NULL,
                          description TEXT,
                          FOREIGN KEY(account_id) REFERENCES accounts(id))''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS budgets (
                          id INTEGER PRIMARY KEY,
                          name TEXT NOT NULL,
                          budget_limit REAL NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS yearly_summary (
                          year INTEGER PRIMARY KEY,
                          income REAL NOT NULL,
                          expense REAL NOT NULL)''')
        conn.commit()

setup_database()


# Main application class
class FinanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Personal Finance System")
        self.geometry("1000x700")

        self.style = tb.Style()
        self.style.theme_use("darkly")

        self.navbar = ttk.Frame(self, padding="10 10 10 10")
        self.navbar.pack(side='left', fill='y')

        self.container = ttk.Frame(self, padding="10 10 10 10")
        self.container.pack(side='right', fill='both', expand=True)

        self.dashboard_button = ttk.Button(self.navbar, text="Dashboard", command=self.show_dashboard)
        self.dashboard_button.pack(fill='x', pady=5)

        self.accounts_button = ttk.Button(self.navbar, text="Accounts", command=self.show_accounts)
        self.accounts_button.pack(fill='x', pady=5)

        self.transactions_button = ttk.Button(self.navbar, text="Transactions", command=self.show_transactions)
        self.transactions_button.pack(fill='x', pady=5)


        self.datafeed_button = ttk.Button(self.navbar, text="Datafeed", command=self.show_datafeed)
        self.datafeed_button.pack(fill='x', pady=5)

        self.show_dashboard()

    def clear_screen(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_screen()
        dashboard_frame = ttk.Frame(self.container)
        dashboard_frame.pack(fill='both', expand=True)

        # Display dashboard content here
        label = ttk.Label(dashboard_frame, text="Dashboard", font=("Helvetica", 16))
        label.pack(pady=20)

        # Example chart (you can replace this with your actual chart)
        fig, ax = plt.subplots()
        ax.plot([1, 2, 3, 4], [10, 20, 25, 30], label='Example Data')
        ax.legend()

        canvas = FigureCanvasTkAgg(fig, master=dashboard_frame)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def show_accounts(self):
        self.clear_screen()
        accounts_frame = ttk.Frame(self.container)
        accounts_frame.pack(fill='both', expand=True)

        # Account list
        accounts_listbox = tk.Listbox(accounts_frame)
        accounts_listbox.pack(side='left', fill='y')

        self.load_accounts(accounts_listbox)

        accounts_listbox.bind("<<ListboxSelect>>", lambda event: self.on_account_select(event, accounts_frame))

        # Account details
        self.account_details_frame = ttk.Frame(accounts_frame)
        self.account_details_frame.pack(side='right', fill='both', expand=True)

        self.account_name_label = ttk.Label(self.account_details_frame, text="Account Name:",
                                            font=("Helvetica", 12, "bold"))
        self.account_name_label.pack(anchor='w')

        self.account_balance_label = ttk.Label(self.account_details_frame, text="Current Balance:",
                                               font=("Helvetica", 12, "bold"))
        self.account_balance_label.pack(anchor='w')

        self.spent_label = ttk.Label(self.account_details_frame, text="Spent Till Now:", font=("Helvetica", 12, "bold"))
        self.spent_label.pack(anchor='w')

        self.total_label = ttk.Label(self.account_details_frame, text="Total This Year:",
                                     font=("Helvetica", 12, "bold"))
        self.total_label.pack(anchor='w')

        self.transactions_listbox = tk.Listbox(self.account_details_frame)
        self.transactions_listbox.pack(fill='both', expand=True)

    def load_accounts(self, listbox):
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM accounts")
            accounts = cursor.fetchall()
            for account in accounts:
                listbox.insert(tk.END, account[1])

    def on_account_select(self, event, frame):
        selected_index = event.widget.curselection()
        if not selected_index:
            return

        selected_account_name = event.widget.get(selected_index)

        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, balance FROM accounts WHERE name = ?", (selected_account_name,))
            account = cursor.fetchone()
            if account:
                account_id, balance = account
                self.account_name_label.config(text=f"Account Name: {selected_account_name}")
                self.account_balance_label.config(text=f"Current Balance: {balance:.2f}")

                cursor.execute("SELECT SUM(amount) FROM transactions WHERE account_id = ? AND amount < 0",
                               (account_id,))
                spent = cursor.fetchone()[0] or 0.0
                self.spent_label.config(text=f"Spent Till Now: {abs(spent):.2f}")

                cursor.execute("SELECT SUM(amount) FROM transactions WHERE account_id = ? AND date LIKE ?",
                               (account_id, f"{datetime.now().year}%"))
                total = cursor.fetchone()[0] or 0.0
                self.total_label.config(text=f"Total This Year: {total:.2f}")

                cursor.execute("SELECT amount, category, date FROM transactions WHERE account_id = ?", (account_id,))
                transactions = cursor.fetchall()
                self.transactions_listbox.delete(0, tk.END)
                for transaction in transactions:
                    self.transactions_listbox.insert(tk.END, f"{transaction[0]} - {transaction[1]} - {transaction[2]}")

    def show_transactions(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        accounts_frame = ttk.Frame(self.container)
        accounts_frame.pack(fill="both", expand=True)

        accounts_listbox = tk.Listbox(accounts_frame, selectmode="single", font=("Arial", 12))
        accounts_listbox.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(accounts_frame, orient="vertical", command=accounts_listbox.yview)
        scrollbar.pack(side="right", fill="y")

        accounts_listbox.config(yscrollcommand=scrollbar.set)

        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM accounts")
            accounts = cursor.fetchall()

        for account in accounts:
            accounts_listbox.insert("end", account[1])

        def add_transaction():
            selected_index = accounts_listbox.curselection()
            if not selected_index:
                return

            account_id = accounts[selected_index[0]][0]

            try:
                amount = float(amount_entry.get())
                type_ = type_var.get()
                date = date_entry.get()
                description = description_entry.get()

                with create_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO transactions (account_id, amount, type, date, description) VALUES (?, ?, ?, ?, ?)",
                                   (account_id, amount, type_, date, description))
                    conn.commit()

                amount_entry.delete(0, "end")
                description_entry.delete(0, "end")

                messagebox.showinfo("Success", "Transaction added successfully")

            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")

        transaction_frame = ttk.Frame(self.container)
        transaction_frame.pack(fill="both", expand=True)

        amount_label = ttk.Label(transaction_frame, text="Amount:")
        amount_label.pack(pady=5)
        amount_entry = ttk.Entry(transaction_frame)
        amount_entry.pack(pady=5)

        type_label = ttk.Label(transaction_frame, text="Type:")
        type_label.pack(pady=5)
        type_var = tk.StringVar(value="income")
        income_rb = ttk.Radiobutton(transaction_frame, text="Income", variable=type_var, value="income")
        income_rb.pack(side="left", padx=5)
        expense_rb = ttk.Radiobutton(transaction_frame, text="Expense", variable=type_var, value="expense")
        expense_rb.pack(side="left", padx=5)

        date_label = ttk.Label(transaction_frame, text="Date:")
        date_label.pack(pady=5)
        date_entry = ttk.Entry(transaction_frame)
        date_entry.pack(pady=5)

        description_label = ttk.Label(transaction_frame, text="Description:")
        description_label.pack(pady=5)
        description_entry = ttk.Entry(transaction_frame)
        description_entry.pack(pady=5)

        add_button = ttk.Button(transaction_frame, text="Add Transaction", command=add_transaction)
        add_button.pack(pady=10)

        back_btn = ttk.Button(transaction_frame, text="Back to Transactions", command=self.show_transactions)
        back_btn.pack(pady=10)

    def show_datafeed(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        datafeed_frame = ttk.Frame(self.container)
        datafeed_frame.pack(fill="both", expand=True)

        # Dropdown menu for selecting the type of data to enter
        type_var = tk.StringVar(value="accounts")

        def show_data_form():
            for widget in datafeed_frame.winfo_children():
                widget.destroy()

            data_type = type_var.get()

            if data_type == "accounts":
                self.show_account_form(datafeed_frame)
            elif data_type == "transactions":
                self.show_transaction_form(datafeed_frame)
            elif data_type == "budgets":
                self.show_budget_form(datafeed_frame)

        type_label = ttk.Label(datafeed_frame, text="Select Data Type:")
        type_label.pack(pady=10)

        type_menu = ttk.OptionMenu(datafeed_frame, type_var, "accounts", "accounts", "transactions", "budgets",
                                   command=lambda x: show_data_form())
        type_menu.pack(pady=5)

        # Initial form display
        show_data_form()

    def show_account_form(self, parent_frame):
        account_frame = ttk.Frame(parent_frame)
        account_frame.pack(fill="both", expand=True)

        name_label = ttk.Label(account_frame, text="Account Name:")
        name_label.pack(pady=5)
        name_entry = ttk.Entry(account_frame)
        name_entry.pack(pady=5)

        balance_label = ttk.Label(account_frame, text="Initial Balance:")
        balance_label.pack(pady=5)
        balance_entry = ttk.Entry(account_frame)
        balance_entry.pack(pady=5)

        def add_account():
            name = name_entry.get()
            try:
                balance = float(balance_entry.get())
                with create_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO accounts (name, balance) VALUES (?, ?)", (name, balance))
                    conn.commit()
                name_entry.delete(0, "end")
                balance_entry.delete(0, "end")
                messagebox.showinfo("Success", "Account added successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid balance")

        add_button = ttk.Button(account_frame, text="Add Account", command=add_account)
        add_button.pack(pady=10)

    def show_transaction_form(self, parent_frame):
        transaction_frame = ttk.Frame(parent_frame)
        transaction_frame.pack(fill="both", expand=True)

        accounts_label = ttk.Label(transaction_frame, text="Select Account:")
        accounts_label.pack(pady=5)

        accounts_var = tk.StringVar()
        accounts_menu = ttk.Combobox(transaction_frame, textvariable=accounts_var)
        accounts_menu.pack(pady=5)

        # Fetch account names for dropdown
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM accounts")
            accounts = cursor.fetchall()

        accounts_menu['values'] = [account[0] for account in accounts]

        amount_label = ttk.Label(transaction_frame, text="Amount:")
        amount_label.pack(pady=5)
        amount_entry = ttk.Entry(transaction_frame)
        amount_entry.pack(pady=5)

        type_var = tk.StringVar(value="income")
        income_rb = ttk.Radiobutton(transaction_frame, text="Income", variable=type_var, value="income")
        income_rb.pack(side="left", padx=5)
        expense_rb = ttk.Radiobutton(transaction_frame, text="Expense", variable=type_var, value="expense")
        expense_rb.pack(side="left", padx=5)

        date_label = ttk.Label(transaction_frame, text="Date:")
        date_label.pack(pady=5)
        date_entry = ttk.Entry(transaction_frame)
        date_entry.pack(pady=5)

        description_label = ttk.Label(transaction_frame, text="Description:")
        description_label.pack(pady=5)
        description_entry = ttk.Entry(transaction_frame)
        description_entry.pack(pady=5)

        def add_transaction():
            selected_account = accounts_var.get()
            with create_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM accounts WHERE name = ?", (selected_account,))
                account_id = cursor.fetchone()
                if account_id:
                    account_id = account_id[0]
                    try:
                        amount = float(amount_entry.get())
                        type_ = type_var.get()
                        date = date_entry.get()
                        description = description_entry.get()

                        cursor.execute(
                            "INSERT INTO transactions (account_id, amount, type, date, description) VALUES (?, ?, ?, ?, ?)",
                            (account_id, amount, type_, date, description))
                        conn.commit()

                        amount_entry.delete(0, "end")
                        description_entry.delete(0, "end")
                        messagebox.showinfo("Success", "Transaction added successfully")
                    except ValueError:
                        messagebox.showerror("Error", "Please enter a valid amount")
                else:
                    messagebox.showerror("Error", "Invalid account selected")

        add_button = ttk.Button(transaction_frame, text="Add Transaction", command=add_transaction)
        add_button.pack(pady=10)

    def show_budget_form(self, parent_frame):
        budget_frame = ttk.Frame(parent_frame)
        budget_frame.pack(fill="both", expand=True)

        name_label = ttk.Label(budget_frame, text="Budget Name:")
        name_label.pack(pady=5)
        name_entry = ttk.Entry(budget_frame)
        name_entry.pack(pady=5)

        limit_label = ttk.Label(budget_frame, text="Budget Limit:")
        limit_label.pack(pady=5)
        limit_entry = ttk.Entry(budget_frame)
        limit_entry.pack(pady=5)

        def add_budget():
            name = name_entry.get()
            try:
                limit = float(limit_entry.get())
                with create_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO budgets (name, budget_limit) VALUES (?, ?)", (name, limit))
                    conn.commit()
                name_entry.delete(0, "end")
                limit_entry.delete(0, "end")
                messagebox.showinfo("Success", "Budget added successfully")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid limit")

        add_button = ttk.Button(budget_frame, text="Add Budget", command=add_budget)
        add_button.pack(pady=10)


app = FinanceApp()
app.mainloop()

