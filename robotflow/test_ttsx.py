import pyttsx3

engine = pyttsx3.init()

# 获取当前所有可用的语音引擎属性
voices = engine.getProperty('voices')
for index, voice in enumerate(voices):
    print(f"Voice {index}: {voice.name}")

# 选择一个不同的语音引擎
engine.setProperty('voice', voices[0].id)  # 选择第一个语音引擎，或者更换为其他的 index

engine.say("Testing voice output.")
engine.runAndWait()

engine.setProperty('volume', 1.0)  # 范围是0.0到1.0，1.0为最大音量
