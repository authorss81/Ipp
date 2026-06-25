# Generate a 440Hz sine wave WAV file using pure Ipp
# Uses write_bytes to write raw PCM data

var sample_rate = 22050
var duration = 0.5
var freq = 440.0
var amplitude = 16000
var num_samples = sample_rate * duration

# Build the WAV header and sample data as a string of raw bytes
var buf = ""

# RIFF header
buf += "RIFF"
buf += from_ascii(0)  # placeholder for file_len (will patch)
buf += from_ascii(0)
buf += from_ascii(0)
buf += from_ascii(0)
buf += "WAVE"

# fmt chunk
buf += "fmt "
buf += from_ascii(16) + from_ascii(0) + from_ascii(0) + from_ascii(0)  # chunk size = 16
buf += from_ascii(1) + from_ascii(0)    # PCM = 1
buf += from_ascii(1) + from_ascii(0)    # mono = 1
# sample rate
buf += from_ascii(sample_rate % 256) + from_ascii(sample_rate >> 8 % 256) + from_ascii(0) + from_ascii(0)
# byte rate = sample_rate * 2
var byte_rate = sample_rate * 2
buf += from_ascii(byte_rate % 256) + from_ascii(byte_rate >> 8 % 256) + from_ascii(0) + from_ascii(0)
# block align = 2
buf += from_ascii(2) + from_ascii(0)
# bits per sample = 16
buf += from_ascii(16) + from_ascii(0)

# "data" chunk header (placeholder)
var data_pos = len(buf) + 4  # skip "data" + 4-byte size
buf += "data"
buf += from_ascii(0) + from_ascii(0) + from_ascii(0) + from_ascii(0)

# Generate samples
var i = 0
while i < num_samples {
    var t = i / sample_rate
    # Envelope: fade in/out over first/last 200 samples
    var env = 1.0
    if i < 200 { env = i / 200 }
    if num_samples - i < 200 { env = (num_samples - i) / 200 }
    var val = amplitude * env * sin(2 * pi * freq * t)
    var ival = int(val)
    # Little-endian 16-bit signed
    if ival < 0 { ival = ival + 65536 }
    buf += from_ascii(ival % 256)
    buf += from_ascii(ival >> 8 % 256)
    i = i + 1
}

# Patch sizes
var data_size = len(buf) - data_pos
var file_size = len(buf) - 8

# patch file_size at bytes 4-7
var tmp = ""
tmp += substring(buf, 0, 4)
tmp += from_ascii(file_size % 256)
tmp += from_ascii(file_size >> 8 % 256)
tmp += from_ascii(file_size >> 16 % 256)
tmp += from_ascii(file_size >> 24 % 256)
tmp += substring(buf, 8, data_pos - 8)

# patch data_size at data_pos - 4 to data_pos
tmp += from_ascii(data_size % 256)
tmp += from_ascii(data_size >> 8 % 256)
tmp += from_ascii(data_size >> 16 % 256)
tmp += from_ascii(data_size >> 24 % 256)

# rest of data
tmp += substring(buf, data_pos)

buf = tmp

# Write it
write_bytes("tests/v2_0_24/beep.ipp.wav", buf)

print("Generated tests/v2_0_24/beep.ipp.wav")
print("  samples:", num_samples)
print("  file size:", len(buf))
