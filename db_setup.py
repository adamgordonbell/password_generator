import os
import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        port=os.environ['PGPORT'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        database=os.environ['PGDATABASE']
    )
    return conn

def setup_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('''
    CREATE TABLE IF NOT EXISTS attempts (
        id SERIAL PRIMARY KEY,
        password TEXT NOT NULL,
        strength INTEGER NOT NULL,
        timestamp TIMESTAMP NOT NULL
    )
    ''')
    
    conn.commit()
    cur.close()
    conn.close()
    print("Database setup complete.")

if __name__ == '__main__':
    setup_db()
