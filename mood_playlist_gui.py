import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import ttkbootstrap as tb
from PIL import Image, ImageTk
import cv2
import json
import os
import bcrypt
import pythoncom
from fer import FER
import matplotlib.pyplot as plt
import vlc
from datetime import datetime
import yt_dlp

# Fix matplotlib backend
plt.switch_backend('TkAgg')

# COM fix for VLC
pythoncom.CoInitialize()

# Paths
USER_DB = "user_data/users.json"
HISTORY_FILE = "user_data/history.json"
os.makedirs("user_data", exist_ok=True)

# Emotion detection
emotion_detector = FER(mtcnn=True)

# ---------- Auth ------------
def load_users():
    return json.load(open(USER_DB)) if os.path.exists(USER_DB) else {}

def save_users(users):
    json.dump(users, open(USER_DB, 'w'), indent=2)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

# ---------- Music ------------
def get_youtube_audio_url(query):
    try:
        ydl_opts = {
            'format': 'bestaudio',
            'quiet': True,
            'no_warnings': True,
            'default_search': 'ytsearch1',
            'noplaylist': True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            return info.get('url'), info.get('title'), info.get('webpage_url')
    except Exception as e:
        print("YouTube/yt_dlp Error:", e)
        return None, None, None

def play_stream(url):
    try:
        instance = vlc.Instance()
        player = instance.media_player_new()
        media = instance.media_new(url)
        player.set_media(media)
        player.play()
        return player
    except Exception as e:
        print("[play_stream ERROR]:", e)
        return None

# ---------- Emotion ------------
def detect_emotion(frame):
    try:
        emotion, _ = emotion_detector.top_emotion(frame)
        if emotion == "happy":
            return "happy"
        elif emotion in ["sad", "disgust", "fear"]:
            return "sad"
        else:
            return "stressed"
    except:
        return "happy"

# ---------- GUI App ------------
class MoodMusicApp:
    def __init__(self, root, profile):
        self.root = root
        self.profile = profile
        self.cap = None
        self.running = False
        self.current_player = None
        self.current_emotion = None
        self.last_emotion = None

        self.setup_ui()

    def setup_ui(self):
        tb.Style("darkly")
        self.root.title("🎧 Mood Music App")
        self.root.geometry("800x650")
        self.root.configure(bg="#121212")

        tk.Label(self.root, text=f"Welcome {self.profile['name']} | Lang: {self.profile['language']} | Artist: {self.profile['favorite_artist']}",
                 fg="white", bg="#121212").pack(pady=5)
        self.video_label = tk.Label(self.root, bg="#121212")
        self.video_label.pack()

        self.mood_var = tk.StringVar(value="Detected Mood: None")
        tk.Label(self.root, textvariable=self.mood_var, fg="white", bg="#121212", font=("Helvetica", 14)).pack()

        self.song_var = tk.StringVar(value="Now Playing: -")
        tk.Label(self.root, textvariable=self.song_var, fg="white", bg="#121212").pack(pady=5)

        frame = tk.Frame(self.root, bg="#121212")
        frame.pack(pady=10)
        ttk.Button(frame, text="Start Camera", command=self.start_camera).grid(row=0, column=0, padx=10)
        ttk.Button(frame, text="Stop Camera", command=self.stop_camera).grid(row=0, column=1, padx=10)
        ttk.Button(frame, text="Play Music", command=self.play_music).grid(row=0, column=2, padx=10)
        ttk.Button(frame, text="Stop Music", command=self.stop_music).grid(row=0, column=3, padx=10)
        ttk.Button(frame, text="Show Mood Chart", command=self.show_chart).grid(row=0, column=4, padx=10)

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.running = True
        self.update_frame()

    def stop_camera(self):
        self.running = False
        if self.cap:
            self.cap.release()
        self.video_label.config(image='')

    def update_frame(self):
        if self.running:
            ret, frame = self.cap.read()
            if ret:
                mood = detect_emotion(frame)
                if mood != self.last_emotion:
                    self.last_emotion = mood
                    self.current_emotion = mood
                    self.mood_var.set(f"Detected Mood: {mood}")
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb)
                imgtk = ImageTk.PhotoImage(img.resize((640, 360)))
                self.video_label.imgtk = imgtk
                self.video_label.configure(image=imgtk)
            self.root.after(300, self.update_frame)

    def play_music(self):
        self.stop_music()
        mood = self.current_emotion or "happy"
        query = f"{self.profile['favorite_artist']} {self.profile['language']} {mood} song"
        url, title, page_url = get_youtube_audio_url(query)

        if not url:
            print("Fallback used")
            url = "https://rr4---sn-npoe7n7e.googlevideo.com/videoplayback?...(working direct stream url)..."
            title = "Fallback: Tera Yaar Hoon Main"
            page_url = "https://www.youtube.com/watch?v=R0aXYvQDWlY"

        self.song_var.set(f"Now Playing: {title}")
        self.current_player = play_stream(url)

        if self.current_player:
            self.log_history(page_url, query, mood)

    def stop_music(self):
        if self.current_player:
            self.current_player.stop()
            self.current_player = None
            self.song_var.set("Now Playing: -")

    def log_history(self, url, query, mood):
        entry = {
            "user": self.profile['name'],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "mood": mood,
            "query": query,
            "url": url
        }
        data = []
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                data = json.load(f)
        data.append(entry)
        with open(HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def show_chart(self):
        if not os.path.exists(HISTORY_FILE):
            return messagebox.showinfo("No Data", "No mood history found.")
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
        moods = [entry['mood'] for entry in data if entry['user'] == self.profile['name']]
        mood_count = {"happy": 0, "sad": 0, "stressed": 0}
        for m in moods:
            if m in mood_count:
                mood_count[m] += 1
        plt.bar(mood_count.keys(), mood_count.values(), color=["green", "blue", "orange"])
        plt.title("Mood History")
        plt.show()

# ---------- Auth GUI ------------
def authenticate():
    users = load_users()

    def try_login():
        u, p = user_entry.get(), pass_entry.get()
        if u in users and verify_password(p, users[u]['password']):
            win.destroy()
            open_app(users[u])
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")

    def try_signup():
        u, p = user_entry.get(), pass_entry.get()
        if u in users:
            messagebox.showerror("Signup Failed", "User already exists")
            return
        lang = simpledialog.askstring("Language", "Enter language (e.g. English/Hindi/Punjabi):")
        artist = simpledialog.askstring("Artist", "Enter your favorite artist:")
        users[u] = {
            "name": u,
            "password": hash_password(p),
            "language": lang,
            "favorite_artist": artist
        }
        save_users(users)
        win.destroy()
        open_app(users[u])

    win = tk.Tk()
    win.title("Login / Signup")
    win.geometry("300x250")
    win.configure(bg="#2d2d2d")

    tk.Label(win, text="Username", fg="white", bg="#2d2d2d").pack(pady=5)
    user_entry = tk.Entry(win)
    user_entry.pack()

    tk.Label(win, text="Password", fg="white", bg="#2d2d2d").pack(pady=5)
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()

    ttk.Button(win, text="Login", command=try_login).pack(pady=10)
    ttk.Button(win, text="Signup", command=try_signup).pack()
    win.mainloop()

def open_app(profile):
    root = tk.Tk()
    MoodMusicApp(root, profile)
    root.mainloop()

if __name__ == "__main__":
    authenticate()
