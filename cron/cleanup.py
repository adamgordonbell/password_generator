import os
import psycopg2
from datetime import datetime, timedelta
import sys

def get_db_connection():
    conn = psycopg2.connect(
        host=os.environ['PGHOST'],
        port=os.environ['PGPORT'],
        user=os.environ['PGUSER'],
        password=os.environ['PGPASSWORD'],
        database=os.environ['PGDATABASE']
    )
    return conn

def cleanup_old_attempts():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get the minimum strength score from the top 5 entries
    cur.execute('SELECT MIN(strength) FROM (SELECT strength FROM attempts ORDER BY strength DESC LIMIT 5) AS top_scores')
    min_top_score = cur.fetchone()[0]

    # Delete attempts older than 7 days that are not in the top score list
    seven_days_ago = datetime.now() - timedelta(days=7)
    cur.execute('DELETE FROM attempts WHERE timestamp < %s AND strength < %s', (seven_days_ago, min_top_score))
    
    deleted_count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"Cleanup complete. {deleted_count} entries removed.")

def clear_all_attempts():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('DELETE FROM attempts')
    
    deleted_count = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    print(f"All attempts cleared. {deleted_count} entries removed.")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--clear-all':
        print("Clearing all attempts")
        clear_all_attempts()
    else:
        print("Running clean up")
        cleanup_old_attempts()
