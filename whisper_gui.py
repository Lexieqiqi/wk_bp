import requests
import tkinter as tk
from tkinter import filedialog, messagebox
import sounddevice as sd
import wave
import os

SERVER_URL = "http://172.16.108.68:5000/transcribe"  # 替换为你的服务端 URL
AUDIO_FILE_PATH = "C:\Users\lexie\Documents\录音\recorded_audio.wav"

def transcribe_audio(file_path, server_url):
    with open(file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(server_url, files=files)
    
    if response.status_code == 200:
        transcription = response.json().get('transcription', 'No transcription found')
        messagebox.showinfo("Transcription Result", transcription)
    else:
        messagebox.showerror("Error", f"Error: {response.status_code} {response.json()}")

def upload_file():
    file_path = filedialog.askopenfilename()
    if file_path:
        transcribe_audio(file_path, SERVER_URL)

def record_audio():
    def callback(indata, frames, time, status):
        audio_frames.append(indata.copy())

    def stop_recording():
        sd.stop()
        with wave.open(AUDIO_FILE_PATH, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(44100)
            wf.writeframes(b''.join(audio_frames))
        transcribe_audio(AUDIO_FILE_PATH, SERVER_URL)
        os.remove(AUDIO_FILE_PATH)

    audio_frames = []
    sd.InputStream(callback=callback).start()
    messagebox.showinfo("Recording", "Recording started. Click OK to stop.")
    stop_recording()

root = tk.Tk()
root.title("Audio Transcription Client")

upload_button = tk.Button(root, text="Upload Audio File", command=upload_file)
upload_button.pack(pady=10)

record_button = tk.Button(root, text="Record Audio", command=record_audio)
record_button.pack(pady=10)

root.mainloop()
