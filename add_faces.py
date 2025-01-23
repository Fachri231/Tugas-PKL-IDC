import cv2
import pickle
import numpy as np
import os

# Inisialisasi
video = cv2.VideoCapture(0)
facedetect = cv2.CascadeClassifier('data/haarcascade_frontalface_default.xml')

# Pastikan folder "data" ada
if not os.path.exists('data'):
    os.makedirs('data')

# Fungsi untuk menyimpan data
def save_data(new_faces, new_names):
    if 'faces_data.pkl' not in os.listdir('data/'):
        faces = new_faces
    else:
        with open('data/faces_data.pkl', 'rb') as f:
            faces = pickle.load(f)
        faces = np.append(faces, new_faces, axis=0)

    if 'names.pkl' not in os.listdir('data/'):
        names = new_names
    else:
        with open('data/names.pkl', 'rb') as f:
            names = pickle.load(f)
        names = names + new_names

    # Simpan kembali data
    with open('data/faces_data.pkl', 'wb') as f:
        pickle.dump(faces, f)
    with open('data/names.pkl', 'wb') as f:
        pickle.dump(names, f)

# Loop untuk menambahkan beberapa orang
while True:
    name = input("Enter Your Name (or type 'exit' to quit): ")
    if name.lower() == 'exit':
        break

    faces_data = []
    i = 0

    print(f"Capturing data for {name}. Press 'q' to quit capturing.")
    while True:
        ret, frame = video.read()
        if not ret:
            print("Failed to capture video. Please check your camera.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = facedetect.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            crop_img = frame[y:y+h, x:x+w, :]
            resized_img = cv2.resize(crop_img, (50, 50))
            if len(faces_data) < 100 and i % 10 == 0:
                faces_data.append(resized_img)
            i += 1
            cv2.putText(frame, str(len(faces_data)), (50, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 255), 1)
            cv2.rectangle(frame, (x, y), (x+w, y+h), (50, 50, 255), 1)

        cv2.imshow("Frame", frame)

        # Cek kondisi untuk keluar dari loop
        k = cv2.waitKey(1)
        if k == ord('q') or len(faces_data) == 100:
            break

    if len(faces_data) == 100:
        print(f"Captured 100 faces for {name}. Saving data...")

    faces_data = np.asarray(faces_data)
    faces_data = faces_data.reshape(len(faces_data), -1)

    # Simpan data baru
    save_data(faces_data, [name] * len(faces_data))
    print(f"Data for {name} has been saved.")

video.release()
cv2.destroyAllWindows()
