import sounddevice as sd
import numpy as np
import queue

RATE = 48000
CHUNK = 1024
q = queue.Queue()

def input_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(indata.copy())

def output_callback(outdata, frames, time, status):
    if status:
        print(status)
    try:
        outdata[:] = q.get_nowait()
    except queue.Empty:
        outdata[:] = 0

print("🎤 Speak into your mic... (press Ctrl+C to stop)")

try:
    with sd.InputStream(samplerate=RATE, blocksize=CHUNK,
                        device=26, channels=2,
                        dtype='int16', callback=input_callback):
        with sd.OutputStream(samplerate=RATE, blocksize=CHUNK,
                             device=27, channels=2,
                             dtype='int16', callback=output_callback):
            print("✅ Stream open! Speak now...")
            while True:
                sd.sleep(100)
except KeyboardInterrupt:
    print("Stopped!")
except Exception as e:
    print(f"Error: {e}")