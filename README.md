# dbms_payment_system

This is a Python program that implements a Funds Transfer System using MySQL as the database management system (DBMS). The program allows users to create accounts, transfer funds between accounts, display account balances, update account details, and delete accounts.
Requirements

Before running the program, make sure you have the following requirements installed:

    Python 3.x
    mysql-connector-python library
    faker library

You can install the required libraries using pip:

pip install mysql-connector-python faker

Configuration

Make sure to update the database configuration variables (db_host, db_username, and db_password) at the beginning of the script according to your MySQL database setup.
Usage

To use the program, run the Python script funds_transfer_system.py. The program will display a menu with options to perform various operations.

    Login: This option allows you to log in to the system. You can enter your username and passkey to authenticate yourself.

    Signup: This option is for creating a new account. You need to provide account details such as account number, initial balance, username, email, phone number, and passkey.

    Exit: This option allows you to exit the program.

Once logged in, the available operations depend on whether you are an admin or a regular user.
Admin Operations

If you are logged in as an admin, the following operations are available:

    Add an account: This option allows you to add a new account to the system. You need to provide account details such as account number, initial balance, username, email, phone number, and passkey.

    Update account details: This option allows you to update the details of an existing account. You can choose the account details to update, including balance, username, email, and phone number.

    Transfer funds: This option allows you to transfer funds between two accounts. You need to provide the account numbers and the amount to transfer.

    Display account balance: This option allows you to display the balance of a specific account. You need to provide the account number.

    Display account list: This option allows you to display detailed information about a specific account. You need to provide the account number.

    Delete account: This option allows you to delete an account from the system. You need to provide the account number.

    Exit: This option allows you to exit the program.

Regular User Operations

If you are logged in as a regular user, the following operations are available:

    Update account details: This option allows you to update your account details, including balance, username, email, and phone number.

    Transfer funds: This option allows you to transfer funds from your account to another account. You need to provide the account number of the receiving account and the amount to transfer.

    Display account balance: This option allows you to display the balance of your account.

    Deactivate your account: This option allows you to deactivate (delete) your account from the system.

    Exit: This option allows you to exit the program.

Sample Data

The program includes a function to generate sample data for the accounts table. You can use this function to populate the table with dummy account entries for testing purposes. When prompted, enter the number of sample entries you want to generate. You can choose whether to log the details of the accounts being pushed.
Note

This program is for educational purposes and demonstrates the basic functionality of a funds transfer system. It may not include all the necessary security measures for a production-ready system. Make sure to implement additional security measures and validations as per your requirements.
