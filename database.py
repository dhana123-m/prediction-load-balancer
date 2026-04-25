import mysql.connector

try:
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Admin123",
        database="load_balancer",
        autocommit=True
    )

    cursor = db.cursor()
    print("MySQL Connected")

except Exception as e:
    print("Database Error:", e)