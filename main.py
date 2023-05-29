import mysql.connector
import re
import random
import hashlib
import getpass
import datetime
import string
from faker import Faker
import uuid
import requests

# Establish connection with MySQL database
db_host = "localhost"
db_username = "root"
db_password = "admin"
is_admin = False

try:
    db = mysql.connector.connect(host=db_host, user=db_username, password=db_password)
except Exception:
    print("There was an error connnecting to the database")
    exit

cursor = db.cursor()

# Create the funds_transfer_system database and accounts table if it doesn't exist
cursor.execute("CREATE DATABASE IF NOT EXISTS funds_transfer_system")
cursor.execute("use funds_transfer_system;")
cursor.execute(
    """
  CREATE TABLE IF NOT EXISTS accounts (
  account_number INT AUTO_INCREMENT PRIMARY KEY,
  balance FLOAT,
  username VARCHAR(255),
  email VARCHAR(255),
  phone_number VARCHAR(255),
  passkey VARCHAR(255)
  );
"""
)
cursor.execute(
    """
  CREATE TABLE IF NOT EXISTS ticket_management_system (
  ticket_id INT AUTO_INCREMENT PRIMARY KEY,
  ticket_type VARCHAR(255),
  ticket_description VARCHAR(255),
  ticket_status VARCHAR(255),
  ticket_date DATE,
  ticket_time TIME,
  );
"""
)


def generate_passkey(length=8):
    # Define characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a random passkey
    passkey = "".join(random.choice(characters) for _ in range(length))

    return passkey

def hash_passkey(passkey):
    
    hashed_passkey = hashlib.sha256(passkey.encode('utf-8')).hexdigest()
    return hashed_passkey

def verify_phone_number(phone_number):
    phone_number_pattern = r"^(?:\+?\d{1,3}\s?)?(?:\(\d{1,}\)|\d{1,})[-.\s/]?\d{1,}[-.\s/]?\d{1,}[-.\s/]?\d{1,}(?:\s?(?:x|ext)\d{1,})?$|^(\+\d{1,3})(\d{1,})$"
    if re.match(phone_number_pattern, phone_number):
        return True
    else:
        return False

def verify_email(email):
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(email_pattern, email):
        return True
    else:
        return False


def push_account(balance, username, email, phone_number, passkey, account_number=""):
    try:
        # encrypt the passkey
        # hashed_passkey = hash_passkey(passkey)

        # Check if the email id is valid
        if verify_email(email) and verify_phone_number(phone_number):
            hashed_passkey = hash_passkey(passkey)
            # Insert the new account into the accounts table
            if account_number != "":
                try:
                    cursor.execute(
                        "INSERT INTO accounts (account_number, balance, username, email, phone_number, passkey) VALUES (%s, %s, %s, %s, %s, %s)",
                        (account_number, balance, username, email, phone_number, hashed_passkey),
                    )
                except Exception as e:
                    print("Erorr inserting account. Same account_number exists in database")
            else:
                cursor.execute(
                    "INSERT INTO accounts ( balance, username, email, phone_number, passkey) VALUES (%s, %s, %s, %s, %s)",
                    (balance, username, email, phone_number, hashed_passkey),
                )

            db.commit()
            # Fetch the generated account number from the database

            table_username = f"transaction_history_{account_number}"

            # Create the user's transaction history table
            cursor.execute(
                f"""
                CREATE TABLE IF NOT EXISTS {table_username} (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    transaction_type VARCHAR(50),
                    amount float,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """
            )

            print("Account created successfully")
    except Exception:
        db.rollback()
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )


# def push_delete_account(account_number):
#     print("hello")
# def push_update_account(account_number):
# def push_display_balance(account_number):
# def push_update_balance(account_number)
# def delete_account(account_number):
# def reactivate_account()


def account_login():
    username = input("Enter your username: ")
    passkey = getpass.getpass("Enter your passkey: ")
    if username == db_username and passkey == db_password:
        is_admin = True
        print("You are logged in successfully as " + db_username)
    else:
        hashed_passkey = hash_passkey(passkey)
        cursor.execute(
            "SELECT * FROM users WHERE username = %s AND passkey = %s",
            (username, hashed_passkey),
        )
        user = cursor.fetchone()
        if user:
            print("Login successful!")
            # Perform further actions or return user data
        else:
            print("Invalid username or passkey.")
            # Handle unsuccessful login


# Function to create sample data for the accounts table
def generate_sample_data():
    try:
        num = int(input("Enter the number of sample entries you want to have: "))
        is_log = bool(
            int(
                input(
                    "Do you want to log the details of accounts being pushed? (1 for yes, 0 for no): "
                )
            )
        )
        fake = Faker("en_IN")

        for _ in range(num):
            balance = random.uniform(0, 1000) * 100
            username = fake.name()
            email = fake.email()
            phone_number = fake.phone_number()
            passkey = generate_passkey()
            # hashed_passkey = hash_passkey(passkey)
            # account_number = 5
            push_account(
                balance=balance,
                username=username,
                email=email,
                phone_number=phone_number,
                passkey=passkey,
            )

            if is_log:
                print(
                    f"Account details: {balance}, {username}, {email}, {phone_number}, {passkey}"
                )

        db.commit()

        print("Sample data for the main table added successfully")

    except Exception as e:
        db.rollback()
        print("An error has occurred:", str(e))


# Function to create a new account
def create_account():
    account_number = int(input("Enter account number: "))
    balance = float(input("Enter initial balance: "))
    username = input("Enter your name: ")
    email = "enter your email id: "
    phone_number = input("Enter your phone number:")
    passkey = getpass.getpass("Enter your passkey: ")

    push_account(account_number, balance, username, email, phone_number, passkey)


# Function to update account details
def update_account(account_number):
    try:
        # Retrieve existing account details
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number,)
        )
        account = cursor.fetchone()
        if account is None:
            print("Account not found")
            return

        print("Select the account details to update:")
        print("1. Balance")
        print("2. username")
        print("3. Email")
        print("4. Phone number")

        choice = int(input("Enter your choice: "))

        if choice == 1:
            balance = float(input("Enter new balance: "))
            cursor.execute(
                "UPDATE accounts SET balance = %s WHERE account_number = %s",
                (balance, account_number),
            )
        elif choice == 2:
            username = input("Enter new username: ")
            cursor.execute(
                "UPDATE accounts SET username = %s WHERE account_number = %s",
                (username, account_number),
            )
        elif choice == 3:
            email = input("Enter new email id: ")
            # Check if the email id is valid
            if not re.match(r"^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
                raise ValueError("Invalid email id")
            cursor.execute(
                "UPDATE accounts SET email = %s WHERE account_number = %s",
                (email, account_number),
            )
        elif choice == 4:
            phone_number = input("Enter new phone number: ")
            # Check if the phone number is valid
            if not re.match(r"^\d{10}$", phone_number):
                raise ValueError("Invalid phone number")
            cursor.execute(
                "UPDATE accounts SET phone_number = %s WHERE account_number = %s",
                (phone_number, account_number),
            )
        else:
            print("Invalid choice")
            return

        db.commit()
        print("Account details updated successfully")
    except Exception as e:
        db.rollback()
        print("An error has occurred:", str(e))


# Function to transfer funds
def transfer_funds():
    try:
        from_account = int(input("Enter account number to transfer from: "))
        to_account = int(input("Enter account number to transfer to: "))
        amount = float(input("Enter amount to transfer: "))

        # Check if the from which funds are transferred exists
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (from_account,)
        )
        from_account_data = cursor.fetchone()
        if not from_account_data:
            raise Exception(
                "The account from which the funds are to be transferred does not exist"
            )

        # Check if the to which funds are transferred exists
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (to_account,)
        )
        to_account_data = cursor.fetchone()
        if not to_account_data:
            print("The account to which the funds are to be transferred does not exist")

        # Retrieve the current balances of the accounts
        from_balance = from_account_data[1]
        to_balance = to_account_data[1]

        # Check if the payee account have sufficient balance
        if from_balance < amount:
            print("Insufficient balance")

        # Deduct amount from the payee account
        new_from_balance = from_balance - amount
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (new_from_balance, from_account),
        )

        # Add amount to the receiver's account
        new_to_balance = to_balance + amount
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (new_to_balance, to_account),
        )

        db.commit()
        print("Funds transferred successfully")
    except Exception:
        db.rollback()
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )


# Function to display account balance
def display_balance():
    try:
        account_number = int(input("Enter account number: "))

        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number,)
        )
        balance = cursor.fetchall()
        if balance:
            print(f"Account Number: {balance[0][0]}, Balance: {balance[0][1]}")
        else:
            print("Account not found")
    except Exception:
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )


# Function to display accounts list detailed
def display_account_list():
    try:
        account_number = int(input("Enter account number: "))

        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number,)
        )
        balance = cursor.fetchall()
        if balance:
            print(f"Account Number: {balance[0][0]}, Balance: {balance[0][1]}")
        else:
            print("Account not found")
    except Exception:
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )

def display_account_info():
    print("Hello")

# function to update balance
def update_balance():
    try:
        account_number = int(input("Enter account number: "))
        balance = float(input("Enter the new account balance: "))
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (balance, account_number),
        )
        db.commit()
        print("Account balance updated successfully")
    except Exception:
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )

def raise_ticket(account_number):
    ticket_id = uuid.uuid4().hex
    issue = input("please enter yor issue")
    cursor.execute(
        "UPDATE accounts SET ticket_number = %s WHERE account_number = %s",
        (ticket_id, account_number),
    )
    cursor.execute("INSERT INTO ticket_management_system  (ticket_id, account_number, issue) VALUES (%s, %s, %s)", (ticket_id, account_number, issue), ) 
    print("Your ticket has been raised with id : ", ticket_id)

# function to delete account
def delete_account():
    try:
        account_number = int(input("Enter account number: "))
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number,)
        )
        account_exists = cursor.fetchone()
        if not account_exists:
            print("The account to which the funds are to be transferred does not exist")
        else:
            cursor.execute(
                "DELETE FROM accounts WHERE account_number = %s", (account_number,)
            )
            db.commit()
            print("Account deleted successfully")
    except Exception:
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )


while True:
    choice = input(
        """Please select an option:
    Press 1 to login
    Press 2 to signup
    Press 3 to exit the program
    """
    )

    if choice == "login" or choice == "1":
        account_login()
        if is_admin():
            while True:
                choice = int(
                    input(
                        """Please select an option:
                Press 1 to add an account
                Press 2 to update account details
                Press 3 to transfer funds
                Press 4 to display account balance
                Press 5 to display account list
                Press 6 to delete account
                Press 7 to exit the program
                """
                    )
                )
                if choice == 1:
                    create_account()
                elif choice == 2:
                    update_account()
                elif choice == 3:
                    transfer_funds()
                elif choice == 4:
                    display_balance()
                elif choice == 5:
                    display_account_list()
                elif choice == 6:
                    delete_account()
                elif choice == 7:
                    exit()
                else:
                    print("Invalid choice")
        else:
            while True:
                choice = int(
                    input(
                        """Please select an option:
                Press 1 to update account details
                Press 2 to transfer funds
                Press 3 to display account balance
                Press 4 to detactivate your account
                Press 5 to reactivate your account
                Press 5 to view transaction history
                Press 6 to delete account
                Press 7 to exit the program
                """
                    )
                )
                if choice == 1:
                    create_account()
                elif choice == 2:
                    update_account()
                elif choice == 3:
                    transfer_funds()
                elif choice == 4:
                    display_balance()
                elif choice == 5:
                    display_account_list()
                elif choice == 6:
                    delete_account()
                elif choice == 7:
                    exit()
                else:
                    print("Invalid choice")

    elif choice == "signup" or choice == "2":
        create_account()
    elif choice == "exit" or choice == "3":
        print("Thank you for using our software. Have a nice day!")
        exit()
    else:
        print("Invalid choice. Please enter 'login' or 'signup'.")
