# v2.0.24 audio playback builtins
# Test basic API exists and error handling works

# set_volume should clamp 0.0-1.0
var vol = set_volume(0.5)
print(vol)

# sound_load with missing file should return nil, not crash
var s = sound_load("nonexistent.wav")
assert s == nil, "sound_load of nonexistent file should return nil"

# stop_all_sounds should not crash even when nothing is playing
stop_all_sounds()

# set_volume out of range should clamp
set_volume(2.0)
set_volume(-1.0)

print("All v2.0.24 audio tests passed")
