import voicemeeterlib
import time

with voicemeeterlib.api('banana') as vm:
    print("Testing VoiceMeeter control...")
    
    # Mute strip 0 (your mic)
    print("Muting mic...")
    vm.strip[0].mute = True
    time.sleep(2)
    
    # Unmute
    #print("Unmuting mic...")
   # vm.strip[0].mute = False
    #time.sleep(1)
    
    # Change gain
    ###time.sleep(2)
    
    # Reset gain
    # print("✅ All controls working!")
    #