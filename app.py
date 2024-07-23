from flask import Flask, request, jsonify
import mysql.connector
from mysql.connector import Error
from decimal import Decimal
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow Cross-Origin Resource Sharing for all routes

#mySQL configurations
MYSQL_HOST = 'your_host' #update with your information
MYSQL_USER = 'your_user' 
MYSQL_PASSWORD = 'your_password' 
MYSQL_DB = 'your_database' 

#function to convert Decimal to float for JSON serialization
def decimal_to_float(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

#route to check if an account exists
@app.route('/check_account', methods=['GET'])
def check_account():
    account_number = request.args.get('account_number')
    
    if not account_number:
        return jsonify({'error': "Missing account number parameter"}), 400
    
    try:
        #connect to MySQL database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM transactions WHERE account_number = %s",
            (account_number,)
        )
        result = cursor.fetchone()
        account_exists = result[0] > 0 
        cursor.close()
        connection.close()

        return jsonify({'account_exists': account_exists}), 200

    except Error as e:
        return jsonify({'error': str(e)}), 500

#route to create a new account
@app.route('/create_account', methods=['POST'])
def create_account():
    data = request.get_json()
    account_number = data.get('account_number')
    initial_balance = Decimal(data.get('initial_balance', 0))

    if not account_number:
        return jsonify({'error': 'Missing account number'}), 400
    
    try:
        #connect to MySQL database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute(
            "INSERT INTO transactions (account_number, transaction_type, amount, balance) VALUES (%s, %s, %s, %s)",
            (account_number, 'initial', initial_balance, initial_balance)
        )
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({'message': 'Account created successfully'}), 200
    
    except Error as e:
        return jsonify({'error': str(e)}), 500

#route to handle deposits and withdrawals
@app.route('/transactions', methods=['POST'])
def handle_transaction():
    data = request.get_json()
    account_number = data['account_number']
    transaction_type = data['transaction_type']
    amount = Decimal(data['amount'])

    try:
        #connect to MySQL database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )

        if connection.is_connected():
            cursor = connection.cursor()

            #fetch the latest balance for the account
            cursor.execute(
                "SELECT balance FROM transactions WHERE account_number = %s ORDER BY id DESC LIMIT 1", 
                (account_number,)
            )
            result = cursor.fetchone()
            current_balance = Decimal(result[0]) if result else Decimal('0.0')

            #calculate the new balance based on transaction type
            if transaction_type.lower() == 'deposit':
                new_balance = current_balance + amount
            elif transaction_type.lower() == 'withdraw':
                if amount > current_balance:
                    return jsonify({'error': 'Insufficient funds for withdrawal'}), 400
                new_balance = current_balance - amount
            else:
                return jsonify({'error': 'Invalid transaction type'}), 400

            #insert the new transaction with the updated balance
            cursor.execute(
                "INSERT INTO transactions (account_number, transaction_type, amount, balance) VALUES (%s, %s, %s, %s)",
                (account_number, transaction_type, amount, new_balance)
            )
            connection.commit()

            cursor.close()
            connection.close()

            return jsonify({'message': 'Transaction successful'}), 200

    except Error as e:
        return jsonify({'error': str(e)}), 500

#route to get the balance of an account
@app.route('/balance', methods=['GET'])
def get_balance():
    account_number = request.args.get('account_number')

    if not account_number:
        return jsonify({'error': 'Missing account number parameter'}), 400
    
    try:
        #connect to MySQL database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )
        cursor = connection.cursor()
        cursor.execute(
            "SELECT balance FROM transactions WHERE account_number = %s ORDER BY id DESC LIMIT 1", 
            (account_number,)
        )
        result = cursor.fetchone()
        balance = result[0] if result else 0.0
        cursor.close()
        connection.close()

        #convert balance to float for JSON serialization
        if isinstance(balance, Decimal):
            balance = float(balance)

        return jsonify({'balance': balance}), 200
    
    except Error as e:
        return jsonify({'error': str(e)}), 500

#route to get all transactions
@app.route('/transactions', methods=['GET'])
def get_transactions():
    try:
        #connect to MySQL database
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB
        )

        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM transactions;")
            transactions = cursor.fetchall()
            transaction_list = []
            for transaction in transactions:
                transaction_dict = {
                    'id': transaction[0],
                    'account_number': transaction[1],
                    'transaction_type': transaction[2],
                    'amount': decimal_to_float(transaction[3]),
                    'transaction_date': transaction[4].strftime('%Y-%m-%d %H:%M:%S')
                }
                transaction_list.append(transaction_dict)
            
            cursor.close()
            connection.close()

            return jsonify({'transactions': transaction_list})

    except Error as e:
        return jsonify({'error': 'Failed to fetch transactions'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#route to welcome message
@app.route('/')
def index():
    return "Welcome to the Bank Transactions API! Go to /transactions to see the transactions."

if __name__ == '__main__':
    app.run(debug=True)
