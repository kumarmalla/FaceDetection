import tkinter as tk
from tkinter import Label, Button, Frame, filedialog
import cv2
from PIL import Image, ImageTk
import mediapipe as mp
import numpy as np

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def create_preview_frame():
    for widget in root.winfo_children():
        if isinstance(widget, Frame) and widget != button_frame:
            widget.pack_forget()
    button_frame.pack_forget()
    
    preview_frame = Frame(root, bg="#22303C")
    preview_frame.pack(pady=10)
    preview_label = Label(preview_frame)
    preview_label.pack()
    return preview_frame, preview_label

def create_inner_buttons(preview_frame, buttons):
    button_frame_inner = Frame(preview_frame, bg="#22303C")
    button_frame_inner.pack(pady=10)
    button_refs = {}
    for text, command in buttons:
        button = Button(button_frame_inner, text=text, command=command, **btn_style)
        button.pack(side="left", padx=10, pady=5)
        button_refs[text] = button
    return button_refs

def detect_faces(frame):
    with mp_face_detection.FaceDetection(min_detection_confidence=0.5) as face_detection:
        results = face_detection.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        if results.detections:
            for detection in results.detections:
                mp_drawing.draw_detection(frame, detection)
    return frame

def update_preview_label(preview_label, frame):
    frame = cv2.resize(frame, (960, 540))
    frame = detect_faces(frame)
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame)
    imgtk = ImageTk.PhotoImage(image=img)
    preview_label.imgtk = imgtk
    preview_label.configure(image=imgtk)

def handle_video_capture(preview_label, cap, is_paused, capturing):
    def show_frame():
        if capturing and not is_paused[0]:
            ret, frame = cap.read()
            if ret:
                update_preview_label(preview_label, frame)
        preview_label.after(10, show_frame)
    show_frame()

def reset_window(preview_frame, cap, capturing):
    if cap:
        cap.release()
    capturing = False
    preview_frame.pack_forget()
    button_frame.pack(pady=10)

def take_photo():
    preview_frame, preview_label = create_preview_frame()
    cap = cv2.VideoCapture(0)
    capturing = True

    handle_video_capture(preview_label, cap, is_paused=[False], capturing=capturing)

    def capture_image():
        nonlocal capturing
        capturing = False
        ret, frame = cap.read()
        if ret:
            update_preview_label(preview_label, frame)
        cap.release()
        button_refs["Capture Image"].config(text="Re-Capture", command=take_photo)

    button_refs = create_inner_buttons(preview_frame, [("Capture Image", capture_image), ("Reset", lambda: reset_window(preview_frame, cap, capturing))])

def stream_video():
    preview_frame, preview_label = create_preview_frame()
    cap = cv2.VideoCapture(0)
    is_paused = [False]

    handle_video_capture(preview_label, cap, is_paused=is_paused, capturing=True)

    def toggle_pause():
        is_paused[0] = not is_paused[0]
        button_refs["Pause"].config(text="Resume" if is_paused[0] else "Pause")

    button_refs = create_inner_buttons(preview_frame, [("Pause", toggle_pause), ("Reset", lambda: reset_window(preview_frame, cap, True))])

def upload_file():
    preview_frame, preview_label = create_preview_frame()

    def clear_inner_buttons():
        for widget in preview_frame.winfo_children():
            if isinstance(widget, Frame):
                widget.pack_forget()

    def show_image(file_path):
        img = Image.open(file_path)
        img = img.resize((960, 540), Image.LANCZOS)
        img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        img = detect_faces(img)
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        preview_label.imgtk = imgtk
        preview_label.configure(image=imgtk)

        def upload_new_file():
            clear_inner_buttons()
            file_path = filedialog.askopenfilename()
            if file_path:
                if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
                    show_image(file_path)
                elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
                    show_video(file_path)

        clear_inner_buttons()
        create_inner_buttons(preview_frame, [("Another File", upload_new_file), ("Reset", lambda: reset_window(preview_frame, None, False))])

    def show_video(file_path):
        cap = cv2.VideoCapture(file_path)
        is_paused = [False]

        def show_frame():
            if cap.isOpened() and not is_paused[0]:
                ret, frame = cap.read()
                if ret:
                    update_preview_label(preview_label, frame)
            preview_label.after(10, show_frame)
        
        show_frame()

        def toggle_pause():
            is_paused[0] = not is_paused[0]
            button_refs["Pause"].config(text="Resume" if is_paused[0] else "Pause")

        clear_inner_buttons()
        button_refs = create_inner_buttons(preview_frame, [("Pause", toggle_pause), ("Reset", lambda: reset_window(preview_frame, cap, True))])

    file_path = filedialog.askopenfilename()
    if file_path:
        if file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif')):
            show_image(file_path)
        elif file_path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            show_video(file_path)

root = tk.Tk()
root.title("Face Detection")
root.geometry("1250x750")
root.configure(bg="#22303C")

window_width = 1250
window_height = 750
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

heading_label = tk.Label(
    root, text="Face Detection", font=("Times New Roman", 20, "bold", "italic"), bg="#22303C", fg="#FFFFFF"
)
heading_label.pack(pady=10)

button_frame = tk.Frame(root, bg="#22303C")
button_frame.pack(pady=10)

btn_style = {"font": ("Roboto Mono Medium", 12), "bg": "#4285F4", "fg": "white", "relief": "raised", "width": 15}

take_photo_button = tk.Button(button_frame, text="Take Photo", command=take_photo, **btn_style)
stream_video_button = tk.Button(button_frame, text="Stream Video", command=stream_video, **btn_style)
upload_file_button = tk.Button(button_frame, text="Upload File", command=upload_file, **btn_style)

take_photo_button.grid(row=0, column=0, padx=10, pady=5)
stream_video_button.grid(row=0, column=1, padx=10, pady=5)
upload_file_button.grid(row=0, column=2, padx=10, pady=5)

footer_label = tk.Label(
    root, text="Designed by our Team", font=("Roboto Mono Medium", 10), bg="#22303C", fg="#8899A6"
)
footer_label.pack(side="bottom", pady=10)

root.mainloop()