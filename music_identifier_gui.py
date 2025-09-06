
import tkinter as tk
from tkinter import messagebox
import threading
import pyaudio
import wave
import requests

API_TOKEN = "2b49aa6c08ce9d83213ca3ea77b21a37"
RECORD_SECONDS = 7
WAV_OUTPUT_FILENAME = "recorded_audio.wav"

def record_audio(callback):
    FORMAT = pyaudio.paInt16
    CHANNELS = 2
    RATE = 44100
    CHUNK = 1024

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    frames = []

    for _ in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    stream.stop_stream()
    stream.close()
    audio.terminate()

    with wave.open(WAV_OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    callback(WAV_OUTPUT_FILENAME)

def identify_music(filename):
    with open(filename, 'rb') as f:
        response = requests.post("https://api.audd.io/",
            data={
                'api_token': API_TOKEN,
                'return': 'timecode,apple_music,spotify',
            },
            files={'audio': f}
        )
    return response.json()

def on_record_finished(filename):
    result = identify_music(filename)

    if result['status'] == 'success' and result['result']:
        song = result['result']
        artist = song.get('artist', 'N/A')
        title = song.get('title', 'N/A')
        bpm = song.get('song', {}).get('bpm', 'N/A')
        key = song.get('song', {}).get('key', 'N/A')
        youtube = song.get('song_link', 'N/A')
        result_text.set(f"🎵 {artist} - {title}\n🔑 Key: {key}\n⚡ BPM: {bpm}\n🔗 YouTube: {youtube}")
    else:
        result_text.set("❌ Pa jwenn mizik.")

    button.config(state=tk.NORMAL)

def start_process():
    button.config(state=tk.DISABLED)
    result_text.set("🎙️ Rekò ap fèt...")
    threading.Thread(target=record_audio, args=(on_record_finished,), daemon=True).start()

# GUI setup
root = tk.Tk()
root.title("Music Identifier Desktop")

tk.Label(root, text="🎧 Rekonèt mizik ki ap jwe sou laptop ou", font=('Arial', 14)).pack(pady=10)

button = tk.Button(root, text="🎤 Rekòde & Idantifye", font=('Arial', 12), command=start_process)
button.pack(pady=10)

result_text = tk.StringVar()
tk.Label(root, textvariable=result_text, font=('Arial', 11), justify="left", wraplength=400).pack(pady=10)

root.geometry("500x300")
root.mainloop()
