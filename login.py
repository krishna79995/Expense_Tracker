import streamlit as st
from expense import Expense
import mysql.connector

def create_connection():
    try:
       conn = mysql.connector.connect(host="localhost", user="root", password="root", database="expensedatabase")
       return conn
    except mysql.connector.Error as e:
        print(e)
        return None

def create_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (id INT AUTO_INCREMENT PRIMARY KEY, username VARCHAR(255) UNIQUE, password VARCHAR(255))''')
        conn.commit()
    except mysql.connector.Error as e:
        print(e)

def insert_user(conn, username, password):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()
        st.success("User registered successfully!")
    except mysql.connector.IntegrityError:
        st.error("Username already exists. Please choose a different one.")
    except mysql.connector.Error as e:
        print(e)

def authenticate_user(conn, username, password):
    try:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        result = c.fetchone()
        if result:
            return True
        else:
            return False
    except mysql.connector.Error as e:
        print(e)
        return False

def expense_tracker(conn):
    st.title("Expense Tracker")

    expense_name = st.text_input("Where did you spend?")

    expense_amount = st.number_input("Enter total amount")

    expense_categories = ["Food 🍕", "Home 🏠", "Work 💼", "Fun 🎉", "Misc ✨"]
    selected_index = st.selectbox("Select the category", expense_categories)

    if st.button("Save Expense"):
        username = st.query_params.get("username", ["username"])[""]
        new_expense = Expense(name=expense_name, category=selected_index, amount=expense_amount)
        save_expense(conn, new_expense, username)

def save_expense(conn, expense, username):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO expenses (name, category, amount, username) VALUES (%s, %s, %s, %s)",
                  (expense.name, expense.category, expense.amount, username))
        conn.commit()
        st.success("Expense saved successfully!")
    except mysql.connector.Error as e:
        st.error("Error occurred while saving the expense")
        print(e)

def summarize_expenses_by_category(conn, username):
    try:
        c = conn.cursor()
        c.execute("SELECT category, SUM(amount) AS total_amount FROM expenses WHERE username = %s GROUP BY category", (username,))
        expenses_summary = c.fetchall()
        st.subheader("Expenses Summary by Category")
        for category, total_amount in expenses_summary:
            st.write(f"Category: {category}, Total Amount: {total_amount}")
    except mysql.connector.Error as e:
        st.error("Error occurred while summarizing expenses")
        print(e)

def display_total_expense(conn, username):
    try:
        c = conn.cursor()
        c.execute("SELECT SUM(amount) AS total_amount FROM expenses WHERE username = %s", (username,))
        total_expense = c.fetchone()[0]
        st.subheader("Total Expense")
        st.write(f"Total Expense for {username}: {total_expense}")
    except mysql.connector.Error as e:
        st.error("Error occurred while calculating total expense")
        print(e)

def is_authenticated():
    return st.session_state.get("logged_in", False)
def main():
    conn = create_connection()
    create_table(conn)

    menu = ["Login", "Signup"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            if authenticate_user(conn, username, password):
                st.session_state.logged_in = True
                st.session_state.username = username
            else:
                st.error("Incorrect username or password. Please try again.")

    elif choice == "Signup":
        st.subheader("Create New Account")
        new_username = st.text_input("Username")
        new_password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        if st.button("Signup"):
            if new_password == confirm_password:
                insert_user(conn, new_username, new_password)
            else:
                st.error("Passwords do not match")

    if st.session_state.get("logged_in", False):
        expense_tracker(conn)
        username = st.session_state.username
        summarize_expenses_by_category(conn, username)
        display_total_expense(conn, username)

if __name__ == '__main__':
    main()

