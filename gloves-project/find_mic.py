import sounddevice as sd

print("Available devices:")
print(sd.query_devices())
print("\nDefault input:", sd.query_devices(kind='input'))
print("\nDefault output:", sd.query_devices(kind='output'))