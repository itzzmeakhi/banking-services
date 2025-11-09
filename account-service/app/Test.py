import psycopg2

try:
    conn = psycopg2.connect(
        dbname="accounts_db",   # <-- database name must be a string
        user="postgres",
        password="postgres",
        host="localhost",
        port="5432"
    )
    print("Connected to Postgres!")
except Exception as e:
    print("Connection failed:", e)
