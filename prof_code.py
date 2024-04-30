import logging
import azure.functions as func
import mysql.connector
import random


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Generate a random code
    random_code = str(random.randint(1000, 9999))  # Simple 4 digit code

    # Database credentials (should ideally be stored securely)
    username = "CC_6"
    password = "in0DLTSyT0r53vqouL_qi93A0UGv8ysbarEKELF5fu0"  # Replace with your actual password
    host = "dockerlab.westeurope.cloudapp.azure.com"
    database = "CC_6"

    # Connect to MySQL
    try:
        conn = mysql.connector.connect(
            user=username, 
            password=password, 
            host=host, 
            database=database
        )
        cursor = conn.cursor()

        # Insert the code into the database
        cursor.execute(f"INSERT INTO codes (code) VALUES ('{random_code}')")
        conn.commit()

        return func.HttpResponse(f'{{"code": "{random_code}"}}', mimetype="application/json")
    except Exception as e:
        return func.HttpResponse(f'{{"error": "{str(e)}"}}', status_code=500, mimetype="application/json")
