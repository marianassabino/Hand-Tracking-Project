import numpy as np
import wave, struct, os

os.makedirs('sounds', exist_ok=True)

def make_note(filename, freq, duration=0.5, volume=0.5):
    sample_rate = 44100
    samples = int(sample_rate * duration)
    with wave.open(filename, 'w') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        for i in range(samples):
            t = i / sample_rate
            fade = min(1.0, (samples - i) / (sample_rate * 0.1))
            val = int(volume * fade * 32767 * np.sin(2 * np.pi * freq * t))
            f.writeframes(struct.pack('<h', val))

make_note('sounds/thumb.wav',  261.63)
make_note('sounds/index.wav',  329.63)
make_note('sounds/middle.wav', 392.00)
make_note('sounds/ring.wav',   440.00)
make_note('sounds/pinky.wav',  523.25)

print('Sound files created!')