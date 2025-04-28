import whisper
import tempfile

model = whisper.load_model("base")  # or "small", "medium", etc.

def transcribe_audio(audio_input):
    # If a string path is passed
    if isinstance(audio_input, str):
        return model.transcribe(audio_input)['text']
    
    # If it's a file-like object (like an uploaded file in Streamlit)
    else:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_input.read())
            temp_path = f.name
        return model.transcribe(temp_path)['text']
