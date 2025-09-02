import cv2
import numpy as np
import os
from database_manager import DatabaseManager

class FaceRecognitionSystem:
    def __init__(self):
        self.db = DatabaseManager()
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.known_faces = []
        self.known_ids = []
        self.load_known_faces()
        
    def load_known_faces(self):
        users = self.db.get_all_users()
        for user in users:
            user_id, _, image_path, _ = user
            if os.path.exists(image_path):
                img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                faces = self.face_cascade.detectMultiScale(img, scaleFactor=1.1, minNeighbors=5)
                if len(faces) > 0:
                    (x, y, w, h) = faces[0]
                    face_roi = img[y:y+h, x:x+w]
                    self.known_faces.append(face_roi)
                    self.known_ids.append(user_id)
        
        if len(self.known_faces) > 0:
            self.face_recognizer.train(self.known_faces, np.array(self.known_ids))
    
    def register_new_user(self, name, image_path):
        if not os.path.exists(image_path):
            raise FileNotFoundError("Image file not found")
            
        # Read and convert image to grayscale
        img = cv2.imread(image_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        if len(faces) == 0:
            raise ValueError("No face found in the image")
            
        # Add user to database
        user_id = self.db.add_user(name, image_path)
        
        # Update known faces
        (x, y, w, h) = faces[0]
        face_roi = gray[y:y+h, x:x+w]
        self.known_faces.append(face_roi)
        self.known_ids.append(user_id)
        
        # Retrain the recognizer
        if len(self.known_faces) > 0:
            self.face_recognizer.train(self.known_faces, np.array(self.known_ids))
        
        return user_id
    
    def process_frame(self, frame):
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        
        # Initialize list for recognized users
        recognized_users = []
        
        for (x, y, w, h) in faces:
            face_roi = gray[y:y+h, x:x+w]
            
            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            
            if len(self.known_faces) > 0:
                # Predict the face
                user_id, confidence = self.face_recognizer.predict(face_roi)
                
                # If confidence is less than 100, consider it a match
                if confidence < 100:
                    recognized_users.append(user_id)
                    
        return recognized_users
    
    def mark_attendance(self, user_id):
        self.db.mark_attendance(user_id)
