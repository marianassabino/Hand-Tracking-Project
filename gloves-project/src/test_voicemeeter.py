import voicemeeterlib

with voicemeeterlib.api('banana') as vm:
    print("✅ Connected to VoiceMeeter Banana!")
    print(f"VoiceMeeter version: {vm.version}")
    
    # Test controlling a parameter
    print(f"Strip 0 gain: {vm.strip[0].gain}")