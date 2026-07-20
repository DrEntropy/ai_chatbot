import mlx_whisper
 
AUDIO_FILE    = "recording.wav"
WHISPER_MODEL = "mlx-community/whisper-medium-mlx"
 
def transcribe(audio_path: str, model: str = WHISPER_MODEL) -> str:
    """Transcribe an audio file and return the text."""
    print(f"Transcribing with {model.split('/')[-1]}...")
    result = mlx_whisper.transcribe(audio_path, path_or_hf_repo=model)
    return result["text"].strip()
 
 
if __name__ == "__main__":
    text = transcribe(AUDIO_FILE)
    print(f"\nTranscript:\n{text}")