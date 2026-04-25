import mysql.connector

db = mysql.connector.connect(
    host="shuttle.proxy.rlwy.net",
    port=34758,
    user="root",
    password="YOUR_PASSWORD",
    database="railway",
    autocommit=True
)

cursor = db.cursor()
