import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wavfile
 
SAMPLE_RATE = 16000
DURATION    = 5
OUTPUT_FILE = "recording.wav"
 
def record(duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Record audio from the default microphone.
 
    Returns a 1D float32 NumPy array (a Python data structure that efficiently stores and processes lists of numbers) of audio samples.
    """
    print(f"Recording for {duration} seconds... (speak now)")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("Done recording.")
    return audio.squeeze()
 
 
def save_wav(audio: np.ndarray, path: str, sample_rate: int = SAMPLE_RATE) -> None:
    """Save a float32 audio array to a WAV file."""
    # WAV files use int16; scale float32 [-1.0, 1.0] to int16 range
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(path, sample_rate, audio_int16)
    print(f"Saved to {path}")
 
 
if __name__ == "__main__":
    audio = record(DURATION)
    save_wav(audio, OUTPUT_FILE)