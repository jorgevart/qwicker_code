import logging
import azure.functions as func
import mysql.connector
import datetime
import os
import json
from azure.storage.queue import QueueClient
from azure.data.tables import TableServiceClient, TableEntity

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Azure Function Processing a HTTP Request for Attendance Tracking')

    # Retrieve parameters from the request
    student_email = req.params.get('email')
    course_name = req.params.get('course')
    entered_code = req.params.get('input')

    # Check if all required parameters are provided
    if not all([student_email, course_name, entered_code]):
        return func.HttpResponse('{"message": "Missing required parameters: email, course, or code", "status_code": 400}', status_code=400, mimetype="application/json")

    # Database credentials
    username = "CC_6"
    password = "in0DLTSyT0r53vqouL_qi93A0UGv8ysbarEKELF5fu0"
    host = "dockerlab.westeurope.cloudapp.azure.com"
    database = "CC_6"

    # Define the name of the error queue
    error_queue_name = 'dlq' 

    try:
        # Establish database connection
        conn = mysql.connector.connect(
            user=username,
            password=password,
            host=host,
            database=database
        )
        cursor = conn.cursor()

        # New Azure Table Service code
        connection_string = "DefaultEndpointsProtocol=https;AccountName=qwickerstorage;AccountKey=gCc+53yuV86U8BTfRiX3sDmqxQ/3mTA1DorXN8xVZbpe/jzR6rvM23eDjOtDGdz1iKDrNtPdMLFY+ASthTxS8A==;EndpointSuffix=core.windows.net"
        table_service = TableServiceClient.from_connection_string(conn_str=connection_string)
        table_client = table_service.get_table_client(table_name="queuelogs")

        # Create and log entry
        log_entry = TableEntity()
        log_entry['PartitionKey'] = student_email
        log_entry['RowKey'] = str(datetime.datetime.utcnow())
        log_entry['EnteredCode'] = entered_code

        # Insert the log entry into the table
        table_client.create_entity(entity=log_entry)


        # Validate the entered code against the latest active code in the database
        cursor.execute("SELECT code FROM codes WHERE status = 'active' ORDER BY code_id DESC LIMIT 1")
        latest_code = cursor.fetchone()

        if latest_code and entered_code == latest_code[0]:
            # Retrieve student_id using the provided email
            cursor.execute("SELECT student_id FROM students WHERE email LIKE %s", ('%' + student_email + '%',))
            student_id = cursor.fetchone()

            if student_id:
                # Update attendance status to 'PRESENT' for the student
                cursor.execute("""
                    UPDATE attendance_records
                    SET status = 'PRESENT'
                    WHERE student_id = %s AND session_id = (
                        SELECT session_id FROM sessions
                        WHERE course_id = (
                            SELECT course_id FROM courses
                            WHERE course_name = %s
                        )
                        ORDER BY session_id DESC
                        LIMIT 1
                    )
                """, (student_id[0], course_name))
                conn.commit()

                return func.HttpResponse('{"message": "Attendance updated to PRESENT."}', mimetype="application/json")
            else:
                return func.HttpResponse('{"message": "Student not found.", "status_code": 404}', status_code=404, mimetype="application/json")
        else:
            # Logging the error attempt in the log-error-attempts queue
            error_attempt = {
                "ReceivedCode": entered_code,
                "Timestamp": str(datetime.datetime.utcnow())
            }
            connection_string = os.environ['AzureWebJobsStorage']
            queue_service = QueueClient.from_connection_string(connection_string, error_queue_name)
            queue_service.send_message(json.dumps(error_attempt))
            return func.HttpResponse('{"message": "Incorrect code entered.", "status_code": 400}', status_code=400, mimetype="application/json")

    except Exception as e:
        logging.error(f"Error: {str(e)}")

        # Logging the error attempt in the log-error-attempts queue
        error_attempt = {
            "ReceivedCode": entered_code,
            "Timestamp": str(datetime.datetime.utcnow())
        }
        connection_string = os.environ['AzureWebJobsStorage']
        queue_service = QueueClient.from_connection_string(connection_string, error_queue_name)
        queue_service.send_message(json.dumps(error_attempt))

        return func.HttpResponse(f'{{"message": "Error: {str(e)}", "status_code": 500}}', status_code=500, mimetype="application/json")
    finally:
        # Close the database connection
        if conn.is_conne
