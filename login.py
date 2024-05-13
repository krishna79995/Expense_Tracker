import streamlit as st
from expense import Expense
import mysql.connector
from datetime import datetime
import plotly.graph_objs as go 
import pandas as pd

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

# Function to create a table for groups
def create_group_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS group1
                     (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255) UNIQUE)''')
        conn.commit()
    except mysql.connector.Error as e:
        print(e)

# Function to create a table for group members
def create_group_members_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS group_members
                     (id INT AUTO_INCREMENT PRIMARY KEY, group_id INT, name VARCHAR(255),
                     FOREIGN KEY (group_id) REFERENCES group1(id))''')
        conn.commit()
    except mysql.connector.Error as e:
        print(e)

# Function to create a table for expenses
def create_expense_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expenses
                     (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255),
                     amount DECIMAL(10, 2), expense_date DATE, group_id INT,
                     FOREIGN KEY (group_id) REFERENCES group1(id))''')
        conn.commit()
    except mysql.connector.Error as e:
        print(e)

# Function to create a table for expense shares
def create_expense_shares_table(conn):
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS expense_shares
                     (id INT AUTO_INCREMENT PRIMARY KEY, expense_id INT, name VARCHAR(255),
                     share_amount DECIMAL(10, 2), FOREIGN KEY (expense_id) REFERENCES expenses(id))''')
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


def add_group(conn, group_name):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO group1 (name) VALUES (%s)", (group_name,))
        conn.commit()
        st.success("Group added successfully!")
    except mysql.connector.IntegrityError:
        st.error("Group name already exists. Please choose a different one.")
    except mysql.connector.Error as e:
        print(e)

# Function to add a new member to a group
def add_group_member(conn, group_id, username):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO group_members (group_id, name) VALUES (%s, %s)", (group_id, username))
        conn.commit()
        st.success("Member added to group successfully!")
    except mysql.connector.IntegrityError:
        st.error("Member already exists in the group.")
    except mysql.connector.Error as e:
        print(e)

def get_groups(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT id, name FROM group1")
        groups = c.fetchall()
        return {group[1]: group[0] for group in groups}
    except mysql.connector.Error as e:
        print(e)
        return {}
    

    
def get_group_members(conn, group_id):
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM group_members WHERE group_id = %s", (group_id,))
        members = c.fetchall()
        return [member[0] for member in members]
    except mysql.connector.Error as e:
        print(e)
        return []

def get_all_users(conn):
    try:
        c = conn.cursor()
        c.execute("SELECT username FROM users")
        users = c.fetchall()
        return [user[0] for user in users]
    except mysql.connector.Error as e:
        print(e)
        return []

def get_group_id_by_name(conn, group_name):
    try:
        c = conn.cursor()
        c.execute("SELECT id FROM group1 WHERE name = %s", (group_name,))
        group_id = c.fetchone()
        if group_id:
            return group_id[0]
        else:
            return None
    except mysql.connector.Error as e:
        print(e)
        return None

def get_user_id_by_username(username, users):
    for user in users:
        if user == username:
            return user
    return None


# Function to add a new expense
def add_expense(conn, expense_name, amount, expense_date, group_id):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO expenses (name, amount, expense_date, group_id) VALUES (%s, %s, %s, %s)",
                  (expense_name, amount, expense_date, group_id))
        conn.commit()
        st.success("Expense added successfully!")
    except mysql.connector.Error as e:
        print(e)

# Function to add expense shares
def add_expense_share(conn, username, share_amount):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO expense_shares ( name, share_amount) VALUES (%s, %s)",
                  (username, share_amount))
        conn.commit()
        st.success("Expense share added successfully!")
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

def main_menu(conn, username):
    st.title("Menu")
    menu_options = ["Expense Tracker", "Group Expense Tracker"]
    choice = st.selectbox("Select Option", menu_options)
    if choice =="Expense Tracker":
        expense_tracker(conn, username)
    elif choice=="Group Expense Tracker":
        group_expense_tracker(conn,username)

def expense_tracker(conn, username):
    st.title("Expense Tracker")

    expense_name = st.text_input("Where did you spend?")

    expense_amount = st.number_input("Enter total amount")

    expense_categories = ["Food 🍕", "Home 🏠", "Work 💼", "Fun 🎉", "Misc ✨"]
    selected_index = st.selectbox("Select the category", expense_categories)

    expense_date = st.date_input("Select expense date", datetime.now())

    if st.button("Save Expense"):
        username = st.experimental_get_query_params().get("username", [""])[0]   
        new_expense = Expense(name=expense_name, category=selected_index, amount=expense_amount, date=expense_date)
        save_expense(conn, new_expense, username)

        # Display menu after adding expense
    menu = ["Summarize by type", "Summarize by Date", "Total Expense", "View Expenses","View graph"]
    choice = st.selectbox("Menu", menu)

    if choice == "Summarize by type":
            summarize_expenses_by_category(conn, username)
    elif choice == "Summarize by Date":
            summarize_expenses_by_date(conn, username)
    elif choice == "Total Expense":
            display_total_expense(conn, username)
    elif choice == "View Expenses":
            display_expenses(conn, username)
    elif choice == "View graph":
            plot_daily_expenses(conn, username)

def group_expense_tracker(conn, username):
    conn = create_connection()  # Create a connection to the database

    st.title("Group Expense Tracker")
    st.subheader("Create a New Group")

    group_name = st.text_input("Enter Group Name:")
    if st.button("Create Group"):
        if group_name:
            add_group(conn, group_name)
            st.success("Group added successfully!")
        else:
            st.warning("Please enter a group name.")

    st.subheader("Add Members to Group")
    users = get_all_users(conn)
    user_usernames = [user for user in users]

    selected_members = st.multiselect("Select Members to Add:", user_usernames)

    if st.button("Add Selected Members"):
        group_id = get_group_id_by_name(conn, group_name)
        if group_id:
            for member in selected_members:
                user_id = get_user_id_by_username(member, users)
                add_group_member(conn, group_id, user_id)
            st.success("Members added to group successfully!")
        else:
            st.error("Error: Group not found.")

    st.subheader("Add Expense to Group")
    
    selected_expense_name = st.text_input("Enter Expense Name:")

    groups = get_groups(conn)
    group_names = list(groups.keys())

    selected_group_name = st.selectbox("Select Group:", group_names)

    selected_group_id = groups[selected_group_name]

    expense_amount = st.number_input("Enter Expense Amount:")
    expense_date = st.date_input("Select Expense Date", datetime.now())

    if st.button("Save Expense to Group"):
        num_group_members = len(get_group_members(conn, selected_group_id))
        if num_group_members == 0:
            st.warning("Please add members to the group before saving an expense.")
        else:
            share_amount = expense_amount / num_group_members
            for member in get_group_members(conn, selected_group_id):
                add_expense_share(conn, member, share_amount)

            add_expense(conn, selected_expense_name, expense_amount, expense_date, selected_group_id)
            st.success("Expense added to group successfully!")
    else:
        st.warning("Please fill in all fields.")


def save_expense(conn, expense, username):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO expenses (name, category, amount, username, expense_date) VALUES (%s, %s, %s, %s, %s)",
                  (expense.name, expense.category, expense.amount, username, expense.date))
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

def summarize_expenses_by_date(conn, username):
    try:
        c = conn.cursor()
        c.execute("SELECT expense_date, SUM(amount) AS total_amount FROM expenses WHERE username = %s GROUP BY expense_date", (username,))
        expenses_summary = c.fetchall()
        st.subheader("Expenses Summary by Date")
        for expense_date, total_amount in expenses_summary:
            st.write(f"Date: {expense_date}, Total Amount: {total_amount}")
    except mysql.connector.Error as e:
        st.error("Error occurred while summarizing expenses by date")
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

def display_expenses(conn, username):
    try:
        c = conn.cursor()
        c.execute("SELECT id, name, category, amount, expense_date FROM expenses WHERE username = %s", (username,))
        expenses = c.fetchall()
        if expenses:
            st.subheader("All Expenses")
            # Create an empty DataFrame to store the expenses
            df = pd.DataFrame(expenses, columns=["ID", "Name", "Category", "Amount", "Date"])
            # Add a new column for checkboxes
            df["Select"] = [st.checkbox(f"Select Expense {expense[0]}") for expense in expenses]
            # Display the DataFrame with checkboxes
            st.write(df)
            # Add a button to delete the selected expenses
            if st.button("Delete Selected Expenses"):
                # Get the IDs of the selected expenses
                selected_ids = df[df["Select"]]["ID"].tolist()
                # Delete the selected expenses
                for expense_id in selected_ids:
                    delete_expense(conn, expense_id)
                st.success("Selected expenses deleted successfully!")
        else:
            st.write("No expenses found.")
    except mysql.connector.Error as e:
        st.error("Error occurred while fetching expenses")
        print(e)

def delete_expense(conn, expense_id):
    try:
        c = conn.cursor()
        c.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
        conn.commit()
    except mysql.connector.Error as e:
        st.error("Error occurred while deleting the expense")
        print(e)


def plot_daily_expenses(conn, username):
    try:
        c = conn.cursor()
        c.execute("SELECT expense_date, SUM(amount) AS total_amount FROM expenses WHERE username = %s GROUP BY expense_date", (username,))
        expenses_summary = c.fetchall()
        
        # Extract dates and total amounts from query result
        dates = [row[0] for row in expenses_summary]
        total_amounts = [row[1] for row in expenses_summary]
        
        # Create a Plotly figure
        fig = go.Figure(data=go.Scatter(x=dates, y=total_amounts, mode='lines+markers'))
        fig.update_layout(title='Daily Expenses',
                          xaxis_title='Date',
                          yaxis_title='Total Amount')
        
        # Display the Plotly figure
        st.plotly_chart(fig)

    except mysql.connector.Error as e:
        st.error("Error occurred while fetching daily expenses")
        print(e)

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
                st.experimental_set_query_params(logged_in=True, username=username) 
            else:
                st.error("Incorrect username or password. Please try again.")

    elif choice == "Signup":
        st.sidebar.subheader("Create New Account")
        new_username = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type="password")
        confirm_password = st.sidebar.text_input("Confirm Password", type="password")
        if st.sidebar.button("Signup"):
            if new_password == confirm_password:
                insert_user(conn, new_username, new_password)
            else:
                st.error("Passwords do not match")

    if st.experimental_get_query_params().get("logged_in"): 
        username = st.experimental_get_query_params().get("username")[0]
        main_menu(conn, username)

if __name__ == '__main__':
    main()
