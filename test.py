import psycopg2

#sudo systemctl start postgresql
# Connect to your postgres DB
conn = psycopg2.connect("dbname=alunos_db user=postgres")

# Open a cursor to perform database operations
cur = conn.cursor()

# Execute a query
cur.execute("SELECT * FROM my_data")

# Retrieve query results
records = cur.fetchall()