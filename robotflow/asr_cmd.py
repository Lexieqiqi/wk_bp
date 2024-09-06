import tkinter as tk
import pyaudio
import wave
import threading
import requests
import re
from pymycobot import ElephantRobot

# 录音参数
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
AUDIO_FILE = "command.wav"
WHISPER_SERVER_URL = 'http://172.16.108.68:5001/transcribe'

# 初始化机械臂客户端
elephant_client = ElephantRobot("192.168.10.173", 5001)
elephant_client.start_client()

class AudioRecorder:
    def __init__(self, output_file):
        self.output_file = output_file
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False

        # 自动选择有效的音频输入设备
        self.device_index = self.get_input_device_index()

    def get_input_device_index(self):
        """获取有效的音频输入设备索引"""
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                print(f"Using Device {i}: {device_info['name']}")
                return i
        raise ValueError("No valid input device found")
    
    def start_recording(self):
        self.stream = self.audio.open(format=FORMAT, channels=CHANNELS,
                                      rate=RATE, input=True,
                                      input_device_index=self.device_index,
                                      frames_per_buffer=CHUNK)
        self.frames = []
        self.is_recording = True
        threading.Thread(target=self.record).start()

    def record(self):
        while self.is_recording:
            try:
                data = self.stream.read(CHUNK)
                self.frames.append(data)
            except IOError as e:
                print(f"Recording Error: {e}")
                self.is_recording = False

    def stop_recording(self):
        self.is_recording = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()

        with wave.open(self.output_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(self.frames))

def transcribe_audio(file_path, server_url):
    """
    调用Whisper服务，将音频文件转录为文本
    """
    with open(file_path, 'rb') as audio_file:
        files = {'audio': audio_file}
        response = requests.post(server_url, files=files)
    
    if response.status_code == 200:
        transcription = response.json().get('transcription', 'No transcription found')
        return transcription
    else:
        print("Error:", response.status_code, response.json())
        return None
    
def chinese_to_number(chinese_str):
    chinese_digits = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    if chinese_str in chinese_digits:
        return chinese_digits[chinese_str]
    elif '十' in chinese_str:
        parts = chinese_str.split('十')
        if len(parts) == 2:
            return chinese_digits[parts[0]] * 10 + chinese_digits[parts[1]]
        else:
            return chinese_digits['十'] if parts[0] == '' else chinese_digits[parts[0]] * 10
    else:
        return None

def parse_voice_command(command):
    # """
    # 解析语音指令，提取运动方向和距离
    # """
    # direction_pattern = r'(?:向|往)([上|下|前|后|後|左|右|X轴向外|X轴向内|Y轴向外|Y轴向内|Z轴向外|Z轴向内])方向'
    # distance_pattern = r'(?:移动|移動|移动|移動)([\d一二三四五六七八九十]+)(?:毫米|mm|厘米|cm)?'
    # joint_pattern = r'(?:G|這|J|關節)([\d一二三四五六七八九十]+)(?:旋轉|增加|減小|轉動)?(?:\s*|)([\d一二三四五六七八九十]+)度'
    """
    解析语音指令，提取运动方向和距离
    """
    direction_pattern = r'(?:向|往)([上|下|前|後|左|右|X|Y|Z|X轴向外|X轴向内|Y轴向外|Y轴向内|Z轴向外|Z轴向内])'
    distance_pattern = r'(?:移动|移動|移动|移動|移動|前進|前进|后退|後退|左右|上下|上移|下移)?(\d+|[\d一二三四五六七八九十]+)(?:毫米|mm|厘米|cm)?'
    joint_pattern = r'(?:J|這|这|G|关节|關節)?(\d+|[\d一二三四五六]+)'
    angle_pattern = r'(?:旋轉|旋转|增加|減小|转动|转動|移动|移動)?(\d+|[\d一二三四五六七八九十百千万]+)(?:度|°)'


    direction_match = re.search(direction_pattern, command)
    distance_match = re.search(distance_pattern, command)
    joint_match = re.search(joint_pattern, command)
    angle_match = re.search(angle_pattern, command)
    
    def parse_number(number_str):
        """将中文数字和阿拉伯数字转换为阿拉伯数字"""
        if number_str.isdigit():
            return int(number_str)
        else:
            return chinese_to_number(number_str)

    if direction_match:
        direction = direction_match.group(1)
        if direction in ['前', 'X', 'X轴向外', '外', '上', '左']:
            sign = 1  # 正方向
        elif direction in ['后', '後', 'X轴向内', '内', '下', '右']:
            sign = -1  # 负方向

        if direction in ['前', '后', '後', 'X轴向外', 'X轴向内', '外', '内']:
            direction = 'X'
        elif direction in ['左', '右', 'Y轴向外', 'Y轴向内']:
            direction = 'Y'
        elif direction in ['上', '下', 'Z轴向外', 'Z轴向内']:
            direction = 'Z'
    
    if direction_match and distance_match:
        distance_str = distance_match.group(1)
        distance = parse_number(distance_str) * sign
        if distance is not None:
            return {"type": "move", "direction": direction, "distance": distance}
    
    elif joint_match and angle_match:
        joint_str = joint_match.group(1)
        angle_str = angle_match.group(1)
        joint = parse_number(joint_str)
        angle = parse_number(angle_str)
        if joint is not None and angle is not None:
            return {"type": "joint", "joint": joint, "angle": angle}
    
    return None

def execute_robot_command(command_info):
    """
    根据解析结果执行对应的机械臂控制指令
    """
    print(command_info)
    if command_info["type"] == "move":
        direction = command_info["direction"]
        distance = command_info["distance"]
        elephant_client.jog_relative(direction, distance, 2000, 1)
    
    elif command_info["type"] == "joint":
        joint = command_info["joint"]
        angle = command_info["angle"]
        elephant_client.jog_relative(f"J{joint}", angle, 2000, 0)
    
    # 等待机器人运动到目标位置再执行后续指令
    elephant_client.command_wait_done()

def start_recording():
    recorder.start_recording()
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)

def stop_recording():
    recorder.stop_recording()
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)

    # 录音结束后，调用Whisper服务进行语音转录
    transcription = transcribe_audio(AUDIO_FILE, WHISPER_SERVER_URL)

    if transcription:
        print("Transcription:", transcription)
        
        # 解析转录文本
        command_info = parse_voice_command(transcription)

        if command_info:
            # 执行机械臂指令
            execute_robot_command(command_info)
        else:
            print("无法解析的指令:", transcription)
    else:
        print("转录失败，无法执行操作。")

# 创建主窗口
root = tk.Tk()
root.title("音频录制")

# 初始化录音器
recorder = AudioRecorder(AUDIO_FILE)

# 创建按钮
start_button = tk.Button(root, text="开始录制", command=start_recording)
start_button.pack(pady=20)

stop_button = tk.Button(root, text="结束录制", command=stop_recording, state=tk.DISABLED)
stop_button.pack(pady=20)

# 运行主循环
root.mainloop()
