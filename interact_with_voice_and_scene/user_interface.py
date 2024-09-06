import tkinter as tk
from tkinter import filedialog
import pyaudio
import wave
import requests
import json
import base64
import threading
import numpy as np

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio and Image Uploader")

        # Label for instruction
        self.label = tk.Label(root, text="Select an image, record audio, and upload.")
        self.label.pack(pady=10)

        # Button to select image
        self.select_image_button = tk.Button(root, text="Select Image", command=self.select_image)
        self.select_image_button.pack(pady=10)

        # Label to show selected image path
        self.image_label = tk.Label(root, text="")
        self.image_label.pack(pady=10)

        # Button to start recording
        self.record_button = tk.Button(root, text="Record Audio", command=self.record_audio, state=tk.DISABLED)
        self.record_button.pack(pady=10)

        # Button to stop recording
        self.stop_button = tk.Button(root, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        # Button to upload audio and image
        self.upload_button = tk.Button(root, text="Upload", command=self.upload, state=tk.DISABLED)
        self.upload_button.pack(pady=10)

        self.image_path = None
        self.audio_path = r"C:\Users\lexie\Documents\录音\recording.wav"
        self.is_recording = False

    def select_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
        if self.image_path:
            self.image_label.config(text=self.image_path)
            self.record_button.config(state=tk.NORMAL)

    def record_audio(self):
        self.is_recording = True
        self.record_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)

        # Start a new thread to record audio
        threading.Thread(target=self._record_audio).start()

    def _record_audio(self):
        chunk = 1024  # Record in chunks of 1024 samples
        sample_format = pyaudio.paInt16  # 16 bits per sample
        channels = 1
        fs = 44100  # Record at 44100 samples per second
        p = pyaudio.PyAudio()  # Create an interface to PortAudio

        print("Recording...")

        stream = p.open(format=sample_format, channels=channels, rate=fs, frames_per_buffer=chunk, input=True)
        frames = []

        while self.is_recording:
            data = stream.read(chunk)
            frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

        print("Recording stopped.")

        wf = wave.open(self.audio_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(sample_format))
        wf.setframerate(fs)
        wf.writeframes(b''.join(frames))
        wf.close()

        self.stop_button.config(state=tk.DISABLED)
        self.upload_button.config(state=tk.NORMAL)

    def stop_recording(self):
        self.is_recording = False

    def upload(self):
        # Upload audio to Whisper server for transcription
        files = {'audio': open(self.audio_path, 'rb')}
        response = requests.post(f"http://172.16.108.68:5001/transcribe", files=files)

        if response.status_code == 200:
            transcription = response.json().get("transcription", 'No transcription found')
            print(f"Transcription: {transcription}")

            if self.image_path:
                self.send_to_vlm(transcription)
        else:
            print("Failed to upload audio.")

    def send_to_vlm(self, transcription):
        with open(self.image_path, "rb") as img_file:
            encoded_image = base64.b64encode(img_file.read()).decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": transcription,
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{encoded_image}"
                        },
                    },
                ],
            },
        ]

        data = {
            "model": "cogvlm-chat-17b",
            "messages": messages,
            "stream": False,
            "max_tokens": 2048,
            "temperature": 0.8,
            "top_p": 0.8,
        }

        response = requests.post(f"http://172.16.108.67:8000/v1/chat/completions", json=data)

        if response.status_code == 200:
            result = response.json().get("choices", [{}])[0].get("message", "").get("content", "")
            print(f"VLM Response: {result}")
            self.synthesize_and_play(result)  # 使用语音合成服务生成音频并播放
        else:
            print("Failed to send data to VLM.")

    def synthesize_and_play(self, text):
        # 使用TTS服务生成音频
        tts_data = {"text": text}
        tts_response = requests.post("http://172.16.108.68:5000/synthesize", json=tts_data)

        if tts_response.status_code == 200:
            # 保存音频内容到文件
            audio_data = np.frombuffer(tts_response.content, dtype=np.float32)
            audio_data = (audio_data * 32767).astype(np.int16)  # 转换为int16格式
            output_path = "output-01.wav"
            with wave.open(output_path, 'wb') as wf:
                wf.setnchannels(1)  # 设置通道数，通常为1（单声道）或2（立体声）
                wf.setsampwidth(2)  # 2字节，16位
                wf.setframerate(24000)  # 设置采样率为24000Hz
                wf.writeframes(audio_data.tobytes())

            # 播放生成的音频
            chunk = 1024
            wf = wave.open(output_path, 'rb')
            p = pyaudio.PyAudio()
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)

            data = wf.readframes(chunk)

            while data:
                stream.write(data)
                data = wf.readframes(chunk)

            stream.stop_stream()
            stream.close()
            p.terminate()
        else:
            print("Failed to generate or retrieve TTS audio.")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
