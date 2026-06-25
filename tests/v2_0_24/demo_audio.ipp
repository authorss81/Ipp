# v2.0.24 Audio Demo
# Demonstrates the sound_load / Sound class API

# Set default volume
set_volume(0.8)

# Load a sound
var sfx = sound_load("tests/v2_0_24/beep.wav")

if sfx == nil {
    print("No audio file found — create tests/v2_0_24/beep.wav to hear the demo")
    print("Demo requires a WAV file at tests/v2_0_24/beep.wav")
} else {
    print("Loaded sound object:", sfx)
    print("Playing sound at full volume...")
    sfx.play(volume=1.0)
    sleep(0.5)

    print("Playing with left pan...")
    sfx.play(pan=-0.8)
    sleep(0.5)

    print("Playing with right pan...")
    sfx.play(pan=0.8)
    sleep(0.5)

    print("Playing 3 times (loops=2)...")
    sfx.play(loops=2, volume=0.5)
    sleep(1.5)

    print("Stopping all sounds...")
    stop_all_sounds()

    print("Done!")
}
