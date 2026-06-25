# v2.0.24 Audio Backend — Sound class API test
# Tests the Sound object returned by sound_load()

# Test 1: sound_load with missing file returns nil
var s = sound_load("nonexistent_file_123.wav")
assert s == nil, "sound_load of missing file should return nil"

# Test 2: sound_load of a real .wav file returns a Sound object
var real = sound_load("tests/v2_0_24/beep.wav")
if real == nil {
    print("skip: no beep.wav — run gen_beep.ipp first")
} else {
    # Test that the Sound object has play/stop/set_volume methods
    assert type(real.play) == "function", "Sound should have a play method"
    assert type(real.stop) == "function", "Sound should have a stop method"
    assert type(real.set_volume) == "function", "Sound should have a set_volume method"

    # Test play returns true/false (may be false on headless CI without audio device)
    var result = real.play()
    # Don't assert — headless runners have no audio device

    # Test stop does not crash
    real.stop()

    # Test set_volume
    real.set_volume(0.8)
    real.set_volume(1.0)

    # Test play with loops, volume, pan args
    real.play(loops=0, volume=0.5, pan=0.0)

    # Test play with keyword args only
    real.play(volume=0.3, pan=-0.5)

    real.stop()
}

# Test 3: stop_all_sounds does not crash
stop_all_sounds()
stop_all_sounds()  # calling again should be safe

# Test 4: set_volume global
set_volume(0.0)
assert set_volume(0.5) == 0.5, "set_volume should return the clamped value"
set_volume(1.0)

print("All v2.0.24 audio real tests passed")
