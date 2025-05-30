import sqlite3


class Database:
    def __init__(self):
        self.__create_connection()
        self.__create_tables()
        self.__initialize_tables_if_not_initialized()
        
    def __create_connection(self):
        print('Initializing the database...')
        self.__conn = sqlite3.connect('bank_db.sqlite')
        self.__cursor = self.__conn.cursor()
        print('Completed initializing the database with bank_db.sqlite')   
    
    def __create_tables(self):
        print('Creating tables...')
        self.__cursor.execute('''
           CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                type TEXT,
                description TEXT,
                min_balance REAL,
                interest_rate REAL
            )                     
        ''')
        
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY,
                type TEXT,
                description TEXT,
                interest_rate REAL,
                max_amount REAL,
                min_term INTEGER,
                max_term INTEGER
            )
        ''')
        
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS branches (
                id INTEGER PRIMARY KEY,
                branch_name VARCHAR(100),
                branch_code INTEGER(3),
                address VARCHAR(255)
            )
        ''')
        
        self.__cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_feedback (
                id INTEGER PRIMARY KEY,
                query TEXT,
                response TEXT,
                feedback INTEGER,
                timestamp TEXT
            )
        ''')
        
        self.__conn.commit()
        print('Completed creating tables.')
        
    def __initialize_tables_if_not_initialized(self):
        if not self.__cursor.execute('SELECT COUNT(*) FROM accounts').fetchone()[0]:
            self.__populate_accounts_table_with_sample_data()
            
        if not self.__cursor.execute('SELECT COUNT(*) FROM loans').fetchone()[0]:
            self.__populate_loans_table_with_sample_data()
            
        if not self.__cursor.execute('SELECT COUNT(*) FROM branches').fetchone()[0]:
            self.__populate_branches_table_with_sample_data()
    
    def __populate_accounts_table_with_sample_data(self):
        print('Populating accounts table with sample data...')
        accounts = [
            ("Savings", "Basic savings account", 500, 1.5),
            ("Checking", "Everyday checking account", 1000, 0.1),
            ("Fixed Deposit", "Term deposit with fixed interest", 10000, 3.5),
            ("Joint", "Account shared between multiple people", 2000, 0.5)
        ]
        self.__cursor.executemany("INSERT INTO accounts (type, description, min_balance, interest_rate) VALUES (?, ?, ?, ?)", accounts)
        self.__conn.commit()
        print('Completed populating accounts table with sample data.')
    
    def __populate_loans_table_with_sample_data(self):
        print('Populating loans table with sample data...')
        loans = [
            ("Personal", "Unsecured personal loan", 7.5, 50000, 1, 5),
            ("Home", "Mortgage for property purchase", 4.5, 2000000, 5, 30),
            ("Auto", "Vehicle financing", 5.0, 500000, 1, 7),
            ("Education", "Student loan for education", 6.0, 1000000, 1, 10)
        ]
        self.__cursor.executemany("INSERT INTO loans (type, description, interest_rate, max_amount, min_term, max_term) VALUES (?, ?, ?, ?, ?, ?)", loans)
        self.__conn.commit()
        print('Completed populating loans table with sample data.')
        
    def __populate_branches_table_with_sample_data(self):
        print('Populating branches table with sample data...')
        branches = [
            ("Colombo Main Branch", 101, "123 Galle Road, Colombo 03"),
            ("Kandy City Branch", 102, "45 Dalada Veediya, Kandy"),
            ("Galle Branch", 103, "78 Matara Road, Galle"),
            ("Jaffna Branch", 104, "12 Kankesanthurai Road, Jaffna"),
            ("Kurunegala Branch", 105, "34 Colombo Road, Kurunegala"),
            ("Negombo Branch", 106, "67 Chilaw Road, Negombo"),
            ("Anuradhapura Branch", 107, "23 Mihintale Road, Anuradhapura"),
            ("Ratnapura Branch", 108, "56 Gem Street, Ratnapura"),
            ("Matara Branch", 109, "89 Beach Road, Matara"),
            ("Batticaloa Branch", 110, "14 Trincomalee Road, Batticaloa")
        ]
        self.__cursor.executemany("INSERT INTO branches (branch_name, branch_code, address) VALUES (?, ?, ?)", branches)
        self.__conn.commit()
        print('Completed populating branches table with sample data.')
    
    def add_data_to_feedback_table(self, query, response, feedback, timestamp):
        self.__cursor.execute(
            "INSERT INTO user_feedback (query, response, feedback, timestamp) VALUES (?, ?, ?, ?)",
            (query, response, feedback, timestamp)
        )
        
        self.__conn.commit()
    
    def get_all_account_types(self):
        # Get all account types from database
        self.__cursor.execute("SELECT type, description, min_balance, interest_rate FROM accounts")
        accounts = self.__cursor.fetchall()
        return accounts

    def get_all_loan_types(self):
        # Get all loan types from database
        self.__cursor.execute("SELECT type, description, interest_rate, max_amount, min_term, max_term FROM loans")
        loans = self.__cursor.fetchall()
        return loans
    
    def get_all_branches(self):
        self.__cursor.execute("SELECT branch_name, branch_code, address FROM branches")
        branches = self.__cursor.fetchall()
        return branches    
    
    def get_all_feedbacks(self):
        self.__cursor.execute("SELECT query, response, feedback, timestamp FROM user_feedback")
        user_feedbacks = self.__cursor.fetchall()
        return user_feedbacks
    
    def connection_close(self):
        self.__conn.close()
        