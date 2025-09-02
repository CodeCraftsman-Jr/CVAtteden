import cv2
import os
from face_recognition_system import FaceRecognitionSystem
from database_manager import DatabaseManager

def main():
    # Initialize the system
    face_system = FaceRecognitionSystem()
    db = DatabaseManager()
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
            
        # Process frame and get recognized users
        recognized_users = face_system.process_frame(frame)
        
        # Mark attendance for recognized users
        for user_id in recognized_users:
            user = db.get_user_by_id(user_id)
            if user:
                face_system.mark_attendance(user_id)
                name = user[1]  # Get user name
                cv2.putText(frame, f"Welcome {name}!", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # Display the frame
        cv2.imshow('Attendance System', frame)
        
        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

def register_new_user():
    face_system = FaceRecognitionSystem()
    db = DatabaseManager()
    
    print("\n=== User Registration ===")
    name = input("Enter user name: ")
    
    # Capture image for registration
    print("\nStarting camera for face capture...")
    print("Instructions:")
    print("1. Position your face in the center of the frame")
    print("2. Press SPACE to capture the image")
    print("3. Press Q to quit without capturing")
    
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break
        
        # Draw guide rectangle in the center
        height, width = frame.shape[:2]
        center_x = width // 2
        center_y = height // 2
        rect_width = 300
        rect_height = 400
        cv2.rectangle(frame,
                     (center_x - rect_width//2, center_y - rect_height//2),
                     (center_x + rect_width//2, center_y + rect_height//2),
                     (0, 255, 0), 2)
            
        cv2.imshow('Registration - Position face in green rectangle', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space key to capture
            # Save the image
            os.makedirs('images', exist_ok=True)
            image_path = os.path.abspath(f'images/{name.lower().replace(" ", "_")}.jpg')
            cv2.imwrite(image_path, frame)
            
            try:
                # Register the user
                user_id = face_system.register_new_user(name, image_path)
                print(f"\nSuccess! User {name} registered with ID {user_id}")
                print(f"Image saved as: {image_path}")
                
                # Display registered users
                print("\nCurrently registered users:")
                users = db.get_all_users()
                for user in users:
                    print(f"ID: {user[0]}, Name: {user[1]}")
                
            except Exception as e:
                print(f"\nError registering user: {str(e)}")
                if os.path.exists(image_path):
                    os.remove(image_path)
            break
        elif key == ord('q'):
            print("\nRegistration cancelled.")
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    while True:
        print("\n=== Attendance System Menu ===")
        print("1. Start Attendance System")
        print("2. Register New User")
        print("3. View All Users")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ")
        
        if choice == '1':
            main()
        elif choice == '2':
            register_new_user()
        elif choice == '3':
            db = DatabaseManager()
            users = db.get_all_users()
            print("\n=== Registered Users ===")
            if users:
                print("ID\tName\t\tRegistration Date")
                print("-" * 50)
                for user in users:
                    print(f"{user[0]}\t{user[1]}\t\t{user[3]}")
            else:
                print("No users registered yet.")
        elif choice == '4':
            print("\nThank you for using the Attendance System!")
            break
        else:
            print("Invalid choice. Please try again.")
