import mysql.connector
import re
import random
import hashlib
import getpass
from datetime import datetime
import string
from faker import Faker
from termcolor import colored, cprint
import uuid

cprint(
    """

████████╗██████╗░░█████╗░███╗░░██╗░██████╗███████╗██╗░░░██╗███╗░░██╗██████╗░░██████╗
╚══██╔══╝██╔══██╗██╔══██╗████╗░██║██╔════╝██╔════╝██║░░░██║████╗░██║██╔══██╗██╔════╝
░░░██║░░░██████╔╝███████║██╔██╗██║╚█████╗░█████╗░░██║░░░██║██╔██╗██║██║░░██║╚█████╗░
░░░██║░░░██╔══██╗██╔══██║██║╚████║░╚═══██╗██╔══╝░░██║░░░██║██║╚████║██║░░██║░╚═══██╗
░░░██║░░░██║░░██║██║░░██║██║░╚███║██████╔╝██║░░░░░╚██████╔╝██║░╚███║██████╔╝██████╔╝
░░░╚═╝░░░╚═╝░░╚═╝╚═╝░░╚═╝╚═╝░░╚══╝╚═════╝░╚═╝░░░░░░╚═════╝░╚═╝░░╚══╝╚═════╝░╚═════╝░

""",
    "yellow",
    "on_light_magenta",
)

# Establish connection with MySQL database
db_host = "localhost"
db_username = "root"
db_password = "root"
is_admin = False
account_number = -1
try:
    db = mysql.connector.connect(host=db_host, user=db_username, password=db_password)
except Exception as e:
    print("There was an error connnecting to the database")
    exit()

cursor = db.cursor()

# SQL query to initilaize the database
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
  passkey VARCHAR(255), 
  active BOOLEAN NOT NULL
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
  ticket_time TIME
  );
"""
)


# Function to exit the program
def exit_program():
    print("Thank you for using our software. Have a nice day!")
    exit()


# Function to print error message
def error():
    cprint(
        "An error has occurred. Please try again later or contact technical support for assistance!",
        "red",
        attrs=["bold"],
    )


# function to generate random password
def generate_passkey(length=8):
    # Define characters to choose from
    characters = string.ascii_letters + string.digits + string.punctuation

    # Generate a random passkey
    passkey = "".join(random.choice(characters) for _ in range(length))

    return passkey


# Function to hash the passkey before storing into database
def hash_passkey(passkey):
    hashed_passkey = hashlib.sha256(passkey.encode("utf-8")).hexdigest()
    return hashed_passkey


# Function to verify phone number
def verify_phone_number(phone_number):
    phone_number_pattern = r"^(?:\+?\d{1,3}\s?)?(?:\(\d{1,}\)|\d{1,})[-.\s/]?\d{1,}[-.\s/]?\d{1,}[-.\s/]?\d{1,}(?:\s?(?:x|ext)\d{1,})?$|^(\+\d{1,3})(\d{1,})$"
    if re.match(phone_number_pattern, str(phone_number)):
        return True
    else:
        return False


# Function to verify email id
def verify_email(email):
    email_pattern = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(email_pattern, email):
        return True
    else:
        return False


# Function to push account details to the server
def push_account(
    username, email, phone_number, passkey, balance=float(0), account_number=""
):
    try:
        # encrypt the passkey
        hashed_passkey = hash_passkey(passkey)

        # Check if the email id is valid
        if verify_email(email) and verify_phone_number(phone_number):
            hashed_passkey = hash_passkey(passkey)
            # Insert the new account into the accounts table
            if account_number != "":
                try:
                    cursor.execute(
                        "INSERT INTO accounts (account_number, balance, username, email, phone_number, passkey) VALUES (%s, %s, %s, %s, %s, %s)",
                        (
                            account_number,
                            balance,
                            username,
                            email,
                            phone_number,
                            hashed_passkey,
                        ),
                    )
                except Exception as e:
                    print(
                        "Error inserting account. Same account_number exists in database",
                        "red",
                        attrs=["bold"],
                    )
            else:
                cursor.execute(
                    "INSERT INTO accounts ( balance, username, email, phone_number, passkey, active) VALUES (%s, %s, %s, %s, %s, 1)",
                    (balance, username, email, phone_number, hashed_passkey),
                )

            db.commit()

            # Fetch the generated account number from the database
            account_number = cursor.lastrowid

            table_username = f"transaction_history_{account_number}"

            # Create the user's transaction history table
            cursor.execute(
                f"""
    CREATE TABLE IF NOT EXISTS {table_username} (
        id INT AUTO_INCREMENT PRIMARY KEY,
        transaction_type VARCHAR(50),
        amount FLOAT,
        transaction_datetime DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """
            )

            db.commit()

            cprint("Account created successfully", "green")
        else:
            cprint("Kindly enter valid details", "red")
    except Exception as e:
        db.rollback()
        # print(e)
        error()

#Function to authorize into application
def account_login():
    global account_number, is_admin
    username = input("Enter your username: ")
    passkey = getpass.getpass("Enter your passkey: ")
    if username == db_username and passkey == db_password:
        is_admin = True
        cprint("You are logged in successfully as " + db_username, "green")
    else:
        hashed_passkey = hash_passkey(passkey)
        cursor.execute(
            "SELECT * FROM accounts WHERE username = %s AND passkey = %s",
            (username, hashed_passkey),
        )
        user = cursor.fetchone()
        if user:
            if int(user[-1]) == 1:
                account_number = int(user[0])
                cprint("Login successful!", "green")
            else:
                cprint(
                    "Your account has been suspended for violating our terms and conditions. For any query contact customer care",
                    "red",
                    attrs=["bold"],
                )
                exit_program()
        else:
            cprint("Invalid username or passkey!", "red", attrs=["bold"])


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
            balance = round(random.uniform(0, 1000) * 100, 2)
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

        cprint("Sample data for the main table added successfully", "green")

    except Exception as e:
        db.rollback()
        print("An error has occurred:", str(e))


# Function to create a new account
def create_account():
    username = input("Enter your name: ")
    email = input("enter your email id: ")
    phone_number = input("Enter your phone number:")
    passkey = getpass.getpass("Enter your passkey: ")

    push_account(username, email, phone_number, passkey)


# Function to update account details
def update_account():
    try:
        # Retrieve existing account details
        if is_admin:
            account_number = input("Enter account number: ")
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
        if is_admin:
            from_account = int(input("Enter account number to transfer from: "))
        else:
            from_account = account_number
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
        transaction_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        from_table_name = f"transaction_history_{from_account}"
        to_table_name = f"transaction_history_{to_account}"
        cursor.execute(
    f"""
    INSERT INTO {from_table_name} (transaction_type, amount, transaction_datetime)
    VALUES ("sent", %s, %s)
    """,
    (amount, transaction_datetime)
)
        cursor.execute(
    f"""
    INSERT INTO {to_table_name} (transaction_type, amount, transaction_datetime)
    VALUES ("received", %s, %s)
    """,
    (amount, transaction_datetime)
)

        db.commit()
        cprint("{} transferred successfully to {}".format(amount, to_account), "green")
    except Exception:
        db.rollback()
        error()

def withdraw():
    global account_number
    amount = float(input("Enter how much do you want to withdraw"))
    try:
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number, ),
        )
        account_data = cursor.fetchone()

        # Retrieve the current balances of the account
        balance = account_data[1]

        # Check if the account has sufficient balance
        if balance < amount:
            print("Insufficient balance")

        # Deduct amount from the payee account
        new_from_balance = balance - amount
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (new_from_balance, account_number),
        )

        transaction_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        table_name = f"transaction_history_{account_number}"
        cursor.execute(
    f"""
    INSERT INTO {table_name} (transaction_type, amount, transaction_datetime)
    VALUES ("withdrawn", %s, %s)
    """,
    (amount, transaction_datetime)
)

        db.commit()
        cprint("successfully withdrawed {}".format(amount), "green")
    except Exception as e:
        db.rollback()
        print(e)
        error()

def deposit():
    global account_number
    amount = float(input("Enter how much do you want to deposit"))
    try:
        cursor.execute(
            "SELECT * FROM accounts WHERE account_number = %s", (account_number, ),
        )
        account_data = cursor.fetchone()

        # Retrieve the current balances of the account
        balance = account_data[1]

        # Deduct amount from the payee account
        new_from_balance = balance + amount
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (new_from_balance, account_number),
        )

        transaction_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        table_name = f"transaction_history_{account_number}"
        cursor.execute(
    f"""
    INSERT INTO {table_name} (transaction_type, amount, transaction_datetime)
    VALUES ("deposited", %s, %s)
    """,
    (amount, transaction_datetime)
)

        db.commit()
        cprint("successfully deposited {}".format(amount), "green")
    except Exception as e:
        db.rollback()
        print(e)
        error()

def view_transaction_history(account_number):
    try:
        table_name = f"transaction_history_{account_number}"
        cursor.execute(
            f"SELECT * FROM {table_name}"
        )
        transactions = cursor.fetchall()

        if transactions:
            print("Transaction History:")
            for transaction in transactions:
                transaction_id = transaction[0]
                transaction_type = transaction[1]
                amount = transaction[2]
                transaction_datetime = transaction[3]
                print(f"Transaction ID: {transaction_id}")
                print(f"Transaction Type: {transaction_type}")
                print(f"Amount: {amount}")
                print(f"Transaction DateTime: {transaction_datetime}")
                print("---------------------------")
        else:
            print("No transaction history found.")
    except Exception as e:
        print(e)
        error()

# Function to deactivate account
def deactivate_account():
    account_number  = input("Enter account number to deactivate:")
    query = "UPDATE accounts SET active = 0 WHERE username = %s"
    cursor.execute(query, (account_number,))
    db.commit()
    cprint(f"Account {account_number} deactivated successfully.", 'green')


# Functio to reactivate account
def reactivate_account():
    account_number  = int(input("Enter account number to reactivate:"))
    query = "UPDATE accounts SET active = 1 WHERE account_number = %s"
    cursor.execute(query, (account_number,))
    db.commit()
    cprint(f"Account {account_number} reactivated successfully.", 'green')


# function to update balance
def update_balance():
    try:
        if is_admin:
            account_number = int(input("Enter account number: "))
        balance = float(input("Enter the new account balance: "))
        cursor.execute(
            "UPDATE accounts SET balance = %s WHERE account_number = %s",
            (balance, account_number),
        )
        db.commit()
        print("Account balance updated successfully")
    except Exception:
        error()


# Function to raise ticket
def raise_ticket():
    ticket_id = uuid.uuid4().hex
    issue = input("please enter yor issue")
    cursor.execute(
        "UPDATE accounts SET ticket_number = %s WHERE account_number = %s",
        (ticket_id, account_number),
    )
    cursor.execute(
        "INSERT INTO ticket_management_system  (ticket_id, account_number, issue) VALUES (%s, %s, %s)",
        (ticket_id, account_number, issue),
    )
    print("Your ticket has been raised with id : {}".format(ticket_id), "green")
    print("Kindly remmeber this for future reference")


# function to delete account
def delete_account():
    global account_number
    try:
        user_input = 1
        if is_admin:
            account_number = int(input("Enter account number: "))
        else:
            user_input = input(
                colored(
                    "Are you sure you want to drop the database(Enter 1 to continue): ",
                    "yellow",
                )
            )
        if int(user_input.strip()) == 1:
            cursor.execute(
                "DELETE FROM accounts WHERE account_number = %s", (account_number,)
            )
            db.commit()
            print("Account deleted successfully")
            exit_program()
    except Exception:
        print(
            "An error has occurred. Please try again later or contact technical support for assistance."
        )


# Function to drop the database
def drop_all():
    try:
        user_input = input(
            colored(
                "Are you sure you want to drop the database(Enter 1 to continue): ",
                "yellow",
            )
        )
        if int(user_input.strip()) == 1:
            cursor.execute("DROP DATABASE funds_transfer_system;")
            db.commit()
            cprint("Database has been deleted", "magenta")
            exit_program()

    except Exception:
        db.rollback()
        error()


def main():
    choice = input(
        """Please select an option:
    Press 1 to login
    Press 2 to signup
    Press 3 to exit the program
    """
    )
    if choice == "login" or choice == "1":
        account_login()
        if is_admin:
            while True:
                choice = int(
                    input(
                        """Please select an option:
Press 1 to add an account
Press 2 to update account details
Press 3 to transfer funds
Press 4 to generate sample data
Press 5 to deactivate account
Press 6 to reactivate account
Press 7 to diplay account list
Press 8 to drop databse
Press 9 to exit
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
                    generate_sample_data()
                elif choice == 5:
                    deactivate_account()
                elif choice == 6:
                    reactivate_account()
                elif choice == 7:
                    print()
                elif choice == 8:
                    drop_all()    
                elif choice == 9:
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
                    update_account()
                elif choice == 2:
                    transfer_funds()
                # elif choice == 3:
                #     display_balance()
                elif choice == 4:
                    deactivate_account()
                # elif choice == 5:
                #     display_account_list()
                elif choice == 6:
                    delete_account()
                elif choice == 7:
                    exit_program()
                else:
                    print("Invalid choice")

    elif choice == "signup" or choice == "2":
        create_account()
    elif choice == "exit" or choice == "3":
        exit_program
    else:
        print("Invalid choice. Please enter 'login' or 'signup'.")

main()
