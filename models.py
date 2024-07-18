import mysql.connector
from mysql.connector import Error
from config import Config

class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=Config.DB_HOST,
                    user=Config.DB_USER,
                    password=Config.DB_PASSWORD,
                    database=Config.DB_NAME,
                    buffered=True
                )
                self.cursor = self.connection.cursor(dictionary=True)
            except Error as e:
                print(f"Error connecting to database: {e}")
                raise

    def execute(self, query, params=None):
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
        except Error as e:
            print(f"Error executing query: {e}")
            raise

    def fetchall(self, query, params=None):
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            results = self.cursor.fetchall()
            self.clear_unread_results()  # Ensure all results are read
            return results
        except Error as e:
            print(f"Error fetching all results: {e}")
            raise

    def fetchone(self, query, params=None):
        self.connect()
        try:
            self.cursor.execute(query, params or ())
            result = self.cursor.fetchone()
            self.clear_unread_results()  # Ensure all results are read
            return result
        except Error as e:
            print(f"Error fetching one result: {e}")
            raise

    def clear_unread_results(self):
        while self.cursor.nextset():
            self.cursor.fetchall()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

class LCApplicationModel:
    def __init__(self):
        self.db = Database()

    def create_application(self, application_id, applicant_country, applicant_name, applicant_bank_account, applicant_pan, amount, currency, applicant_bank_name, purpose, beneficiary_country, beneficiary_name, beneficiary_bank_account, beneficiary_bank_name):
        query = """
        INSERT INTO lc_applications (application_id, applicant_country, applicant_name, applicant_bank_account, applicant_pan, amount, currency, applicant_bank_name, purpose, beneficiary_country, beneficiary_name, beneficiary_bank_account, beneficiary_bank_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.db.execute(query, (application_id, applicant_country, applicant_name, applicant_bank_account, applicant_pan, amount, currency, applicant_bank_name, purpose, beneficiary_country, beneficiary_name, beneficiary_bank_account, beneficiary_bank_name))

    def get_all_applications(self):
        query = "SELECT * FROM lc_applications"
        return self.db.fetchall(query)
    
    def delete_application(self, application_id):
        query = "DELETE FROM lc_applications WHERE application_id = %s"
        self.db.execute(query, (application_id,))

    def update_approval_status(self, application_id, status):
        query = "UPDATE lc_applications SET approval_status = %s WHERE application_id = %s"
        self.db.execute(query, (status, application_id))

    def update_dispatch_status(self, application_id, status):
        query = "UPDATE lc_applications SET dispatch_status = %s WHERE application_id = %s"
        self.db.execute(query, (status, application_id))
    
    def update_document_url(self, application_id, document_url):
        query = "UPDATE lc_applications SET document_url = %s WHERE application_id = %s"
        self.db.execute(query, (document_url, application_id))

    def get_document_url(self, application_id):
        query = "SELECT document_url FROM lc_applications WHERE application_id = %s"
        result = self.db.fetchone(query, (application_id,))
        return result['document_url'] if result else None
     
    def update_fund_release_status(self, application_id, status):
        query = "UPDATE lc_applications SET fund_release_status = %s WHERE application_id = %s"
        self.db.execute(query, (status, application_id))