# 🎧 Mood-Based Music Player with Emotion Detection

This is a Python-based GUI application that plays music based on the user's facial expression detected through the webcam. The app uses emotion detection (happy, sad, stressed) to suggest songs accordingly from YouTube. It also supports multilingual preferences and remembers user mood history.

---

## 💡 Features

- 🧠 **AI Emotion Detection** using webcam and FER (Facial Expression Recognition)
- 🎶 **Mood-Based Music Playback** via YouTube (happy, sad, stressed)
- 🧑‍💻 **User Login/Signup** with password hashing
- 🕵️‍♂️ **Personalized Recommendations** based on preferred artist & language
- 📊 **Mood History Chart** with matplotlib
- 🌐 **Multilingual Support** (English, Hindi, Punjabi)
- 🔐 Passwords securely stored using `bcrypt`
- 📁 History saved in local JSON file

---



## 🚀 Getting Started

### ✅ Requirements

- Python 3.8+
- Webcam (for emotion detection)

### 📦 Install Dependencies

```bash
pip install opencv-python-headless fer matplotlib pillow bcrypt ttkbootstrap vlc yt-dlp
