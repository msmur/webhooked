import os
import psycopg2
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
DB_CONNECTION_STRING = os.environ.get("DB_CONNECTION_STRING")

# SQL query to delete records older than 48 hours
DELETE_QUERY = """
    DELETE FROM webhooks WHERE created_at < NOW() - INTERVAL '48 hours';
"""


def cleanup_old_webhooks():
    try:
        print("Cleaning up old webhooks...")
        conn = psycopg2.connect(DB_CONNECTION_STRING)
        conn.autocommit = True  # Ensure changes are committed automatically
        cursor = conn.cursor()

        cursor.execute(DELETE_QUERY)
        deleted_rows = cursor.rowcount  # Get number of rows affected
        print(f"Deleted {deleted_rows} old webhook entries successfully.")

        # Close the connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    cleanup_old_webhooks()
