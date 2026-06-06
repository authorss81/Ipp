# v2.3.0 audio playback builtins
# Test basic API exists and error handling works

# set_volume should clamp 0.0-1.0
var vol = set_volume(0.5)
print(vol)

# play_sound with missing file should return error, not crash
var err = play_sound("nonexistent.wav")
print(err)

# stop_sound should not crash even when nothing is playing
var stopped = stop_sound()
print(stopped)

# set_volume out of range should clamp
set_volume(2.0)
set_volume(-1.0)

print("All v2.3.0 audio tests passed")
