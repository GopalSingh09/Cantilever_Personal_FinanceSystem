import sys
import sqlite3
from PyQt5.QtWidgets import (QApplication, QMainWindow, QStackedWidget, QWidget, QVBoxLayout, QLabel, QPushButton,
                             QLineEdit, QFormLayout, QTableWidget, QTableWidgetItem, QComboBox, QMessageBox)
from PyQt5.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from datetime import datetime
import json
from PyQt5.QtWidgets import QFileDialog
import qdarkstyle

def setup_database():
    conn = sqlite3.connect('finance.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY,
        amount REAL,
        type TEXT,
        date TEXT
    )
    ''')
    conn.commit()
    conn.close()

# def add_sample_data():
#     conn = sqlite3.connect('finance.db')
#     cursor = conn.cursor()
#     cursor.execute("INSERT INTO transactions (amount, type, date) VALUES (500, 'income', '2024-01-15')")
#     cursor.execute("INSERT INTO transactions (amount, type, date) VALUES (200, 'expense', '2024-02-10')")
#     conn.commit()
#     conn.close()

class FinanceApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Personal Finance System")
        self.setGeometry(100, 100, 1000, 700)

        setup_database()
        # add_sample_data()

        self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)

        self.create_dashboard_screen()
        self.create_accounts_screen()
        self.create_transactions_screen()
        self.create_datafeed_screen()

        self.nav_buttons = QWidget()
        self.nav_layout = QVBoxLayout()
        self.nav_buttons.setLayout(self.nav_layout)
        self.layout.addWidget(self.nav_buttons)

        self.create_nav_buttons()

        self.stacked_widget.setCurrentWidget(self.dashboard_screen)

    def create_nav_buttons(self):
        nav_style = "QPushButton {background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 16px;} QPushButton:hover {background-color: #45a049;}"
        self.dashboard_button = QPushButton("Dashboard")
        self.dashboard_button.setStyleSheet(nav_style)
        self.dashboard_button.clicked.connect(self.show_dashboard)
        self.nav_layout.addWidget(self.dashboard_button)

        self.accounts_button = QPushButton("Accounts")
        self.accounts_button.setStyleSheet(nav_style)
        self.accounts_button.clicked.connect(self.show_accounts)
        self.nav_layout.addWidget(self.accounts_button)

        self.transactions_button = QPushButton("Transactions")
        self.transactions_button.setStyleSheet(nav_style)
        self.transactions_button.clicked.connect(self.show_transactions)
        self.nav_layout.addWidget(self.transactions_button)

        self.datafeed_button = QPushButton("Datafeed")
        self.datafeed_button.setStyleSheet(nav_style)
        self.datafeed_button.clicked.connect(self.show_datafeed)
        self.nav_layout.addWidget(self.datafeed_button)

    def create_dashboard_screen(self):
        self.dashboard_screen = QWidget()
        self.dashboard_layout = QVBoxLayout()
        self.dashboard_screen.setLayout(self.dashboard_layout)

        self.year_selector = QComboBox()
        self.year_selector.addItems([str(year) for year in range(datetime.now().year, datetime.now().year + 10)])
        self.year_selector.setStyleSheet("QComboBox {padding: 5px; font-size: 16px;} QComboBox::drop-down {border: none;}")  # Styling
        self.year_selector.currentIndexChanged.connect(self.update_dashboard)
        self.dashboard_layout.addWidget(self.year_selector)

        self.total_income_label = QLabel("Total Income: 0")
        self.total_income_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.dashboard_layout.addWidget(self.total_income_label)

        self.total_expense_label = QLabel("Total Expense: 0")
        self.total_expense_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.dashboard_layout.addWidget(self.total_expense_label)

        self.net_saving_label = QLabel("Net Saving: 0")
        self.net_saving_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.dashboard_layout.addWidget(self.net_saving_label)

        self.chart_widget = QWidget()
        self.dashboard_layout.addWidget(self.chart_widget)

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        chart_layout = QVBoxLayout()
        chart_layout.addWidget(self.canvas)
        self.chart_widget.setLayout(chart_layout)

        self.stacked_widget.addWidget(self.dashboard_screen)
        self.update_dashboard()

    def create_accounts_screen(self):
        self.accounts_screen = QWidget()
        self.accounts_layout = QVBoxLayout()
        self.accounts_screen.setLayout(self.accounts_layout)

        self.accounts_table = QTableWidget()
        self.accounts_table.setColumnCount(4)
        self.accounts_table.setHorizontalHeaderLabels(["ID", "Amount", "Type", "Date"])
        self.accounts_table.setStyleSheet("QTableWidget {font-size: 16px;} QTableWidget::item {padding: 5px;}")
        self.accounts_layout.addWidget(self.accounts_table)

        self.stacked_widget.addWidget(self.accounts_screen)
        self.update_accounts()

    def create_transactions_screen(self):
        self.transactions_screen = QWidget()
        self.transactions_layout = QFormLayout()
        self.transactions_screen.setLayout(self.transactions_layout)

        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet("padding: 5px; font-size: 16px;")
        self.transactions_layout.addRow("Amount:", self.amount_input)

        self.type_input = QComboBox()
        self.type_input.addItems(['income', 'expense'])
        self.type_input.setStyleSheet("padding: 5px; font-size: 16px;")
        self.transactions_layout.addRow("Type:", self.type_input)

        self.date_input = QLineEdit()
        self.date_input.setStyleSheet("padding: 5px; font-size: 16px;")
        self.transactions_layout.addRow("Date (YYYY-MM-DD):", self.date_input)

        self.add_button = QPushButton("Add Transaction")
        self.add_button.setStyleSheet("background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 16px;")
        self.add_button.clicked.connect(self.add_transaction)
        self.transactions_layout.addWidget(self.add_button)

        self.stacked_widget.addWidget(self.transactions_screen)

    def create_datafeed_screen(self):
        self.datafeed_screen = QWidget()
        self.datafeed_layout = QVBoxLayout()
        self.datafeed_screen.setLayout(self.datafeed_layout)

        self.datafeed_label = QLabel("Datafeed screen content here.")
        self.datafeed_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.datafeed_layout.addWidget(self.datafeed_label)

        self.stacked_widget.addWidget(self.datafeed_screen)

    def update_dashboard(self):
        year = self.year_selector.currentText()
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'income' AND strftime('%Y', date) = ?",
                       (year,))
        total_income = cursor.fetchone()[0] or 0
        cursor.execute("SELECT SUM(amount) FROM transactions WHERE type = 'expense' AND strftime('%Y', date) = ?",
                       (year,))
        total_expense = cursor.fetchone()[0] or 0
        net_saving = total_income - total_expense

        self.total_income_label.setText(f"Total Income: {total_income}")
        self.total_expense_label.setText(f"Total Expense: {total_expense}")
        self.net_saving_label.setText(f"Net Saving: {net_saving}")

        if total_income == 0 and total_expense == 0:
            QMessageBox.information(self, "No Data", f"No data found for the year {year}.")

        self.update_chart(total_income, total_expense)

        conn.close()

    def update_chart(self, total_income, total_expense):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        categories = ['Income', 'Expense']
        values = [total_income, total_expense]

        ax.bar(categories, values, color=['#4CAF50', '#F44336'])
        ax.set_xlabel('Category')
        ax.set_ylabel('Amount')
        ax.set_title('Income vs Expense')

        self.canvas.draw()

    def update_accounts(self):
        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM transactions")
        rows = cursor.fetchall()

        self.accounts_table.setRowCount(len(rows))
        for row_idx, row_data in enumerate(rows):
            for col_idx, col_data in enumerate(row_data):
                self.accounts_table.setItem(row_idx, col_idx, QTableWidgetItem(str(col_data)))

        conn.close()

    def add_transaction(self):
        amount = self.amount_input.text()
        trans_type = self.type_input.currentText()
        date = self.date_input.text()

        if not amount or not date:
            QMessageBox.warning(self, "Input Error", "Please fill all fields.")
            return

        try:
            float(amount)
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Amount should be a number.")
            return

        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO transactions (amount, type, date) VALUES (?, ?, ?)", (amount, trans_type, date))
        conn.commit()
        conn.close()

        self.amount_input.clear()
        self.date_input.clear()
        self.update_accounts()
        self.update_dashboard()
        QMessageBox.information(self, "Success", "Transaction added successfully.")

    def create_datafeed_screen(self):
        self.datafeed_screen = QWidget()
        self.datafeed_layout = QVBoxLayout()
        self.datafeed_screen.setLayout(self.datafeed_layout)

        self.upload_button = QPushButton("Upload JSON File")
        self.upload_button.setStyleSheet(
            "background-color: #4CAF50; color: white; border: none; padding: 10px; border-radius: 5px; font-size: 16px;")
        self.upload_button.clicked.connect(self.upload_json_file)
        self.datafeed_layout.addWidget(self.upload_button)

        self.status_label = QLabel("Upload a JSON file containing transactions.")
        self.status_label.setStyleSheet("font-size: 18px; padding: 10px;")
        self.datafeed_layout.addWidget(self.status_label)

        self.stacked_widget.addWidget(self.datafeed_screen)

    def upload_json_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Open JSON File", "", "JSON Files (*.json)")

        if file_name:
            try:
                with open(file_name, 'r') as file:
                    data = json.load(file)
                    self.process_json_data(data)
                    QMessageBox.information(self, "Success", "Transactions imported successfully.")
            except json.JSONDecodeError:
                QMessageBox.warning(self, "File Error", "Error decoding JSON file.")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def process_json_data(self, data):
        if not isinstance(data, list):
            QMessageBox.warning(self, "Data Error", "JSON data should be a list of transactions.")
            return

        conn = sqlite3.connect('finance.db')
        cursor = conn.cursor()

        for entry in data:
            amount = entry.get('amount')
            trans_type = entry.get('type')
            date = entry.get('date')

            if not amount or not trans_type or not date:
                continue

            try:
                float(amount)
            except ValueError:
                continue

            cursor.execute("INSERT INTO transactions (amount, type, date) VALUES (?, ?, ?)", (amount, trans_type, date))

        conn.commit()
        conn.close()

        self.update_accounts()
        self.update_dashboard()

    def show_dashboard(self):
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)

    def show_accounts(self):
        self.stacked_widget.setCurrentWidget(self.accounts_screen)

    def show_transactions(self):
        self.stacked_widget.setCurrentWidget(self.transactions_screen)

    def show_datafeed(self):
        self.stacked_widget.setCurrentWidget(self.datafeed_screen)

app = QApplication(sys.argv)
window = FinanceApp()
window.show()
sys.exit(app.exec_())
