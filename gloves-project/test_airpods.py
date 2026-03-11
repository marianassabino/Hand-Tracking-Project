import sounddevice as sd
import numpy as np
import queue

RATE = 48000
CHUNK = 2048
q = queue.Queue()

# Auto-find AirPods
devices = sd.query_devices()
mic_id = None
out_id = None

for i, d in enumerate(devices):
    if 'AirPods' in d['name'] and d['max_input_channels'] > 0 and mic_id is None:
        mic_id = i
    if 'AirPods' in d['name'] and d['max_output_channels'] >= 2 and out_id is None:
        out_id = i

print(f"Found mic: [{mic_id}] {devices[mic_id]['name']}")
print(f"Found output: [{out_id}] {devices[out_id]['name']}")

# Get supported sample rate
info = sd.query_devices(mic_id)
rate = int(info['default_samplerate'])
print(f"Using sample rate: {rate}")

def callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    stereo = np.column_stack((indata[:,0], indata[:,0]))
    outdata[:] = stereo

try:
    with sd.Stream(samplerate=rate,
                   blocksize=CHUNK,
                   device=(mic_id, out_id),
                   channels=(1, 2),
                   dtype='int16',
                   callback=callback):
        print("✅ Stream open! Speak now... (Ctrl+C to stop)")
        while True:
            sd.sleep(100)
except KeyboardInterrupt:
    print("Stopped!")
except Exception as e:
    print(f"Error: {e}")