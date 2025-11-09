import csv
import psycopg2
import os
import time

def wait_for_db():
    for i in range(10):
        try:
            conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "accounts_db"),
                user=os.getenv("DB_USER", "admin"),
                password=os.getenv("DB_PASSWORD", "Password"),
                host=os.getenv("DB_HOST", "account-db"),
                port=os.getenv("DB_PORT", "5433")
            )
            conn.close()
            print("✅ Database is ready.")
            return
        except Exception as e:
            print(f"⏳ Waiting for DB... ({i+1}/10) {e}")
            time.sleep(3)
    raise Exception("❌ Database not reachable after 10 attempts")

def seed_accounts():
    wait_for_db()
    print("🚀 Starting seeding process...")

    conn = psycopg2.connect(
        dbname=os.getenv("DB_NAME", "accounts_db"),
        user=os.getenv("DB_USER", "admin"),
        password=os.getenv("DB_PASSWORD", "Password"),
        host=os.getenv("DB_HOST", "account-db"),
        port=os.getenv("DB_PORT", "5433")
    )
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id SERIAL PRIMARY KEY,
        customer_id VARCHAR(36) NOT NULL,
        account_number VARCHAR(50) UNIQUE NOT NULL,
        account_type VARCHAR(50) NOT NULL,
        balance NUMERIC(12,2) DEFAULT 0.00,
        currency VARCHAR(10) DEFAULT 'INR',
        status VARCHAR(20) DEFAULT 'ACTIVE',
        created_at TIMESTAMP NOT NULL
    );
    """)
    conn.commit()
    print("✅ 'accounts' table ready.")

    csv_path = os.getenv("CSV_PATH", "./data/accounts.csv")
    print(f"📄 Reading CSV from {csv_path}")

    if not os.path.exists(csv_path):
        print(f"❌ CSV file not found at {csv_path}")
        return

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

        if not rows:
            print("⚠️ CSV file is empty.")
            return

        print(f"📦 Preparing to insert {len(rows)} rows...")
        for row in rows:
            cursor.execute("""
                INSERT INTO accounts (
                    customer_id, account_number, account_type, balance, currency, status, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row["customer_id"],
                row["account_number"],
                row["account_type"],
                float(row["balance"]),
                row["currency"],
                row["status"],
                row["created_at"]
            ))

    conn.commit()
    cursor.close()
    conn.close()
    print("🌱 Seeding completed successfully!")

if __name__ == "__main__":
    seed_accounts()
