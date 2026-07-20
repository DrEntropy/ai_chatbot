"""voice_input.py — Record audio from the microphone and transcribe with MLX Whisper.
 
Usage as a script:
    python voice_input.py --duration 5 --model mlx-community/whisper-small-mlx
 
Usage as a module:
    from voice_input import record_and_transcribe
    text = record_and_transcribe(duration=5)
"""
 
import argparse
import os
import tempfile
 
import numpy as np
import scipy.io.wavfile as wavfile
import sounddevice as sd
import mlx_whisper
 
SAMPLE_RATE    = 16000
DEFAULT_MODEL  = "mlx-community/whisper-medium-mlx"
DEFAULT_DURATION = 5
 
 
def record(duration: float, sample_rate: int = SAMPLE_RATE) -> np.ndarray:
    """Record `duration` seconds of mono audio from the default microphone.
 
    Returns a 1D float32 NumPy array.
    """
    print(f"🎤 Recording for {duration} second(s)... speak now")
    audio = sd.rec(
        int(duration * sample_rate),
        samplerate=sample_rate,
        channels=1,
        dtype="float32",
    )
    sd.wait()
    print("⏹  Recording complete.")
    return audio.squeeze()
 
 
def transcribe_array(
    audio: np.ndarray,
    model: str = DEFAULT_MODEL,
    sample_rate: int = SAMPLE_RATE,
) -> str:
    """Transcribe a float32 NumPy audio array.
 
    Writes a temporary WAV file (required by mlx_whisper), runs transcription,
    then deletes the temp file.
    """
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        tmp_path = f.name
        wavfile.write(tmp_path, sample_rate, (audio * 32767).astype(np.int16))
    try:
        result = mlx_whisper.transcribe(tmp_path, path_or_hf_repo=model)
        return result["text"].strip()
    finally:
        os.unlink(tmp_path)
 
 
def transcribe_file(path: str, model: str = DEFAULT_MODEL) -> str:
    """Transcribe an existing WAV file."""
    result = mlx_whisper.transcribe(path, path_or_hf_repo=model)
    return result["text"].strip()
 
 
def record_and_transcribe(
    duration: float = DEFAULT_DURATION,
    model: str = DEFAULT_MODEL,
) -> str:
    """Record from the microphone and return the transcript."""
    audio = record(duration)
    print("🔍 Transcribing...")
    text = transcribe_array(audio, model)
    return text
 
 
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record and transcribe speech.")
    parser.add_argument("--duration", type=float, default=DEFAULT_DURATION,
                        help="Recording duration in seconds (default: 5)")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help="MLX Whisper model to use")
    args = parser.parse_args()
 
    transcript = record_and_transcribe(args.duration, args.model)
    print(f"\n📝 Transcript:\n{transcript}\n")