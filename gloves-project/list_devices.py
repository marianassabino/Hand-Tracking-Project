import pyaudio

p = pyaudio.PyAudio()

print("Available audio devices:\n")
for i in range(p.get_device_count()):
    dev = p.get_device_info_by_index(i)
    print(f"[{i}] {dev['name']}")
    print(f"     Input channels: {dev['maxInputChannels']}")
    print(f"     Output channels: {dev['maxOutputChannels']}")
    print()

p.terminate()