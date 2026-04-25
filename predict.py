import pandas as pd
import mysql.connector
from sklearn.tree import DecisionTreeClassifier
import pickle

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Admin123",
    database="load_balancer"
)

query = "SELECT cpu, ram, disk FROM system_metrics"
df = pd.read_sql(query, db)

# Create labels manually
labels = []

for i in range(len(df)):
    avg = (df['cpu'][i] + df['ram'][i] + df['disk'][i]) / 3

    if avg < 40:
        labels.append("Low")
    elif avg < 75:
        labels.append("Medium")
    else:
        labels.append("High")

df['label'] = labels

X = df[['cpu', 'ram', 'disk']]
y = df['label']

model = DecisionTreeClassifier()
model.fit(X, y)

pickle.dump(model, open("model.pkl", "wb"))

print("Model Trained Successfully")