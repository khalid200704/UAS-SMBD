import mysql.connector
import os

# Pastikan folder output ada
if not os.path.exists("output"):
    os.mkdir("output")

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="yolo_edge"
)

cursor = db.cursor()
cursor.execute("SELECT id, timestamp, image FROM detections")

for (id, timestamp, image_blob) in cursor:
    if image_blob is None:
        continue

    # Convert timestamp to string dan ganti karakter ilegal
    ts = str(timestamp)
    ts = ts.replace(":", "-").replace(" ", "_")

    filename = f"output/{id}_{ts}.jpg"

    with open(filename, "wb") as f:
        f.write(image_blob)

cursor.close()
db.close()
