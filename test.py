from sklearn.neighbors import KNeighborsClassifier
import cv2
import pickle
import numpy as np
import mysql.connector
from datetime import datetime
from win32com.client import Dispatch  
import time

# Fungsi untuk memberikan notifikasi suara
def speak(message):
    speaker = Dispatch("SAPI.SpVoice")
    speaker.Speak(message)

# Koneksi ke database MySQL
def connect_to_database():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="attendance_system"
        )
        return db
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

db = connect_to_database()
cursor = db.cursor() if db else None

# Inisialisasi kamera dan face detection
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Load data wajah dan label
with open('data/names.pkl', 'rb') as w:
    LABELS = pickle.load(w)
with open('data/faces_data.pkl', 'rb') as f:
    FACES = pickle.load(f)

print('Shape of Faces matrix --> ', FACES.shape)

# Inisialisasi model KNN
knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(FACES, LABELS)

# Background untuk tampilan
imgBackground = cv2.imread("assets/background.png")

# Daftar nama yang sudah absensi untuk masuk dan keluar
absent_today_in = set()
absent_today_out = set()

while True:
    ret, frame = video.read()
    if not ret:
        print("Error: Unable to access the camera.")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = facedetect.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        crop_img = frame[y:y + h, x:x + w, :]
        resized_img = cv2.resize(crop_img, (50, 50)).reshape(50*50*3).reshape(1, -1)

        # Normalisasi gambar
        resized_img = resized_img / 255.0
        output = knn.predict(resized_img)[0]

        # Waktu saat ini
        ts = time.time()
        date = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        timestamp = datetime.fromtimestamp(ts).strftime("%H:%M:%S")

        # Logika absensi masuk dan keluar
        cursor.execute("SELECT * FROM attendance WHERE name = %s AND date = %s", (output, date))
        record = cursor.fetchone()

        if not record:
            # Jika belum ada data absensi, lakukan check-in
            cursor.execute("INSERT INTO attendance (name, date, time, status) VALUES (%s, %s, %s, 'Active')",
                            (output, date, timestamp))
            db.commit()
            absent_today_in.add(output)
            speak(f"{output}, absen masuk Anda telah direkam!")
            print(f"{output} berhasil absen masuk.")
        elif record and record[4] == 'Active':  # Jika status 'Active' sudah ada, lakukan check-out
            cursor.execute("UPDATE attendance SET time = %s, status = 'Inactive' WHERE name = %s AND date = %s",
                            (timestamp, output, date))
            db.commit()
            absent_today_out.add(output)
            speak(f"{output}, absen keluar Anda telah direkam!")
            print(f"{output} berhasil absen keluar.")
        elif record and record[4] == 'Inactive':  # Jika status 'Inactive', lakukan check-in ulang
            cursor.execute("UPDATE attendance SET time = %s, status = 'Active' WHERE name = %s AND date = %s",
                            (timestamp, output, date))
            db.commit()
            absent_today_in.add(output)
            speak(f"{output}, absen masuk Anda telah diperbarui!")
            print(f"{output} berhasil absen masuk kembali.")
        else:
            speak(f"{output}, Anda sudah menyelesaikan absensi hari ini!")
            print(f"{output} sudah menyelesaikan absensi hari ini.")

        # Tambahkan rectangle dan teks nama ke frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(frame, str(output), (x, y - 15), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)

        # Tambahkan nama pengguna di atas frame utama
        cv2.putText(imgBackground, f"Current User: {output}", (50, 100), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

    # Gabungkan frame ke background
    imgBackground[162:162 + 480, 55:55 + 640] = frame
    cv2.imshow("Attendance System", imgBackground)

    # Tombol untuk keluar
    k = cv2.waitKey(1)
    if k == ord('q'):
        break

# Tutup koneksi kamera dan database
video.release()
cv2.destroyAllWindows()
if cursor:
    cursor.close()
if db:
    db.close()
